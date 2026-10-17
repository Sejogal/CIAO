import { useEffect, useState } from "react";
import { ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { useMe, useLogout, useUpdateMe } from "@/api/auth";
import { notify } from "@/store";
import { s, Header, BottomNav, Card, Button, Field, Loading } from "@/ui";

export default function Profile() {
  const router = useRouter();
  const meQuery = useMe(true, true);
  const logout = useLogout();
  const updateMe = useUpdateMe();
  const [fullName, setFullName] = useState("");
  const [avatar, setAvatar] = useState("");
  const [language, setLanguage] = useState("pt");
  const [timezone, setTimezone] = useState("Africa/Luanda");

  useEffect(() => {
    if (!meQuery.data) return;
    setFullName(meQuery.data.full_name);
    setAvatar(meQuery.data.avatar ?? "");
    setLanguage(meQuery.data.language);
    setTimezone(meQuery.data.timezone);
  }, [meQuery.data]);

  return (
    <View style={s.safe}>
      <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
        <Header title="Perfil" />
        {meQuery.isLoading ? <Loading /> : meQuery.data ? (
          <Card>
            <Text style={s.h2}>Dados pessoais</Text>
            <Field label="Nome" value={fullName} onChangeText={setFullName} />
            <Text style={[s.muted, { marginTop: 10 }]}>Email</Text>
            <Text style={s.h2}>{meQuery.data.email}</Text>
            <Text style={[s.muted, { marginTop: 10 }]}>Perfil</Text>
            <Text style={s.h2}>{meQuery.data.role?.name ?? "Sem perfil atribuído"}</Text>
            <Field label="Avatar (URL, opcional)" value={avatar} onChangeText={setAvatar} />
            <Field label="Idioma" value={language} onChangeText={setLanguage} placeholder="pt" />
            <Field label="Fuso horário" value={timezone} onChangeText={setTimezone} placeholder="Africa/Luanda" />
            {updateMe.isError && <Text style={s.error}>{updateMe.error.message}</Text>}
            <Button
              disabled={updateMe.isPending || fullName.trim().length < 3}
              onPress={async () => {
                try {
                  await updateMe.mutateAsync({
                    full_name: fullName.trim(),
                    avatar: avatar.trim() || null,
                    language: language.trim(),
                    timezone: timezone.trim(),
                  });
                  notify("Perfil atualizado.");
                } catch {
                  // O erro fica visível no formulário via updateMe.isError.
                }
              }}
            >
              {updateMe.isPending ? "A guardar..." : "Guardar alterações"}
            </Button>
          </Card>
        ) : <Text style={s.error}>{meQuery.error?.message ?? "Não foi possível carregar o perfil."}</Text>}
        <Button variant="outline" onPress={() => router.push("/definicoes")}>Definições</Button>
        <Button variant="danger" onPress={async () => { await logout(); router.replace("/"); }}>Terminar sessão</Button>
      </ScrollView>
      <BottomNav />
    </View>
  );
}
