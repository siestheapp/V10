import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { IS_DEMO } from '../src/config';
import { demoBootstrap } from '../src/demo/demoStore';

export default function Layout() {
  useEffect(() => {
    if (IS_DEMO) {
      demoBootstrap().catch(() => {});
    }
  }, []);
  return <Stack screenOptions={{ headerShown: false }} />;
}
