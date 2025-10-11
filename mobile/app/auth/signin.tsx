import { View, Text, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import { supabase } from '../../src/lib/supabase';
import { linkToDemoProfile } from '../../src/lib/auth';

// Required for proper browser session handling
WebBrowser.maybeCompleteAuthSession();

export default function SignIn() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

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

  async function onGoogle() {
    setLoading(true);
    try {
      // Use hard-coded redirect URI instead of makeRedirectUri for now
      const REDIRECT_TO = 'freestyle://auth/callback';

      console.log('Redirect URI:', REDIRECT_TO);
      console.log('Add this URL to Supabase Dashboard → Auth → URL Configuration → Redirect URLs');

      // Initiate OAuth flow
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: REDIRECT_TO,          // <— force deep link
          skipBrowserRedirect: false,
        }
      });

      if (error) {
        console.error('OAuth error:', error);
        Alert.alert('Error', error.message);
        return;
      }

      if (!data.url) {
        Alert.alert('Error', 'Failed to get OAuth URL');
        return;
      }

      // Open the OAuth URL in browser
      console.log('Opening OAuth URL:', data.url);
      const result = await WebBrowser.openAuthSessionAsync(
        data.url,
        REDIRECT_TO
      );

      console.log('OAuth result:', result);

      if (result.type === 'success') {
        // Extract the URL and let Supabase handle it
        const { url } = result;
        console.log('OAuth success, redirected to:', url);
      } else {
        console.log('OAuth cancelled or failed:', result);
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to sign in with Google');
      console.error('OAuth exception:', err);
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
          {loading ? 'Signing in...' : 'Continue with Google'}
        </Text>
      </Pressable>
    </View>
  );
}


