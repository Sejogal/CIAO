import { View, Text } from "react-native";
import { useState } from "react";
import { useRouter, useLocalSearchParams } from "expo-router";
import { s, Header, Card, Field, Button, Chips, Empty } from "@/ui";
import { useCreateDevice, setLastProvisioned } from "@/api/devices";
import { useProjects } from "@/api/projects";
import { ApiError } from "@/api/client";
const MODELS = ["ESP32", "ESP8266", "Arduino", "Raspberry Pi", "Outro"];
export default function NewDevice() {
  const r = useRouter();
  const params = useLocalSearchParams<{ projectId?: string }>();
  const projectsQuery = useProjects();
  const projects = projectsQuery.data ?? [];
  const [n, setN] = useState("");
  const [serial, setSerial] = useState("");
  const [model, setModel] = useState("ESP32");
  const [p, setP] = useState(params.projectId || "");
  const [err, setErr] = useState("");
  const createMutation = useCreateDevice();
  const projectId = p || projects[0]?.id || "";
  function submit() {
    setErr("");
    if (n.trim().length < 2) return setErr("Indique o nome do dispositivo.");
    if (!projectId) return setErr("Selecione um projeto.");
    createMutation.mutate(
      { project_id: projectId, name: n, serial: serial || undefined, model },
      {
        onSuccess: (device) => {
          setLastProvisioned(device);
          r.replace(`/provisionamento/${device.id}`);
        },
        onError: (e) => setErr(e instanceof ApiError ? e.message : "Não foi possível registar o dispositivo."),
      },
    );
  }
  if (!projectsQuery.isLoading && !projects.length) {
    return <View style={s.safe}><View style={s.content}><Header title="Registar dispositivo" /><Empty icon="folder-outline" title="Crie um projeto primeiro" text="Um dispositivo tem de pertencer a um projeto." /></View></View>;
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Registar dispositivo" />
        {err ? <Text style={{ color: "#DC2626" }}>{err}</Text> : null}
        <Card>
          <Field label="Nome" value={n} onChangeText={setN} />
          <Field label="Número de série (opcional)" value={serial} onChangeText={setSerial} />
          <Chips value={model} onChange={setModel} options={MODELS.map((x) => ({ value: x, label: x }))} />
          <Chips value={projectId} onChange={setP} options={projects.map((x) => ({ value: x.id, label: x.name }))} />
          <Button onPress={submit} disabled={createMutation.isPending}>{createMutation.isPending ? "A registar…" : "Registar dispositivo"}</Button>
        </Card>
      </View>
    </View>
  );
}
