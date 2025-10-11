import { View, Text, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { demoSignUp } from '../../src/demo/demoStore';

export default function SignIn() {
  const router = useRouter();

  async function onGoogle() {
    await demoSignUp('alexis@example.com', 'demo');
    router.replace('/(tabs)/home');
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#F7F9FB', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <Text style={{ fontSize: 28, fontWeight: '700', color: '#1F1F1F', marginBottom: 16 }}>Welcome</Text>
      <Text style={{ color: '#6F6F74', marginBottom: 24 }}>Sign in to continue</Text>

      <Pressable onPress={onGoogle} style={{ backgroundColor: '#00A3A3', paddingVertical: 14, paddingHorizontal: 18, borderRadius: 12, width: '100%' }}>
        <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>Continue with Google (demo)</Text>
      </Pressable>
    </View>
  );
}


