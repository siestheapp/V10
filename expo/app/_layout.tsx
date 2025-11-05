import { Stack, Tabs } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="index" options={{ title: 'Closet' }} />
      <Tabs.Screen name="tryons" options={{ title: 'Try-ons' }} />
      <Tabs.Screen name="scan" options={{ title: 'Scan' }} />
    </Tabs>
  );
}

export default function Root() {
  const [qc] = useState(() => new QueryClient());
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={qc}>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
