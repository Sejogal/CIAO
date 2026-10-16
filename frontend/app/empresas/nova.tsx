import { useState } from "react";
import { Text, View } from "react-native";
import { useRouter } from "expo-router";
import { C, s, Header, Card, Field, Button } from "@/ui";
import { useCreateCompany } from "@/api/companies";
import { ApiError } from "@/api/client";
export default function NewCompany() {
  const r = useRouter();
  const [n, setN] = useState("");
  const [d, setD] = useState("");
  const [err, setErr] = useState("");
  const createMutation = useCreateCompany();
  function submit() {
    setErr("");
    if (n.trim().length < 2) return setErr("Indique o nome da empresa.");
    createMutation.mutate(
      { name: n, description: d || undefined },
      { onSuccess: (c) => r.replace(`/empresas/${c.id}`), onError: (e) => setErr(e instanceof ApiError ? e.message : "Não foi possível criar a empresa.") },
    );
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Nova empresa" />
        {err ? <Text style={{ color: C.danger }}>{err}</Text> : null}
        <Card>
          <Field label="Nome" value={n} onChangeText={setN} />
          <Field label="Descrição" value={d} onChangeText={setD} />
          <Button onPress={submit} disabled={createMutation.isPending}>{createMutation.isPending ? "A criar…" : "Criar empresa"}</Button>
        </Card>
      </View>
    </View>
  );
}
