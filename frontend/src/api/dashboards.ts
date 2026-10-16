import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export type Dashboard = {
  id: string;
  project_id: string;
  owner_id: string;
  name: string;
  description: string | null;
  layout: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type DashboardWidget = {
  id: string;
  dashboard_id: string;
  datastream_id: string;
  name: string;
  widget_type: "value" | "chart" | "switch";
  config: Record<string, unknown>;
  position: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

const dashboardsKey = (projectId?: string) => ["projects", projectId, "dashboards"];
const widgetsKey = (dashboardId?: string) => ["dashboards", dashboardId, "widgets"];

export function useProjectDashboards(projectId?: string) {
  return useQuery({
    queryKey: dashboardsKey(projectId),
    queryFn: () => api<Dashboard[]>(`/dashboards/projects/${projectId}`),
    enabled: !!projectId,
  });
}

export function useDashboardWidgets(dashboardId?: string) {
  return useQuery({
    queryKey: widgetsKey(dashboardId),
    queryFn: () => api<DashboardWidget[]>(`/dashboards/${dashboardId}/widgets`),
    enabled: !!dashboardId,
  });
}

export function useCreateDashboard() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { project_id: string; name: string; description?: string; layout?: Record<string, unknown> }) =>
      api<Dashboard>("/dashboards", { method: "POST", body: data }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: dashboardsKey(vars.project_id) }),
  });
}

export function useCreateDashboardWidget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { dashboard_id: string; datastream_id: string; name: string; widget_type: DashboardWidget["widget_type"] }) =>
      api<DashboardWidget>(`/dashboards/${vars.dashboard_id}/widgets`, {
        method: "POST",
        body: {
          datastream_id: vars.datastream_id,
          name: vars.name,
          widget_type: vars.widget_type,
          config: {},
          position: {},
        },
      }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: widgetsKey(vars.dashboard_id) }),
  });
}

export function useDeleteDashboardWidget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { dashboard_id: string; widget_id: string }) =>
      api<void>(`/dashboards/widgets/${vars.widget_id}`, { method: "DELETE" }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: widgetsKey(vars.dashboard_id) }),
  });
}
