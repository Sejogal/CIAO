import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, BottomNav, Card, Empty, Loading } from "@/ui";
import { useCompanies } from "@/api/companies";
export default function Companies() {
  const r = useRouter();
  const companiesQuery = useCompanies();
  const companies = companiesQuery.data ?? [];
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Empresas" subtitle={`${companies.length} com acesso`} right={<Pressable onPress={() => r.push("/empresas/nova")} style={s.icon}><Text style={{ fontSize: 24, color: C.primary }}>+</Text></Pressable>} />
        {companiesQuery.isLoading && <Loading />}
        {!companiesQuery.isLoading && !companies.length && <Empty icon="business-outline" title="Sem empresas" text="Crie a sua empresa para começar a registar projetos e dispositivos." />}
        {companies.map((c) => (
          <Pressable key={c.id} onPress={() => r.push(`/empresas/${c.id}`)}>
            <Card><Text style={s.h2}>{c.name}</Text><Text style={s.muted}>{c.description || "Sem descrição"}</Text></Card>
          </Pressable>
        ))}
        <BottomNav />
      </View>
    </View>
  );
}
