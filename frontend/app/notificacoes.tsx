import { Text, View } from "react-native";
import { Button, C, Card, Header, Loading, s } from "@/ui";
import { useMarkAllNotificationsRead, useMarkNotificationRead, useNotifications } from "@/api/automation";

export default function Notifications() {
  const query = useNotifications();
  const markAll = useMarkAllNotificationsRead();
  const markOne = useMarkNotificationRead();
  const notices = query.data ?? [];
  const unread = notices.filter((notice) => !notice.read_at).length;
  return (
    <View style={s.safe}>
      <View style={s.content}>
        <Header title="Notificações" subtitle={`${unread} por ler`} right={<Text onPress={() => markAll.mutate()} style={{ color: C.primary, fontWeight: "700", padding: 8 }}>Ler tudo</Text>} />
        {query.isLoading && <Loading />}
        {!query.isLoading && notices.length === 0 && <Card><Text style={s.muted}>Ainda não há notificações.</Text></Card>}
        {notices.map((notice) => <Card key={notice.id} style={{ opacity: notice.read_at ? 0.65 : 1 }}>
          <Text style={{ fontWeight: "800", color: notice.level === "critical" ? C.danger : C.warning }}>{notice.title}</Text>
          <Text style={{ color: C.ink }}>{notice.message}</Text>
          <Text style={s.muted}>{new Date(notice.created_at).toLocaleString("pt-PT")}</Text>
          {!notice.read_at && <Button variant="soft" disabled={markOne.isPending} onPress={() => markOne.mutate({ id: notice.id, read: true })}>Marcar como lida</Button>}
        </Card>)}
        {!!(query.error || markAll.error || markOne.error) && <Text style={s.error}>{(query.error || markAll.error || markOne.error)?.message}</Text>}
      </View>
    </View>
  );
}
