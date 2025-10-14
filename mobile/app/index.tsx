import { Redirect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';

export default function Index() {
  const [ready, setReady] = useState(false);
  const [signedIn, setSignedIn] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem('demo:user').then(v => {
      setSignedIn(!!v);
      setReady(true);
    });
  }, []);

  if (!ready) return null;
  return <Redirect href={signedIn ? '/(tabs)/home' : '/start'} />;
}
