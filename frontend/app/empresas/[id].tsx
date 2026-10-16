import { View, Text, Pressable } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { s, Header, Card, Section, Loading } from "@/ui";
import { useCompany, useCompanyMembers } from "@/api/companies";
import { useProjects } from "@/api/projects";
export default function Company() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const r = useRouter();
  const companyQuery = useCompany(id);
  const membersQuery = useCompanyMembers(id);
  const projectsQuery = useProjects();
  if (companyQuery.isLoading) return <View style={s.safe}><View style={s.content}><Header title="Empresa" /><Loading /></View></View>;
  const c = companyQuery.data;
  if (!c) return <View style={s.safe}><View style={s.content}><Header title="Empresa" /><Text>Empresa não encontrada.</Text></View></View>;
  const projects = (projectsQuery.data ?? []).filter((p) => p.company_id === c.id);
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title={c.name} subtitle={c.description || undefined} />
        <Card>
          <Text style={s.h2}>Membros</Text>
          {(membersQuery.data ?? []).map((m) => (
            <View key={m.id} style={{ paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#eee" }}>
              <Text style={{ fontWeight: "700" }}>{m.user.full_name}</Text>
              <Text style={s.muted}>{m.user.email} · {m.role}</Text>
            </View>
          ))}
        </Card>
        <Section title="Projetos" />
        {projects.map((p) => (
          <Pressable key={p.id} onPress={() => r.push(`/projetos/${p.id}`)}>
            <Card><Text style={s.h2}>{p.name}</Text><Text style={s.muted}>{p.description}</Text></Card>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
