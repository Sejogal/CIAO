import { View, Text } from "react-native";
import { useState } from "react";
import { useRouter } from "expo-router";
import { s, Header, Card, Field, Button, Chips, Empty } from "@/ui";
import { useCreateProject } from "@/api/projects";
import { useCompanies } from "@/api/companies";
import { ApiError } from "@/api/client";
export default function NewProject() {
  const r = useRouter();
  const companiesQuery = useCompanies();
  const companies = companiesQuery.data ?? [];
  const [n, setN] = useState("");
  const [d, setD] = useState("");
  const [co, setCo] = useState("");
  const [err, setErr] = useState("");
  const createMutation = useCreateProject();
  const companyId = co || companies[0]?.id || "";
  function submit() {
    setErr("");
    if (n.trim().length < 2) return setErr("Indique o nome do projeto.");
    if (!companyId) return setErr("Selecione uma empresa.");
    createMutation.mutate(
      { name: n, description: d || undefined, company_id: companyId },
      { onSuccess: (p) => r.replace(`/projetos/${p.id}`), onError: (e) => setErr(e instanceof ApiError ? e.message : "Não foi possível criar o projeto.") },
    );
  }
  if (!companiesQuery.isLoading && !companies.length) {
    return <View style={s.safe}><View style={s.content}><Header title="Novo projeto" /><Empty icon="business-outline" title="Crie uma empresa primeiro" text="Um projeto pertence sempre a uma empresa." /></View></View>;
  }
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Novo projeto" />
        {err ? <Text style={{ color: "#DC2626" }}>{err}</Text> : null}
        <Card>
          <Field label="Nome" value={n} onChangeText={setN} />
          <Field label="Descrição" value={d} onChangeText={setD} />
          <Chips value={companyId} onChange={setCo} options={companies.map((c) => ({ value: c.id, label: c.name }))} />
          <Button onPress={submit} disabled={createMutation.isPending}>{createMutation.isPending ? "A criar…" : "Criar projeto"}</Button>
        </Card>
      </View>
    </View>
  );
}
