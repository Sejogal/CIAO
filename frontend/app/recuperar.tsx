import { View, Text } from "react-native";
import { useRouter } from "expo-router";
import { s, Header, Card, Button } from "@/ui";
export default function Recuperar() {
  const r = useRouter();
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Recuperar acesso" subtitle="Ainda não disponível" />
        <Card>
          <Text style={s.muted}>A recuperação de palavra-passe ainda não está disponível no CIAO. Contacte um administrador para repor o seu acesso.</Text>
          <Button onPress={() => r.back()}>Voltar</Button>
        </Card>
      </View>
    </View>
  );
}
