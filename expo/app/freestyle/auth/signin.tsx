import { View, Text, Pressable, Alert, TextInput } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { supabase } from '../../src/lib/supabase';
import { linkToDemoProfile } from '../../src/lib/auth';

export default function SignIn() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Listen for auth state changes
  useEffect(() => {
    // Check if user is already signed in
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        // User is already signed in, navigate to home
        router.replace('/(tabs)/home');
      }
    });

    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth event:', event);
        
        if (event === 'SIGNED_IN' && session?.user) {
          // Link to demo profile
          await linkToDemoProfile(session.user);
          router.replace('/(tabs)/home');
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  async function onSignInEmailPassword() {
    if (!email || !password) {
      Alert.alert('Missing info', 'Please enter email and password');
      return;
    }
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        Alert.alert('Sign in failed', error.message);
        return;
      }
      if (data.user) {
        await linkToDemoProfile(data.user);
        router.replace('/(tabs)/home');
      }
    } catch (err) {
      console.error('Sign in error:', err);
      Alert.alert('Error', 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  }

  async function onSignUpEmailPassword() {
    if (!email || !password) {
      Alert.alert('Missing info', 'Please enter email and password');
      return;
    }
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) {
        Alert.alert('Sign up failed', error.message);
        return;
      }
      // If email confirmation is required, there may be no immediate session
      if (data.user && data.session) {
        await linkToDemoProfile(data.user);
        router.replace('/(tabs)/home');
      } else {
        Alert.alert('Check your email', 'We sent you a confirmation link to complete sign up.');
      }
    } catch (err) {
      console.error('Sign up error:', err);
      Alert.alert('Error', 'Failed to create account');
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#F7F9FB', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <Text style={{ fontSize: 28, fontWeight: '700', color: '#1F1F1F', marginBottom: 16 }}>Welcome</Text>
      <Text style={{ color: '#6F6F74', marginBottom: 16 }}>Sign in to continue</Text>

      <View style={{ width: '100%', gap: 12 }}>
        <TextInput
          placeholder="Email"
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
          style={{ backgroundColor: '#fff', borderColor: '#E5E7EB', borderWidth: 1, borderRadius: 12, padding: 12 }}
        />
        <TextInput
          placeholder="Password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          style={{ backgroundColor: '#fff', borderColor: '#E5E7EB', borderWidth: 1, borderRadius: 12, padding: 12 }}
        />

        <Pressable
          onPress={onSignInEmailPassword}
          disabled={loading}
          style={{ backgroundColor: loading ? '#80D1D1' : '#00A3A3', paddingVertical: 14, paddingHorizontal: 18, borderRadius: 12 }}
        >
          <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
            {loading ? 'Signing in...' : 'Sign in'}
          </Text>
        </Pressable>

        <Pressable
          onPress={onSignUpEmailPassword}
          disabled={loading}
          style={{ backgroundColor: '#111827', paddingVertical: 14, paddingHorizontal: 18, borderRadius: 12 }}
        >
          <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
            {loading ? 'Creating...' : 'Create account'}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}


