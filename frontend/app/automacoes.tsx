import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, BottomNav, Card, Toggle, Button, Empty, Loading } from "@/ui";
import { useAllAutomations, useDeleteAutomation, useUpdateAutomation } from "@/api/automation";
import { useProjects } from "@/api/projects";
import { useAllDatastreams } from "@/api/datastreams";

export default function Automacoes() {
  const router = useRouter();
  const projectsQuery = useProjects();
  const streamsQuery = useAllDatastreams();
  const projects = projectsQuery.data ?? [];
  const rulesQuery = useAllAutomations(projects.map((project) => project.id));
  const update = useUpdateAutomation();
  const remove = useDeleteAutomation();
  const rules = rulesQuery.data;
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Automações" subtitle={`${rules.length} regras`} right={<Pressable onPress={() => router.push("/automacoes/nova")} style={s.icon}><Text style={{ fontSize: 24, color: C.primary }}>+</Text></Pressable>} />
        {(projectsQuery.isLoading || streamsQuery.isLoading || rulesQuery.isLoading) && <Loading />}
        {!rulesQuery.isLoading && rules.length === 0 && <Empty icon="flash-outline" title="Sem automações" text="Crie uma regra para gerar notificações quando um valor ultrapassar o limite configurado." />}
        {rules.map((rule) => (
          <Card key={rule.id}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", gap: 12 }}>
              <View style={{ flex: 1 }}>
                <Text style={s.h2}>{rule.name}</Text>
                <Text style={s.muted}>{streamsQuery.data.find((stream) => stream.id === rule.datastream_id)?.name ?? "Datastream removido"} {rule.operator} {rule.threshold}</Text>
                <Text style={s.muted}>{rule.action} · intervalo {rule.cooldown_seconds}s</Text>
              </View>
              <Toggle label={rule.name} value={rule.is_active} disabled={update.isPending} onValueChange={(is_active) => update.mutate({ id: rule.id, project_id: rule.project_id, is_active })} />
            </View>
            <Button variant="danger" disabled={remove.isPending} onPress={() => remove.mutate({ id: rule.id, project_id: rule.project_id })}>Eliminar</Button>
          </Card>
        ))}
        {!!(update.error || remove.error) && <Text style={s.error}>{(update.error || remove.error)?.message}</Text>}
        <BottomNav />
      </View>
    </View>
  );
}
