import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export type AutomationRule = {
  id: string; project_id: string; datastream_id: string; owner_id: string;
  name: string; operator: "<" | ">" | "="; threshold: number; action: string;
  action_type: "notification" | "control_device"; target_datastream_id: string | null;
  action_value: unknown; is_active: boolean; cooldown_seconds: number; last_triggered_at: string | null;
};
export type CiaoNotification = {
  id: string; project_id: string; automation_id: string | null; datastream_id: string | null;
  title: string; message: string; level: string; read_at: string | null; created_at: string;
};

const rulesKey = (projectId?: string) => ["projects", projectId, "automations"];
export function useProjectAutomations(projectId?: string) {
  return useQuery({ queryKey: rulesKey(projectId), queryFn: () => api<AutomationRule[]>(`/automations/projects/${projectId}`), enabled: !!projectId });
}
export function useAllAutomations(projectIds: string[]) {
  const queries = useQueries({ queries: projectIds.map((id) => ({ queryKey: rulesKey(id), queryFn: () => api<AutomationRule[]>(`/automations/projects/${id}`) })) });
  return { data: queries.flatMap((q) => q.data ?? []), isLoading: queries.some((q) => q.isLoading), isError: queries.some((q) => q.isError) };
}
export function useCreateAutomation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { project_id: string; datastream_id: string; name: string; operator: AutomationRule["operator"]; threshold: number; action: string; action_type: AutomationRule["action_type"]; target_datastream_id?: string; action_value?: unknown; is_active: boolean; cooldown_seconds: number }) =>
      api<AutomationRule>("/automations", { method: "POST", body }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: rulesKey(vars.project_id) }),
  });
}
export function useUpdateAutomation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; project_id: string; is_active: boolean }) => api<AutomationRule>(`/automations/${vars.id}`, { method: "PATCH", body: { is_active: vars.is_active } }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: rulesKey(vars.project_id) }),
  });
}
export function useDeleteAutomation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; project_id: string }) => api<void>(`/automations/${vars.id}`, { method: "DELETE" }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: rulesKey(vars.project_id) }),
  });
}
export function useNotifications() {
  return useQuery({ queryKey: ["notifications"], queryFn: () => api<CiaoNotification[]>("/notifications") });
}
export function useMarkNotificationRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; read: boolean }) => api<CiaoNotification>(`/notifications/${vars.id}`, { method: "PATCH", body: { read: vars.read } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });
}
export function useMarkAllNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: () => api<void>("/notifications/read-all", { method: "POST" }), onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }) });
}
