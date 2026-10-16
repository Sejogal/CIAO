import { useState } from "react";
import { Text, View } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, Card, Field, Button } from "@/ui";
import { useRegister } from "@/api/auth";
import { ApiError } from "@/api/client";
export default function Registo() {
  const r = useRouter();
  const [n, setN] = useState("");
  const [e, setE] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState("");
  const registerMutation = useRegister();
  function submit() {
    setErr("");
    if (n.trim().length < 3) return setErr("Indique o seu nome completo.");
    if (!/^\S+@\S+\.\S+$/.test(e)) return setErr("Introduza um email válido.");
    if (p.length < 8) return setErr("A palavra-passe tem pelo menos 8 caracteres.");
    registerMutation.mutate(
      { name: n, email: e, password: p },
      { onSuccess: () => r.replace("/inicio"), onError: (err) => setErr(err instanceof ApiError ? err.message : "Não foi possível ligar ao servidor.") },
    );
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Card style={{ marginTop: 25 }}>
          <Header title="Criar conta" subtitle="Comece a usar o CIAO" back={false} />
          {err ? <Text style={{ color: C.danger }}>{err}</Text> : null}
          <Field label="Nome" value={n} onChangeText={setN} />
          <Field label="Email" value={e} onChangeText={setE} />
          <Field label="Palavra-passe" value={p} onChangeText={setP} secureTextEntry />
          <Button onPress={submit} disabled={registerMutation.isPending}>{registerMutation.isPending ? "A criar…" : "Criar conta"}</Button>
          <Text onPress={() => r.back()} style={{ textAlign: "center", color: C.primary }}>Já tenho conta</Text>
        </Card>
      </View>
    </View>
  );
}
