import { View, Text, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useState } from 'react';
import { supabase } from '../../src/lib/supabase';

export default function SignIn() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function onGoogle() {
    setLoading(true);
    try {
      // Generate random username for demo
      const username = `user${Math.floor(Math.random() * 900) + 100}`;
      
      // Call Supabase RPC to create demo user
      const { data, error } = await supabase.rpc('api_signup', { p_username: username });
      
      if (error) {
        Alert.alert('Error', error.message);
        return;
      }

      if (data && data.length > 0) {
        const userId = data[0].id;
        const userName = data[0].username;
        
        // Store user info in AsyncStorage
        await AsyncStorage.setItem('demo:user', JSON.stringify({ id: userId, username: userName }));
        
        router.replace('/(tabs)/home');
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to sign up');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#F7F9FB', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <Text style={{ fontSize: 28, fontWeight: '700', color: '#1F1F1F', marginBottom: 16 }}>Welcome</Text>
      <Text style={{ color: '#6F6F74', marginBottom: 24 }}>Sign in to continue</Text>

      <Pressable 
        onPress={onGoogle} 
        disabled={loading}
        style={{ 
          backgroundColor: loading ? '#80D1D1' : '#00A3A3', 
          paddingVertical: 14, 
          paddingHorizontal: 18, 
          borderRadius: 12, 
          width: '100%' 
        }}
      >
        <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
          {loading ? 'Signing in...' : 'Continue with Google (demo)'}
        </Text>
      </Pressable>
    </View>
  );
}


