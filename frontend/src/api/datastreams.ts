import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import { useAllDevices } from "./devices";

export type Datastream = {
  id: string;
  device_id: string;
  name: string;
  key: string;
  data_type: "boolean" | "integer" | "float" | "string" | "json";
  unit: string | null;
  min_value: number | null;
  max_value: number | null;
  is_active: boolean;
};
export type DatastreamValue = { id: string; datastream_id: string; value: unknown; recorded_at: string };

export function useDeviceDatastreams(deviceId: string | undefined) {
  return useQuery({
    queryKey: ["devices", deviceId, "datastreams"],
    queryFn: () => api<Datastream[]>(`/datastreams/devices/${deviceId}`),
    enabled: !!deviceId,
  });
}
/** Não existe "listar todos os datastreams" no backend - agrega por dispositivo. Só usado onde é mesmo preciso escolher de entre todos (ex.: automações). */
export function useAllDatastreams() {
  const devicesQuery = useAllDevices();
  const deviceIds = devicesQuery.data.map((d) => d.id);
  const results = useQueries({
    queries: deviceIds.map((id) => ({
      queryKey: ["devices", id, "datastreams"],
      queryFn: () => api<Datastream[]>(`/datastreams/devices/${id}`),
    })),
  });
  return {
    isLoading: devicesQuery.isLoading || results.some((r) => r.isLoading),
    data: results.flatMap((r) => r.data ?? []),
  };
}

export function useDatastream(id: string | undefined) {
  return useQuery({
    queryKey: ["datastreams", id],
    queryFn: () => api<Datastream>(`/datastreams/${id}`),
    enabled: !!id,
  });
}
export function useLatestValue(datastreamId: string | undefined) {
  return useQuery({
    queryKey: ["datastreams", datastreamId, "latest"],
    queryFn: () => api<DatastreamValue>(`/datastreams/${datastreamId}/values/latest`),
    enabled: !!datastreamId,
    retry: false,
  });
}
export function useValueHistory(datastreamId: string | undefined, limit = 30) {
  return useQuery({
    queryKey: ["datastreams", datastreamId, "history", limit],
    queryFn: () => api<DatastreamValue[]>(`/datastreams/${datastreamId}/values?limit=${limit}`),
    enabled: !!datastreamId,
  });
}
export function useCreateDatastream() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: {
      device_id: string;
      name: string;
      key: string;
      data_type: Datastream["data_type"];
      unit?: string;
      min_value?: number;
      max_value?: number;
    }) =>
      api<Datastream>(`/datastreams/devices/${vars.device_id}`, {
        method: "POST",
        body: { name: vars.name, key: vars.key, data_type: vars.data_type, unit: vars.unit, min_value: vars.min_value, max_value: vars.max_value },
      }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: ["devices", vars.device_id, "datastreams"] }),
  });
}
export function useCreateValue() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { datastream_id: string; value: unknown }) =>
      api<DatastreamValue>(`/datastreams/${vars.datastream_id}/values`, { method: "POST", body: { value: vars.value } }),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ["datastreams", vars.datastream_id, "latest"] });
      qc.invalidateQueries({ queryKey: ["datastreams", vars.datastream_id, "history"] });
    },
  });
}
export function useDeleteDatastream() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; deviceId: string }) => api<void>(`/datastreams/${vars.id}`, { method: "DELETE" }),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: ["devices", vars.deviceId, "datastreams"] }),
  });
}
