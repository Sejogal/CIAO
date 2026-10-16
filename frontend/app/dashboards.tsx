import { useMemo, useState } from "react";
import { ScrollView, Text, TextInput, View } from "react-native";
import {
  BottomNav, Button, Card, Chips, C, Empty, Gauge, Header, Loading,
  Section, s, Status, Toggle,
} from "@/ui";
import { useAllDatastreams, useCreateValue, useLatestValue, useValueHistory, type Datastream } from "@/api/datastreams";
import { useAllDevices } from "@/api/devices";
import { useProjects } from "@/api/projects";
import {
  useCreateDashboard, useCreateDashboardWidget, useDashboardWidgets,
  useDeleteDashboardWidget, useProjectDashboards, type DashboardWidget,
} from "@/api/dashboards";

function ValueWidget({ stream }: { stream: Datastream }) {
  const latest = useLatestValue(stream.id);
  const value = latest.data?.value;
  if (typeof value === "number" && stream.min_value !== null && stream.max_value !== null) {
    return <Gauge value={value} min={stream.min_value} max={stream.max_value} unit={stream.unit ?? ""} />;
  }
  return <Text style={{ color: C.ink, fontSize: 28, fontWeight: "800" }}>
    {value === undefined ? "—" : typeof value === "object" ? JSON.stringify(value) : String(value)}{stream.unit ?? ""}
  </Text>;
}

function ChartWidget({ stream }: { stream: Datastream }) {
  const history = useValueHistory(stream.id, 24);
  const values = (history.data ?? []).map((item) => item.value).filter((v): v is number => typeof v === "number").reverse();
  if (values.length < 2) return <Text style={s.muted}>Ainda não há valores suficientes para o gráfico.</Text>;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return (
    <View style={{ gap: 8 }}>
      <View style={{ height: 96, flexDirection: "row", alignItems: "flex-end", gap: 3 }}>
        {values.map((value, index) => (
          <View key={`${index}-${value}`} style={{ flex: 1, height: `${Math.max(5, ((value - min) / range) * 100)}%`, backgroundColor: C.primary, borderRadius: 3 }} />
        ))}
      </View>
      <Text style={s.muted}>{min}{stream.unit ?? ""} — {max}{stream.unit ?? ""} · últimas {values.length} leituras</Text>
    </View>
  );
}

function SwitchWidget({ stream, online }: { stream: Datastream; online: boolean }) {
  const latest = useLatestValue(stream.id);
  const writeValue = useCreateValue();
  const on = latest.data?.value === true;
  return (
    <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
      <Text style={{ color: C.ink, fontSize: 20, fontWeight: "800" }}>{on ? "Ligado" : "Desligado"}</Text>
      <Toggle label={stream.name} value={on} disabled={!online || writeValue.isPending} onValueChange={(value) => writeValue.mutate({ datastream_id: stream.id, value })} />
    </View>
  );
}

function SavedWidget({ widget, stream, online, onDelete, deleting }: {
  widget: DashboardWidget;
  stream: Datastream;
  online: boolean;
  onDelete: () => void;
  deleting: boolean;
}) {
  return (
    <Card>
      <Section title={widget.name} right={<Text onPress={onDelete} style={{ color: C.danger, fontWeight: "700", padding: 4 }}>{deleting ? "A remover…" : "Remover"}</Text>} />
      {widget.widget_type === "chart" ? <ChartWidget stream={stream} />
        : widget.widget_type === "switch" && stream.data_type === "boolean" ? <SwitchWidget stream={stream} online={online} />
          : <ValueWidget stream={stream} />}
    </Card>
  );
}

