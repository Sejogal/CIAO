import { useState } from "react";
import { View, Text } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { C, s, Header, Card, Button } from "@/ui";
import { takeLastProvisioned, type DeviceWithSecrets } from "@/api/devices";
export default function Provision() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const r = useRouter();
  const [secrets] = useState<DeviceWithSecrets | null>(() => takeLastProvisioned(id));
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Provisionamento" subtitle={secrets?.name} back={false} />
        {!secrets ? (
          <Card><Text style={s.muted}>Os dados de ligação só são mostrados uma vez, imediatamente após o registo do dispositivo. Se os perdeu, elimine este dispositivo e registe-o de novo.</Text></Card>
        ) : (
          <>
            <Card style={{ backgroundColor: "#fff7ed" }}>
              <Text style={{ color: C.warning, fontWeight: "700" }}>Guarde estes dados agora — não serão mostrados outra vez.</Text>
            </Card>
            <Card>
              <Text style={s.h2}>Token do dispositivo</Text>
              <Text selectable style={{ fontFamily: "monospace", color: C.primary }}>{secrets.token}</Text>
              <Text style={s.muted}>Usado para o dispositivo autenticar cada leitura enviada por MQTT (vai no payload, junto com o valor).</Text>
            </Card>
            <Card>
              <Text style={s.h2}>Credenciais MQTT</Text>
              <Text style={s.muted}>Utilizador</Text>
              <Text selectable style={{ fontFamily: "monospace", color: C.primary }}>{secrets.mqtt_username}</Text>
              <Text style={[s.muted, { marginTop: 8 }]}>Palavra-passe</Text>
              <Text selectable style={{ fontFamily: "monospace", color: C.primary }}>{secrets.mqtt_password}</Text>
            </Card>
          </>
        )}
        <Button onPress={() => r.replace(`/dispositivos/${id}`)}>Concluído</Button>
      </View>
    </View>
  );
}
