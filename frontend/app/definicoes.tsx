import { View, Text } from "react-native";
import { useState } from "react";
import { useStore, actions, notify } from "@/store";
import { s, Header, BottomNav, Card, Toggle, Field, Button } from "@/ui";
import { setApiUrl } from "@/api/client";
export default function Settings() {
  const { prefs } = useStore();
  const [url, setUrl] = useState(prefs.apiUrl);
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Definições" />
        <Card>
          <Text style={s.h2}>Notificações</Text>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}><Text>Push</Text><Toggle label="Push" value={prefs.push} onValueChange={(v) => actions.setPrefs({ push: v })} /></View>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}><Text>Email</Text><Toggle label="Email" value={prefs.email} onValueChange={(v) => actions.setPrefs({ email: v })} /></View>
        </Card>
        <Card>
          <Text style={s.h2}>Servidor API</Text>
          <Text style={s.muted}>No simulador Android use 10.0.2.2 em vez de localhost. Num telemóvel físico, use o IP da rede local do computador (ex.: http://192.168.1.10:8000/api/v1).</Text>
          <Field label="URL" value={url} onChangeText={setUrl} />
          <Button onPress={async () => { await setApiUrl(url); actions.setPrefs({ apiUrl: url }); notify("URL da API atualizado."); }}>Guardar</Button>
        </Card>
        <BottomNav />
      </View>
    </View>
  );
}
