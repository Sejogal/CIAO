import { useState } from "react";
import { Text, View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { ApiError } from "@/api/client";
import { useConfirmPasswordReset, useRequestPasswordReset } from "@/api/auth";
import { C, s, Header, Card, Field, Button } from "@/ui";

export default function RecoverPassword() {
  const router = useRouter();
  const params = useLocalSearchParams<{ token?: string }>();
  const token = typeof params.token === "string" ? params.token : "";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const request = useRequestPasswordReset();
  const confirm = useConfirmPasswordReset();

  function submitRequest() {
    setError("");
    request.mutate(email.trim(), {
      onSuccess: () => setSent(true),
      onError: (cause) => setError(cause instanceof ApiError ? cause.message : "Nao foi possivel enviar o email."),
    });
  }

  function submitReset() {
    setError("");
    if (password.length < 8) return setError("A palavra-passe deve ter pelo menos 8 caracteres.");
    if (password !== confirmation) return setError("As palavras-passe nao coincidem.");
    confirm.mutate({ token, new_password: password }, {
      onSuccess: () => router.replace("/entrar"),
      onError: (cause) => setError(cause instanceof ApiError ? cause.message : "Nao foi possivel atualizar a palavra-passe."),
    });
  }

  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title={token ? "Nova palavra-passe" : "Recuperar acesso"} />
        {error ? <Card style={{ backgroundColor: "#fff1f2" }}><Text style={{ color: C.danger }}>{error}</Text></Card> : null}
        {token ? (
          <Card>
            <Field label="Nova palavra-passe" value={password} onChangeText={setPassword} secureTextEntry />
            <Field label="Confirmar palavra-passe" value={confirmation} onChangeText={setConfirmation} secureTextEntry />
            <Button onPress={submitReset} disabled={confirm.isPending}>{confirm.isPending ? "A atualizar..." : "Guardar nova palavra-passe"}</Button>
          </Card>
        ) : sent ? (
          <Card>
            <Text style={s.muted}>Se existir uma conta para este email, enviamos um link válido por 30 minutos. Abra-o neste dispositivo para escolher uma nova palavra-passe.</Text>
            <Button variant="outline" onPress={() => router.replace("/entrar")}>Voltar ao início de sessão</Button>
          </Card>
        ) : (
          <Card>
            <Text style={s.muted}>Indique o email da conta. Enviaremos um link para confirmar a sua identidade.</Text>
            <Field label="Email" value={email} onChangeText={setEmail} placeholder="voce@exemplo.com" />
            <Button onPress={submitRequest} disabled={request.isPending}>{request.isPending ? "A enviar..." : "Enviar link de recuperação"}</Button>
          </Card>
        )}
      </View>
    </View>
  );
}
