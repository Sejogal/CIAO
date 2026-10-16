import { useMemo, useState } from "react";
import { Text, View } from "react-native";
import { useRouter } from "expo-router";
import { s, Header, Card, Field, Button, Chips, Loading, Empty } from "@/ui";
import { useAllDatastreams } from "@/api/datastreams";
import { useAllDevices } from "@/api/devices";
import { useCreateAutomation } from "@/api/automation";

export default function NewAutomation() {
  const router = useRouter();
  const streamsQuery = useAllDatastreams();
  const devicesQuery = useAllDevices();
  const sensors = streamsQuery.data.filter((stream) => stream.data_type === "integer" || stream.data_type === "float");
  const [name, setName] = useState("Nova automação");
  const [datastreamId, setDatastreamId] = useState("");
  const [operator, setOperator] = useState<"<" | ">" | "=">("<");
  const [threshold, setThreshold] = useState("40");
  const [actionType, setActionType] = useState<"notification" | "control_device">("notification");
  const [targetId, setTargetId] = useState("");
  const [turnOn, setTurnOn] = useState(true);
  const create = useCreateAutomation();
  const selectedId = sensors.some((stream) => stream.id === datastreamId) ? datastreamId : sensors[0]?.id;
  const stream = sensors.find((item) => item.id === selectedId);
  const deviceById = useMemo(() => new Map(devicesQuery.data.map((device) => [device.id, device] as const)), [devicesQuery.data]);
  const projectId = stream ? deviceById.get(stream.device_id)?.project_id : undefined;
  const targets = streamsQuery.data.filter((item) =>
    item.data_type === "boolean" && deviceById.get(item.device_id)?.project_id === projectId,
  );
  const targetStream = targets.find((item) => item.id === targetId) ?? targets[0];
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Nova automação" />
        {(streamsQuery.isLoading || devicesQuery.isLoading) ? <Loading /> : sensors.length === 0 ?
          <Empty icon="flash-outline" title="Sem datastreams numéricos" text="Crie um datastream integer ou float para configurar uma regra de limite." /> :
          <Card>
            <Field label="Nome" value={name} onChangeText={setName} />
            <Text style={s.label}>Datastream</Text>
            <Chips value={selectedId ?? ""} onChange={setDatastreamId} options={sensors.map((item) => ({ value: item.id, label: item.name }))} />
            <Text style={s.label}>Condição</Text>
            <Chips value={operator} onChange={(v) => setOperator(v as typeof operator)} options={["<", ">", "="].map((v) => ({ value: v, label: v }))} />
            <Field label={`Limite${stream?.unit ? ` (${stream.unit})` : ""}`} value={threshold} onChangeText={setThreshold} />
            <Text style={s.label}>Ação</Text>
            <Chips value={actionType} onChange={(v) => setActionType(v as typeof actionType)} options={[
              { value: "notification", label: "Notificar" }, { value: "control_device", label: "Controlar atuador" },
            ]} />
            {actionType === "control_device" && <>
              {targets.length === 0 ? <Text style={s.error}>Este projeto não tem datastreams booleanos para controlar.</Text> : <>
                <Text style={s.label}>Datastream do atuador</Text>
                <Chips value={targetStream?.id ?? ""} onChange={setTargetId} options={targets.map((item) => ({ value: item.id, label: item.name }))} />
                <Chips value={turnOn ? "on" : "off"} onChange={(v) => setTurnOn(v === "on")} options={[{ value: "on", label: "Ligar" }, { value: "off", label: "Desligar" }]} />
              </>}
            </>}
            <Text style={s.muted}>A condição gera uma notificação interna. Intervalo mínimo: 5 minutos.</Text>
            <Button disabled={create.isPending || !projectId || !name.trim() || !threshold.trim() || !Number.isFinite(Number(threshold)) || (actionType === "control_device" && !targetStream)} onPress={() => {
              if (!stream || !projectId) return;
              create.mutate({
                project_id: projectId,
                datastream_id: stream.id,
                name: name.trim(),
                operator,
                threshold: Number(threshold),
                action: actionType === "notification" ? "Enviar notificação" : `Definir ${targetStream?.name} como ${turnOn ? "ligado" : "desligado"}`,
                action_type: actionType,
                target_datastream_id: actionType === "control_device" ? targetStream?.id : undefined,
                action_value: actionType === "control_device" ? turnOn : undefined,
                is_active: true,
                cooldown_seconds: 300,
              }, { onSuccess: () => router.back() });
            }}>Criar automação</Button>
            {!!create.error && <Text style={s.error}>{create.error.message}</Text>}
          </Card>}
      </View>
    </View>
  );
}
