import { View, Text } from "react-native";
import { useState } from "react";
import { useRouter, useLocalSearchParams } from "expo-router";
import { s, Header, Card, Field, Button, Chips } from "@/ui";
import { useCreateDatastream, type Datastream } from "@/api/datastreams";
import { ApiError } from "@/api/client";
const TYPES: { value: Datastream["data_type"]; label: string }[] = [
  { value: "float", label: "Número" },
  { value: "boolean", label: "Sim/Não" },
  { value: "string", label: "Texto" },
];
export default function NewDatastream() {
  const r = useRouter();
  const { deviceId } = useLocalSearchParams<{ deviceId: string }>();
  const [n, setN] = useState("");
  const [key, setKey] = useState("");
  const [unit, setUnit] = useState("");
  const [dataType, setDataType] = useState<Datastream["data_type"]>("float");
  const [err, setErr] = useState("");
  const createMutation = useCreateDatastream();
  function submit() {
    setErr("");
    if (n.trim().length < 2) return setErr("Indique o nome do datastream.");
    const code = (key.trim() || n.trim()).toLowerCase().replace(/\s+/g, "_");
    createMutation.mutate(
      { device_id: deviceId, name: n, key: code, data_type: dataType, unit: unit || undefined },
      { onSuccess: () => r.back(), onError: (e) => setErr(e instanceof ApiError ? e.message : "Não foi possível criar o datastream.") },
    );
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Novo datastream" />
        {err ? <Text style={{ color: "#DC2626" }}>{err}</Text> : null}
        <Card>
          <Field label="Nome" value={n} onChangeText={setN} placeholder="Temperatura" />
          <Field label="Chave (opcional)" value={key} onChangeText={setKey} placeholder="temperature" />
          <Field label="Unidade" value={unit} onChangeText={setUnit} placeholder="°C, %, kW..." />
          <Chips value={dataType} onChange={(v) => setDataType(v as Datastream["data_type"])} options={TYPES} />
          <Button onPress={submit} disabled={createMutation.isPending}>{createMutation.isPending ? "A criar…" : "Criar datastream"}</Button>
        </Card>
      </View>
    </View>
  );
}
