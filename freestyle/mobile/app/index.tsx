import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { supabase } from '../src/lib/supabase';
import Constants from 'expo-constants';

export default function Index() {
  const [ready, setReady] = useState(false);
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    (async () => {
      // 1) Check existing session
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setSignedIn(true);
        setReady(true);
        return;
      }

      // 2) Dev auto-login using embedded config
      const extra = (Constants.expoConfig?.extra ?? {}) as any;
      const devAuto = String(extra.EXPO_PUBLIC_DEV_AUTO_LOGIN ?? process.env.EXPO_PUBLIC_DEV_AUTO_LOGIN ?? '').toLowerCase() === 'true';
      const devEmail = String(extra.EXPO_PUBLIC_DEV_EMAIL ?? process.env.EXPO_PUBLIC_DEV_EMAIL ?? '');
      const devPass = String(extra.EXPO_PUBLIC_DEV_PASSWORD ?? process.env.EXPO_PUBLIC_DEV_PASSWORD ?? '');
      if (devAuto && devEmail && devPass) {
        try {
          const { data, error } = await supabase.auth.signInWithPassword({ email: devEmail, password: devPass });
          if (!error && data.user) {
            setSignedIn(true);
            setReady(true);
            return;
          }
        } catch {}
      }

      // 3) Fall back to start/sign-in
      setSignedIn(false);
      setReady(true);
    })();
  }, []);

  if (!ready) return null;
  return <Redirect href={signedIn ? '/(tabs)/home' : '/start'} />;
}
