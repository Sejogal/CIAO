import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { C, s, Header, BottomNav, Card, Section } from "@/ui";
import { useMe } from "@/api/auth";
import { useCompanies } from "@/api/companies";
import { useProjects } from "@/api/projects";
import { useAllDevices } from "@/api/devices";
import { useNotifications } from "@/api/automation";
export default function Inicio() {
  const r = useRouter();
  const notificationsQuery = useNotifications();
  const notices = notificationsQuery.data ?? [];
  const meQuery = useMe(true);
  const companiesQuery = useCompanies();
  const projectsQuery = useProjects();
  const devicesQuery = useAllDevices();
  const companies = companiesQuery.data ?? [];
  const projects = projectsQuery.data ?? [];
  const devices = devicesQuery.data;
  const online = devices.filter((d) => d.status === "online").length;
  const nav = (p: string, label: string) => (
    <Pressable onPress={() => r.push(p as any)} style={[s.btn, s.btnSoft, { flex: 1 }]}><Text style={{ color: C.primary, fontWeight: "800", textAlign: "center" }}>{label}</Text></Pressable>
  );
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header back={false} title={`Olá, ${meQuery.data?.full_name.split(" ")[0] ?? "visitante"}`} subtitle={`${companies.length} empresas com acesso`} right={<Pressable onPress={() => r.push("/notificacoes")} style={s.icon}><Ionicons name="notifications-outline" size={21} color={C.ink} /><Text style={{ color: C.primary, fontSize: 10, fontWeight: "800" }}>{notices.filter((n) => !n.read_at).length || ""}</Text></Pressable>} />
        <View style={{ flexDirection: "row", gap: 10 }}>
          {[["Projetos", projects.length], ["Dispositivos", devices.length], ["Online", `${online}/${devices.length}`]].map((x) => (
            <Card key={x[0] as string} style={{ flex: 1, padding: 12 }}><Text style={s.muted}>{x[0]}</Text><Text style={{ fontSize: 22, fontWeight: "900", color: C.ink }}>{x[1]}</Text></Card>
          ))}
        </View>
        <Section title="Atalhos" />
        <View style={{ flexDirection: "row", gap: 10 }}>{nav("/empresas/nova", "Empresa")}{nav("/projetos/novo", "Projeto")}{nav("/dispositivos/novo", "Dispositivo")}</View>
        <Section title="Empresas" />
        {companies.map((c) => (
          <Pressable key={c.id} onPress={() => r.push(`/empresas/${c.id}`)}>
            <Card><Text style={s.h2}>{c.name}</Text><Text style={s.muted}>{projects.filter((p) => p.company_id === c.id).length} projetos</Text></Card>
          </Pressable>
        ))}
        {notices.length > 0 && (
          <>
            <Section title="Atividade recente" />
            {notices.slice(0, 3).map((n) => (
              <Card key={n.id} style={{ flexDirection: "row", alignItems: "center" }}>
                <Ionicons name="warning-outline" size={23} color={n.level === "critical" ? C.danger : C.warning} />
                <View style={{ flex: 1 }}><Text style={{ fontWeight: "700", color: C.ink }}>{n.title}</Text><Text style={s.muted}>{new Date(n.created_at).toLocaleString("pt-PT")}</Text></View>
              </Card>
            ))}
          </>
        )}
        <BottomNav />
      </View>
    </View>
  );
}
