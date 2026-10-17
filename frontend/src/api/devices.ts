import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import { useProjects } from "./projects";

export type Device = {
  id: string;
  project_id: string;
  uuid: string;
  serial: string | null;
  name: string;
  model: string | null;
  firmware_version: string | null;
  status: string;
  last_seen: string | null;
  is_active: boolean;
};
/** Só existe na resposta de criação - nunca mais é possível obtê-los de novo. */
export type DeviceWithSecrets = Device & { token: string; mqtt_username: string; mqtt_password: string };

// Handoff em memória (não vai para os route params nem é persistido) entre
// o ecrã de criação e o de provisionamento, que mostra os segredos uma
// única vez - tal como o backend só os devolve uma única vez.
let lastProvisioned: DeviceWithSecrets | null = null;
export const setLastProvisioned = (d: DeviceWithSecrets) => { lastProvisioned = d; };
export const takeLastProvisioned = (deviceId: string): DeviceWithSecrets | null => {
  if (lastProvisioned?.id !== deviceId) return null;
  const d = lastProvisioned;
  lastProvisioned = null;
  return d;
};

export function useProjectDevices(projectId: string | undefined) {
  return useQuery({
    queryKey: ["projects", projectId, "devices"],
    queryFn: () => api<Device[]>(`/devices/projects/${projectId}`),
    enabled: !!projectId,
  });
}

/** Não existe "listar todos os meus dispositivos" no backend - agrega por projeto. */
export function useAllDevices() {
  const projectsQuery = useProjects();
  const projectIds = projectsQuery.data?.map((p) => p.id) ?? [];
  const results = useQueries({
    queries: projectIds.map((id) => ({
      queryKey: ["projects", id, "devices"],
      queryFn: () => api<Device[]>(`/devices/projects/${id}`),
    })),
  });
  return {
    isLoading: projectsQuery.isLoading || results.some((r) => r.isLoading),
    isError: projectsQuery.isError || results.some((r) => r.isError),
    data: results.flatMap((r) => r.data ?? []),
  };
}

export function useDevice(id: string | undefined) {
  return useQuery({
    queryKey: ["devices", id],
    queryFn: () => api<Device>(`/devices/${id}`),
    enabled: !!id,
  });
}
export function useCreateDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { project_id: string; name: string; serial?: string; model?: string; firmware_version?: string }) =>
      api<DeviceWithSecrets>(`/devices/projects/${vars.project_id}`, {
        method: "POST",
        body: { name: vars.name, serial: vars.serial, model: vars.model, firmware_version: vars.firmware_version },
      }),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ["projects", vars.project_id, "devices"] });
    },
  });
}
export function useDeleteDevice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api<void>(`/devices/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ predicate: (q) => q.queryKey[0] === "projects" || q.queryKey[0] === "devices" }),
  });
}

export function useRotateDeviceCredentials() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api<DeviceWithSecrets>(`/devices/${id}/credentials/rotate`, { method: "POST" }),
    onSuccess: (credentials) => {
      setLastProvisioned(credentials);
      qc.invalidateQueries({ predicate: (q) => q.queryKey[0] === "projects" || q.queryKey[0] === "devices" });
    },
  });
}
