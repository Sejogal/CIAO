import { View, Text, Pressable } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { s, Header, Card, Button, Section, Status, Loading, Empty } from "@/ui";
import { useProject, useDeleteProject } from "@/api/projects";
import { useCompany } from "@/api/companies";
import { useProjectDevices } from "@/api/devices";
export default function Project() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const r = useRouter();
  const projectQuery = useProject(id);
  const companyQuery = useCompany(projectQuery.data?.company_id);
  const devicesQuery = useProjectDevices(id);
  const deleteMutation = useDeleteProject();
  if (projectQuery.isLoading) return <View style={s.safe}><View style={s.content}><Header title="Projeto" /><Loading /></View></View>;
  const p = projectQuery.data;
  if (!p) return <View style={s.safe}><View style={s.content}><Header title="Projeto" /><Text>Projeto não encontrado.</Text></View></View>;
  const devices = devicesQuery.data ?? [];
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title={p.name} subtitle={companyQuery.data?.name} />
        <Card><Text style={s.h2}>{p.description}</Text><Text style={s.muted}>{devices.length} dispositivos</Text></Card>
        <Section title="Dispositivos" />
        {!devicesQuery.isLoading && !devices.length && <Empty icon="hardware-chip-outline" title="Sem dispositivos" text="Registe o primeiro dispositivo deste projeto." action={<Button onPress={() => r.push("/dispositivos/novo")}>Registar</Button>} />}
        {devices.map((d) => (
          <Pressable key={d.id} onPress={() => r.push(`/dispositivos/${d.id}`)}>
            <Card style={{ flexDirection: "row", justifyContent: "space-between" }}>
              <View><Text style={s.h2}>{d.name}</Text><Text style={s.muted}>{d.model || "—"} · {d.last_seen ? new Date(d.last_seen).toLocaleString("pt-PT") : "nunca"}</Text></View>
              <Status online={d.status === "online"} />
            </Card>
          </Pressable>
        ))}
        <Button variant="danger" onPress={() => deleteMutation.mutate(p.id, { onSuccess: () => r.back() })} disabled={deleteMutation.isPending}>{deleteMutation.isPending ? "A eliminar…" : "Eliminar projeto"}</Button>
      </View>
    </View>
  );
}
