import { View, Text, Pressable, Alert } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { s, Header, Card, Status, Button, Section, Gauge, Toggle, Loading, Empty } from "@/ui";
import { useDevice, useDeleteDevice, useRotateDeviceCredentials } from "@/api/devices";
import { useProject } from "@/api/projects";
import { useDeviceDatastreams, useLatestValue, useCreateValue, type Datastream } from "@/api/datastreams";
import { useMe } from "@/api/auth";

function DatastreamRow({ x, deviceOnline, canControl, onPress }: { x: Datastream; deviceOnline: boolean; canControl: boolean; onPress: () => void }) {
  const latestQuery = useLatestValue(x.id);
  const createValue = useCreateValue();
  const value = latestQuery.data?.value;
  const isSensor = x.data_type !== "boolean";
  return (
    <Pressable onPress={onPress}>
      <Card style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <View><Text style={s.h2}>{x.name}</Text><Text style={s.muted}>{x.key}</Text></View>
        {isSensor ? (
          <Gauge value={typeof value === "number" ? value : 0} min={x.min_value ?? 0} max={x.max_value ?? 100} unit={x.unit ?? ""} />
        ) : (
          <Toggle label={x.name} value={!!value} disabled={!deviceOnline || !canControl || createValue.isPending} onValueChange={(v) => createValue.mutate({ datastream_id: x.id, value: v })} />
        )}
      </Card>
    </Pressable>
  );
}

export default function Device() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const r = useRouter();
  const deviceQuery = useDevice(id);
  const projectQuery = useProject(deviceQuery.data?.project_id);
  const meQuery = useMe(true, true);
  const datastreamsQuery = useDeviceDatastreams(id);
  const deleteMutation = useDeleteDevice();
  const rotateMutation = useRotateDeviceCredentials();
  if (deviceQuery.isLoading) return <View style={s.safe}><View style={s.content}><Header title="Dispositivo" /><Loading /></View></View>;
  const d = deviceQuery.data;
  if (!d) return <View style={s.safe}><View style={s.content}><Header title="Dispositivo" /><Text>Não encontrado.</Text></View></View>;
  const online = d.status === "online";
  const canManage = projectQuery.data?.owner_id === meQuery.data?.id;
  const ds = datastreamsQuery.data ?? [];
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title={d.name} subtitle={d.model || undefined} right={<Status online={online} />} />
        <Card>
          <Text style={s.muted}>Serial</Text>
          <Text style={s.h2}>{d.serial || "—"}</Text>
          <Text style={s.muted}>Firmware {d.firmware_version || "—"} · projeto {projectQuery.data?.name}</Text>
          <Text style={s.muted}>Última comunicação: {d.last_seen ? new Date(d.last_seen).toLocaleString("pt-PT") : "nunca"}</Text>
        </Card>
        <Section title="Datastreams" right={canManage ? <Button variant="soft" onPress={() => r.push({ pathname: "/datastreams/novo", params: { deviceId: d.id } })}>+ Novo</Button> : undefined} />
        {!datastreamsQuery.isLoading && !ds.length && <Empty icon="pulse-outline" title="Sem datastreams" text="Um datastream é um canal de dados do dispositivo (um sensor ou um atuador)." />}
        {ds.map((x) => <DatastreamRow key={x.id} x={x} deviceOnline={online} canControl={canManage} onPress={() => r.push(`/datastreams/${x.id}`)} />)}
        {canManage ? <>
        <Button variant="outline" disabled={rotateMutation.isPending} onPress={() => Alert.alert(
          "Rodar credenciais MQTT?",
          "As credenciais atuais deixam de funcionar imediatamente. O dispositivo precisa de ser reprovisionado.",
          [
            { text: "Cancelar", style: "cancel" },
            { text: "Rodar", style: "destructive", onPress: () => rotateMutation.mutate(d.id, { onSuccess: () => r.push(`/provisionamento/${d.id}`) }) },
          ],
        )}>{rotateMutation.isPending ? "A gerar credenciais…" : "Rodar credenciais MQTT"}</Button>
        <Button variant="danger" onPress={() => deleteMutation.mutate(d.id, { onSuccess: () => r.back() })} disabled={deleteMutation.isPending}>{deleteMutation.isPending ? "A eliminar…" : "Eliminar dispositivo"}</Button>
        </> : null}
      </View>
    </View>
  );
}
