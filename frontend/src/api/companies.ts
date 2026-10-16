import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";

export type Company = { id: string; name: string; slug: string; description: string | null; owner_id: string };
export type CompanyMember = { id: string; company_id: string; user_id: string; role: string; user: { id: string; full_name: string; email: string } };

export function useCompanies() {
  return useQuery({ queryKey: ["companies"], queryFn: () => api<Company[]>("/companies/companies") });
}
export function useCompany(id: string | undefined) {
  return useQuery({
    queryKey: ["companies", id],
    queryFn: () => api<Company>(`/companies/companies/${id}`),
    enabled: !!id,
  });
}
export function useCompanyMembers(id: string | undefined) {
  return useQuery({
    queryKey: ["companies", id, "members"],
    queryFn: () => api<CompanyMember[]>(`/companies/companies/${id}/members`),
    enabled: !!id,
  });
}
export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { name: string; description?: string }) =>
      api<Company>("/companies/companies", { method: "POST", body: vars }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}
// Nota: o backend não tem DELETE /companies/companies/{id} - só remoção
// de membros. Não há forma de eliminar uma empresa pela API ainda.
