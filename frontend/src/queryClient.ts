import { QueryCache, QueryClient } from "@tanstack/react-query";
import { ApiError } from "./api/client";
import { notify } from "./store";

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (query.meta?.suppressGlobalError === true) return;
      notify(error instanceof ApiError ? error.message : "Não foi possível carregar os dados.");
    },
  }),
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error instanceof ApiError && (error.status === 401 || error.status === 403 || error.status === 404)) return false;
        return failureCount < 2;
      },
    },
  },
});
