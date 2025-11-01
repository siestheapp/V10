import { View, Text, Pressable, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, space, typography } from '../../theme/tokens';
import Section from '../../components/Section';
import { profileMeasurements } from '../../features/mocks/iframe';
import { supabase } from '../../src/lib/supabase';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';

export default function Profile() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setEmail(session?.user?.email || null);
    });
  }, []);

  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) {
        Alert.alert('Error', error.message);
        return;
      }
      // Navigate to sign in
      router.replace('/auth/signin');
    } catch (err) {
      console.error('Sign out error:', err);
      Alert.alert('Error', 'Failed to sign out');
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.backgroundAlt }} contentContainerStyle={{ paddingBottom: 96 }}>
      <SafeAreaView style={{ paddingHorizontal: space[20] }}>
      
      {email && (
        <View style={{ marginBottom: 16, marginTop: 8 }}>
          <Text style={{ fontSize: 14, color: colors.textSecondary, marginBottom: 4 }}>Signed in as</Text>
          <Text style={{ fontSize: 16, color: colors.text, fontWeight: '600', marginBottom: 12 }}>{email}</Text>
          <Pressable
            onPress={handleSignOut}
            style={{
              backgroundColor: colors.petrol500,
              paddingVertical: 12,
              paddingHorizontal: 18,
              borderRadius: 12,
            }}
          >
            <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
              Sign Out & Clear Data
            </Text>
          </Pressable>
        </View>
      )}

      <Text style={{ ...typography.h2, color: colors.text, marginBottom: 8 }}>Profile Strength</Text>
      <View style={{ backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: '#E0F2FE', padding: 16, marginBottom: 8 }}>
        <View style={{ height: 6, backgroundColor: '#E5E7EB', borderRadius: 3, overflow: 'hidden' }}>
          <View style={{ height: '100%', width: '85%', backgroundColor: colors.petrol500, borderRadius: 3 }} />
        </View>
        <Text style={{ ...typography.subtle, marginTop: 6 }}>Add 2 more items to unlock premium fit insights</Text>
      </View>

      <Text style={{ ...typography.h2, color: colors.text, marginTop: 14, marginBottom: 8 }}>Measurements</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 12 }}>
        {profileMeasurements.map(m => (
          <Pressable key={m.label} style={{ padding: 14, backgroundColor: '#fff', borderRadius: 16, minWidth: 160, borderWidth: 1, borderColor: colors.border }}>
            <Text style={{ ...typography.subtle }}>{m.label}</Text>
            <Text style={{ ...typography.h2, color: colors.text }}>{m.value}</Text>
          </Pressable>
        ))}
      </ScrollView>
      </SafeAreaView>
    </ScrollView>
  );
}


