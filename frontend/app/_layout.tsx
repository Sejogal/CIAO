import { useEffect } from "react";
import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toast } from "@/ui";
import { queryClient } from "@/queryClient";
import { loadAuthFromStorage } from "@/api/client";
import { actions } from "@/store";

export default function Layout() {
  useEffect(() => {
    loadAuthFromStorage().then(({ apiUrl, loggedIn }) => actions.setAuthReady(apiUrl, loggedIn));
  }, []);
  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false, animation: "slide_from_right" }} />
        <Toast />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
