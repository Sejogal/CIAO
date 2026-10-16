import { View, Text } from "react-native";
import { useRouter } from "expo-router";
import { s, Header, BottomNav, Card, Button, Loading } from "@/ui";
import { useMe, useLogout } from "@/api/auth";
export default function Profile() {
  const r = useRouter();
  const meQuery = useMe(true);
  const logout = useLogout();
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Perfil" />
        {meQuery.isLoading ? <Loading /> : (
          <Card>
            <Text style={s.muted}>Nome</Text>
            <Text style={s.h2}>{meQuery.data?.full_name}</Text>
            <Text style={[s.muted, { marginTop: 10 }]}>Email</Text>
            <Text style={s.h2}>{meQuery.data?.email}</Text>
            <Text style={[s.muted, { marginTop: 10 }]}>Perfil</Text>
            <Text style={s.h2}>{meQuery.data?.role?.name ?? "Sem perfil atribuído"}</Text>
          </Card>
        )}
        <Button variant="outline" onPress={() => r.push("/definicoes")}>Definições</Button>
        <Button variant="danger" onPress={async () => { await logout(); r.replace("/"); }}>Terminar sessão</Button>
        <BottomNav />
      </View>
    </View>
  );
}
