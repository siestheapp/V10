import { useEffect } from 'react';
import { View, Text } from 'react-native';
import { useRouter } from 'expo-router';

export default function Start() {
  const router = useRouter();
  useEffect(() => {
    const t = setTimeout(() => {
      router.replace('/auth/signin');
    }, 900);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <View style={{ flex: 1, backgroundColor: '#F7F9FB', alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 32, fontWeight: '700', letterSpacing: -0.2, color: '#00A3A3' }}>freestyle</Text>
    </View>
  );
}


