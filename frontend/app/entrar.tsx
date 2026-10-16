import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, Card, Field, Button } from "@/ui";
import { useLogin } from "@/api/auth";
import { ApiError } from "@/api/client";
export default function Login() {
  const r = useRouter();
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState("");
  const loginMutation = useLogin();
  function submit() {
    setErr("");
    if (!/^\S+@\S+\.\S+$/.test(email)) return setErr("Introduza um email válido.");
    if (pass.length < 8) return setErr("A palavra-passe tem pelo menos 8 caracteres.");
    loginMutation.mutate(
      { email, password: pass },
      {
        onSuccess: () => r.replace("/inicio"),
        onError: (e) => setErr(e instanceof ApiError ? e.message : "Não foi possível ligar ao servidor."),
      },
    );
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Iniciar sessão" subtitle="Bem-vindo de volta" />
        {err ? <Card style={{ backgroundColor: "#fff1f2" }}><Text style={{ color: C.danger }}>{err}</Text></Card> : null}
        <Card>
          <Field label="Email" value={email} onChangeText={setEmail} placeholder="voce@exemplo.com" />
          <Field label="Palavra-passe" value={pass} onChangeText={setPass} secureTextEntry />
          <Pressable onPress={() => r.push("/recuperar")}><Text style={{ color: C.primary, fontWeight: "700", textAlign: "right" }}>Esqueceu a palavra-passe?</Text></Pressable>
          <Button onPress={submit} disabled={loginMutation.isPending}>{loginMutation.isPending ? "A entrar…" : "Entrar"}</Button>
        </Card>
        <Text style={{ textAlign: "center", color: C.muted }}>Ainda não tem conta? <Text onPress={() => r.push("/registo")} style={{ color: C.primary, fontWeight: "700" }}>Criar conta</Text></Text>
      </View>
    </View>
  );
}
