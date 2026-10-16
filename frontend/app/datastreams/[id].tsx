import { View, Text } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { s, Header, Card, Button, Sparkline, Gauge, Toggle, Loading } from "@/ui";
import { useDatastream, useLatestValue, useValueHistory, useCreateValue, useDeleteDatastream } from "@/api/datastreams";
import { useDevice } from "@/api/devices";
export default function Datastream() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const r = useRouter();
  const dsQuery = useDatastream(id);
  const deviceQuery = useDevice(dsQuery.data?.device_id);
  const latestQuery = useLatestValue(id);
  const historyQuery = useValueHistory(id);
  const createValue = useCreateValue();
  const deleteMutation = useDeleteDatastream();
  if (dsQuery.isLoading) return <View style={s.safe}><View style={s.content}><Header title="Datastream" /><Loading /></View></View>;
  const x = dsQuery.data;
  if (!x) return <View style={s.safe}><View style={s.content}><Header title="Datastream" /><Text>Não encontrado.</Text></View></View>;
  const value = latestQuery.data?.value;
  const history = (historyQuery.data ?? []).map((v) => (typeof v.value === "number" ? v.value : 0)).reverse();
  const isSensor = x.data_type !== "boolean";
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title={x.name} subtitle={`${deviceQuery.data?.name ?? ""} · ${x.data_type}`} />
        <Card>
          {isSensor ? (
            <Gauge value={typeof value === "number" ? value : 0} min={x.min_value ?? 0} max={x.max_value ?? 100} unit={x.unit ?? ""} />
          ) : (
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <Text style={{ fontSize: 28, fontWeight: "900" }}>{value ? "ON" : "OFF"}</Text>
              <Toggle label={x.name} value={!!value} disabled={createValue.isPending} onValueChange={(v) => createValue.mutate({ datastream_id: x.id, value: v })} />
            </View>
          )}
          {history.length > 1 && <Sparkline data={history} height={130} />}
          {!latestQuery.data && !latestQuery.isLoading && <Text style={s.muted}>Ainda sem valores recebidos.</Text>}
        </Card>
        <Card><Text style={s.muted}>Chave</Text><Text style={s.h2}>{x.key}</Text><Text style={s.muted}>Unidade: {x.unit || "—"}</Text></Card>
        <Button variant="danger" onPress={() => deleteMutation.mutate({ id: x.id, deviceId: x.device_id }, { onSuccess: () => r.back() })} disabled={deleteMutation.isPending}>{deleteMutation.isPending ? "A eliminar…" : "Eliminar datastream"}</Button>
      </View>
    </View>
  );
}
