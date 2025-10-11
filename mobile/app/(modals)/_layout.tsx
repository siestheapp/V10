import { Stack } from 'expo-router';

export default function ModalStack() {
  return (
    <Stack screenOptions={{ presentation: 'modal', headerTitle: '' }}>
      <Stack.Screen name="settings" options={{ title: 'Settings' }} />
      <Stack.Screen name="tips" options={{ title: 'Tips' }} />
    </Stack>
  );
}


