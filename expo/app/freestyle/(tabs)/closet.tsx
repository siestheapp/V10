import { router } from 'expo-router';
import { View, Text, FlatList, Image, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, radii, space, typography } from '../../theme/tokens';
import { useEffect, useState } from 'react';
import { supabase } from '../../src/lib/supabase';

interface ClosetItem {
  id: number;
  variant_id: number;
  size: string;
  brand_name: string;
  style_name: string;
  image_url: string | null;
}

export default function Closet() {
  const [data, setData] = useState<ClosetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);

  // Get user ID
  useEffect(() => {
    const init = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUserId(session?.user?.id ?? null);
    };
    const sub = supabase.auth.onAuthStateChange((_e, s) => {
      setUserId(s?.user?.id ?? null);
    });
    init();
    return () => sub.data.subscription.unsubscribe();
  }, []);

  // Load closet items
  useEffect(() => {
    if (!userId) return;

    const loadCloset = async () => {
      try {
        setLoading(true);
        const { data: items, error } = await supabase
          .from('user_closet')
          .select(`
            id,
            variant_id,
            size,
            variant:variant_id (
              style:style_id (
                brand:brand_id (name),
                name
              )
            )
          `)
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        if (error) {
          console.error('Error loading closet:', error);
          return;
        }

        // Transform data
        const transformed = (items || []).map((item: any) => ({
          id: item.id,
          variant_id: item.variant_id,
          size: item.size,
          brand_name: item.variant?.style?.brand?.name || 'Unknown',
          style_name: item.variant?.style?.name || 'Unknown',
          image_url: null, // TODO: Add image lookup
        }));

        setData(transformed);
      } catch (err) {
        console.error('Failed to load closet:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCloset();
  }, [userId]);

  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={colors.petrol500} />
        <Text style={{ marginTop: 12, color: colors.textSecondary }}>Loading your closet...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ paddingHorizontal: space[24] }}>
        <Text style={{ ...typography.h1, color: colors.petrol500 }}>freestyle</Text>
      </View>
      <Text style={{ ...typography.h2, color: colors.text, paddingHorizontal: space[24], marginTop: 6 }}>Your Closet</Text>
      
      {data.length === 0 ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: space[24] }}>
          <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 8 }}>
            Your closet is empty
          </Text>
          <Text style={{ fontSize: 16, color: colors.textSecondary, textAlign: 'center' }}>
            Add items to see them here
          </Text>
        </View>
      ) : (
        <FlatList
          data={data}
          numColumns={2}
          keyExtractor={(i) => String(i.id)}
          columnWrapperStyle={{ gap: 12, paddingHorizontal: space[24] }}
          contentContainerStyle={{ gap: 12, paddingVertical: space[16], paddingBottom: 96 }}
          renderItem={({ item }) => (
            <View style={{ flex: 1, borderRadius: radii.card, overflow: 'hidden', backgroundColor: '#f8f8fb', borderWidth: 1, borderColor: '#eee6' }}>
              <View style={{ padding: 16, minHeight: 150 }}>
                <View style={{ marginBottom: 8 }}>
                  <Text style={{ color: colors.petrol600, fontWeight: '700', fontSize: 14 }}>{item.size}</Text>
                </View>
                <Text style={{ fontWeight: '700', fontSize: 12, color: colors.textSecondary }}>{item.brand_name}</Text>
                <Text style={{ fontWeight: '600', fontSize: 14, color: colors.text, marginTop: 4 }}>{item.style_name}</Text>
              </View>
            </View>
          )}
        />
      )}
    </SafeAreaView>
  );
}


