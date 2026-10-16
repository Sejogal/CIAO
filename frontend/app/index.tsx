import { View, Text, Pressable, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";
import { useEffect } from "react";
import { C, s } from "@/ui";
import { useStore } from "@/store";
export default function Welcome() {
  const r = useRouter();
  const { authReady, loggedIn } = useStore();
  useEffect(() => {
    if (authReady && loggedIn) r.replace("/inicio");
  }, [authReady, loggedIn]);
  if (!authReady) return <SafeAreaView style={[s.safe, { alignItems: "center", justifyContent: "center" }]}><ActivityIndicator color={C.primary} /></SafeAreaView>;
  if (loggedIn) return null;
  return (
    <SafeAreaView style={[s.safe, { padding: 24 }]}>
      <View style={{ flex: 1, justifyContent: "space-between" }}>
        <View>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <View style={{ width: 58, height: 58, borderRadius: 18, backgroundColor: C.primary, alignItems: "center", justifyContent: "center" }}>
              <Ionicons name="radio-outline" size={30} color="#fff" />
            </View>
            <Pressable onPress={() => r.push("/definicoes")} style={s.icon}>
              <Ionicons name="settings-outline" size={22} color={C.ink} />
            </Pressable>
          </View>
          <Text style={{ fontSize: 52, fontWeight: "900", color: C.ink, marginTop: 25 }}>CIAO</Text>
          <Text style={{ fontSize: 19, color: C.ink }}>Conecta IoT Angola</Text>
          <Text style={[s.muted, { fontSize: 16, lineHeight: 24, marginTop: 20 }]}>Ligue os seus dispositivos, acompanhe sensores em tempo real e controle atuadores a partir do telemóvel.</Text>
          {[["hardware-chip", "ESP32, ESP8266 e mais"], ["stats-chart", "Dashboards com gráficos e medidores"], ["flash", "Automações e alertas"]].map(([i, t]) => (
            <View key={t} style={{ flexDirection: "row", gap: 12, alignItems: "center", marginTop: 22 }}>
              <Ionicons name={i as any} size={21} color={C.primary} />
              <Text style={{ color: C.ink }}>{t}</Text>
            </View>
          ))}
        </View>
        <View style={{ gap: 10 }}>
          <Pressable onPress={() => r.push("/entrar")} style={s.btn}>
            <Text style={s.btnText}>Entrar</Text>
          </Pressable>
          <Pressable onPress={() => r.push("/registo")} style={[s.btn, s.btnOutline]}>
            <Text style={{ color: C.primary, fontWeight: "800" }}>Criar conta</Text>
          </Pressable>
        </View>
      </View>
    </SafeAreaView>
  );
}
