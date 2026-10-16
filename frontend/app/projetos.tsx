import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, BottomNav, Card, Chips, Empty, Button, Loading } from "@/ui";
import { useProjects } from "@/api/projects";
import { useCompanies } from "@/api/companies";
export default function Projects() {
  const r = useRouter();
  const projectsQuery = useProjects();
  const companiesQuery = useCompanies();
  const [co, setCo] = useState("all");
  const projects = projectsQuery.data ?? [];
  const companies = companiesQuery.data ?? [];
  const list = projects.filter((p) => co === "all" || p.company_id === co);
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Projetos" subtitle={`${projects.length} projetos`} right={<Pressable onPress={() => r.push("/projetos/novo")} style={s.icon}><Text style={{ fontSize: 24, color: C.primary }}>+</Text></Pressable>} />
        <Chips value={co} onChange={setCo} options={[{ value: "all", label: "Todas as empresas" }, ...companies.map((c) => ({ value: c.id, label: c.name }))]} />
        {projectsQuery.isLoading && <Loading />}
        {!projectsQuery.isLoading && !list.length && <Empty icon="folder-outline" title="Sem projetos" text="Um projeto agrupa dispositivos de uma mesma solução IoT." action={<Button onPress={() => r.push("/projetos/novo")}>Criar projeto</Button>} />}
        {list.map((p) => (
          <Pressable key={p.id} onPress={() => r.push(`/projetos/${p.id}`)}>
            <Card><Text style={s.h2}>{p.name}</Text><Text style={s.muted}>{p.description}</Text><Text style={{ fontSize: 12, color: C.primary }}>{companies.find((c) => c.id === p.company_id)?.name}</Text></Card>
          </Pressable>
        ))}
        <BottomNav />
      </View>
    </View>
  );
}