export default function DashboardsScreen() {
  const projectsQuery = useProjects();
  const devicesQuery = useAllDevices();
  const streamsQuery = useAllDatastreams();
  const [projectChoice, setProjectChoice] = useState<string | null>(null);
  const [dashboardChoice, setDashboardChoice] = useState<string | null>(null);
  const [newName, setNewName] = useState("");
  const projects = projectsQuery.data ?? [];
  const projectId = projects.some((p) => p.id === projectChoice) ? projectChoice! : projects[0]?.id;
  const project = projects.find((p) => p.id === projectId);
  const devices = (devicesQuery.data ?? []).filter((d) => d.project_id === projectId);
  const deviceIds = useMemo(() => new Set(devices.map((d) => d.id)), [devices]);
  const streams = (streamsQuery.data ?? []).filter((stream) => deviceIds.has(stream.device_id) && stream.is_active);
  const dashboardsQuery = useProjectDashboards(projectId);
  const dashboards = dashboardsQuery.data ?? [];
  const dashboardId = dashboards.some((d) => d.id === dashboardChoice) ? dashboardChoice! : dashboards[0]?.id;
  const dashboard = dashboards.find((d) => d.id === dashboardId);
  const widgetsQuery = useDashboardWidgets(dashboardId);
  const widgets = widgetsQuery.data ?? [];
  const createDashboard = useCreateDashboard();
  const createWidget = useCreateDashboardWidget();
  const deleteWidget = useDeleteDashboardWidget();

  const createDashboardNow = () => {
    if (!projectId) return;
    const name = newName.trim() || `Painel ${project?.name ?? "do projeto"}`;
    createDashboard.mutate({ project_id: projectId, name }, { onSuccess: (created) => setDashboardChoice(created.id) });
  };

  const addWidget = (stream: Datastream, type: DashboardWidget["widget_type"]) => {
    if (!dashboardId) return;
    createWidget.mutate({ dashboard_id: dashboardId, datastream_id: stream.id, name: stream.name, widget_type: type });
  };

  const deviceForStream = (stream: Datastream) => devices.find((device) => device.id === stream.device_id);

  return (
    <View style={s.safe}>
      <ScrollView contentContainerStyle={[s.content, { paddingBottom: 100 }]}>
        <Header title="Dashboards" subtitle={project?.name ?? "Selecione um projeto"} />
        {projectsQuery.isLoading && <Loading />}
        {!projectsQuery.isLoading && projects.length === 0 && <Empty icon="folder-outline" title="Sem projetos" text="Crie um projeto antes de configurar um dashboard." />}
        {projects.length > 0 && <>
          <Chips value={projectId ?? ""} onChange={setProjectChoice} options={projects.map((p) => ({ value: p.id, label: p.name }))} />
          {dashboards.length > 0 && <Chips value={dashboardId ?? ""} onChange={setDashboardChoice} options={dashboards.map((item) => ({ value: item.id, label: item.name }))} />}
          {dashboardsQuery.isLoading && <Loading />}
          {!dashboardsQuery.isLoading && dashboards.length === 0 && (
            <Card>
              <Text style={s.h2}>Crie o primeiro dashboard</Text>
              <TextInput value={newName} onChangeText={setNewName} placeholder={`Painel ${project?.name ?? ""}`} style={s.input} />
              <Button onPress={createDashboardNow} disabled={createDashboard.isPending}>Criar dashboard</Button>
              {!!createDashboard.error && <Text style={s.error}>{createDashboard.error.message}</Text>}
            </Card>
          )}
          {dashboard && <>
            <Card style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <View><Text style={s.muted}>Projeto</Text><Text style={s.h2}>{project?.name}</Text></View>
              <Text style={s.muted}>{devices.length} dispositivo(s)</Text>
            </Card>
            {devices.map((device) => <Card key={device.id} style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
              <View><Text style={s.muted}>Dispositivo</Text><Text style={s.h2}>{device.name}</Text></View><Status online={device.status === "online"} />
            </Card>)}
            {widgetsQuery.isLoading && <Loading />}
            {!widgetsQuery.isLoading && widgets.length > 0 && <Section title="Widgets guardados" />}
            {widgets.map((widget) => {
              const stream = streams.find((item) => item.id === widget.datastream_id);
              if (!stream) return null;
              return <SavedWidget key={widget.id} widget={widget} stream={stream} online={deviceForStream(stream)?.status === "online"}
                deleting={deleteWidget.isPending && deleteWidget.variables?.widget_id === widget.id}
                onDelete={() => deleteWidget.mutate({ dashboard_id: dashboard.id, widget_id: widget.id })} />;
            })}
            {!!deleteWidget.error && <Text style={s.error}>{deleteWidget.error.message}</Text>}
            <Section title="Adicionar ao dashboard" />
            {streams.length === 0 && <Empty icon="pulse-outline" title="Sem datastreams ativos" text="Adicione datastreams aos dispositivos deste projeto para criar widgets." />}
            {streams.map((stream) => {
              const alreadyAdded = widgets.some((widget) => widget.datastream_id === stream.id);
              return <Card key={stream.id}>
                <Text style={s.h2}>{stream.name}</Text>
                <Text style={s.muted}>{stream.key} · {stream.data_type}{stream.unit ? ` · ${stream.unit}` : ""}</Text>
                {alreadyAdded ? <Text style={s.muted}>Já adicionado a este dashboard.</Text> : stream.data_type === "boolean" ?
                  <Button variant="soft" onPress={() => addWidget(stream, "switch")} disabled={createWidget.isPending}>Adicionar controlo</Button> :
                  <View style={{ flexDirection: "row", gap: 8 }}>
                    <View style={{ flex: 1 }}><Button variant="soft" onPress={() => addWidget(stream, "value")} disabled={createWidget.isPending}>Valor</Button></View>
                    <View style={{ flex: 1 }}><Button variant="outline" onPress={() => addWidget(stream, "chart")} disabled={createWidget.isPending}>Gráfico</Button></View>
                  </View>}
              </Card>;
            })}
            {!!createWidget.error && <Text style={s.error}>{createWidget.error.message}</Text>}
          </>}
        </>}
      </ScrollView>
      <BottomNav />
    </View>
  );
}
