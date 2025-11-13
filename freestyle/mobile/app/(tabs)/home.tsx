import { router } from 'expo-router';
import { View, Text, Image, Pressable, ScrollView, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, radii, space, typography } from '../../theme/tokens';
import { useEffect, useState, useCallback } from 'react';
import { supabase } from '../../src/lib/supabase';
import { DemoControls, useDemoTrigger } from '../../src/demo/DemoControls';

interface FeedItem {
  owner_username: string;
  variant_id: number;
  style_id: number;
  brand_name: string;
  style_name: string;
  shared_size: string;
  image_url: string | null;
  pill_text: string;
  matched_at: string;
}

// Hook to track userId across auth state changes
function useUserId() {
  const [userId, setUserId] = useState<string | null>(null);

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

  return userId;
}

// Extracted feed loading function
async function loadFeedData(userId: string): Promise<FeedItem[]> {
  const { data, error } = await supabase.rpc('api_feed', { p_user_id: userId });
  if (error) {
    console.error('Feed error:', error);
    throw error;
  }
  return data || [];
}

export default function Home() {
  const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { open, setOpen, registerTap } = useDemoTrigger();
  
  // Guard: track userId and only load feed when signed in
  const userId = useUserId();

  const loadFeed = useCallback(async (isRefresh = false) => {
    if (!userId) return; // Don't call until signed in

    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);

      const data = await loadFeedData(userId);
      setFeedItems(data);
    } catch (err) {
      console.error('Failed to load feed:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) return; // Don't call until signed in
    loadFeed();
  }, [userId, loadFeed]);
  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.background, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={colors.petrol500} />
        <Text style={{ marginTop: 12, color: colors.textSecondary }}>Loading your feed...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ paddingHorizontal: space[24], flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <Text onPress={registerTap} style={{ ...typography.h1, color: colors.text, marginTop: 6 }}>freestyle</Text>
        <Pressable
          onPress={() => router.push('/add-item')}
          style={{ backgroundColor: colors.petrol500, paddingVertical: 8, paddingHorizontal: 16, borderRadius: 20 }}
        >
          <Text style={{ color: '#fff', fontWeight: '700', fontSize: 14 }}>+ Add Item</Text>
        </Pressable>
      </View>

      <ScrollView 
        contentContainerStyle={{ paddingHorizontal: space[24], paddingBottom: 96 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => loadFeed(true)} />}
      >
        {feedItems.length === 0 ? (
          <View style={{ marginTop: 60, alignItems: 'center' }}>
            <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 8 }}>
              No matches yet
            </Text>
            <Text style={{ fontSize: 16, color: colors.textSecondary, textAlign: 'center', marginBottom: 24 }}>
              Add items to your closet to find size twins
            </Text>
            <Pressable
              onPress={() => router.push('/add-item')}
              style={{ backgroundColor: colors.petrol500, paddingVertical: 14, paddingHorizontal: 24, borderRadius: 12 }}
            >
              <Text style={{ color: '#fff', fontWeight: '700' }}>Add Your First Item</Text>
            </Pressable>
          </View>
        ) : (
          feedItems.map((item, index) => (
            <View 
              key={`${item.variant_id}-${item.owner_username}-${index}`}
              style={{ 
                backgroundColor: colors.surface, 
                borderWidth: 1, 
                borderColor: '#eee6', 
                borderRadius: radii.card, 
                overflow: 'hidden', 
                marginTop: 12 
              }}
            >
              {item.image_url && (
                <View style={{ position: 'relative' }}>
                  <Image source={{ uri: item.image_url }} style={{ width: '100%', height: 440 }} resizeMode="cover" />
                  <LinearGradient 
                    colors={[ 'rgba(255,255,255,0)', 'rgba(250,248,246,.56)', '#fff' ]} 
                    locations={[0, 0.48, 1]} 
                    style={{ position: 'absolute', left:0, right:0, bottom:0, height: '20%' }} 
                  />
                </View>
              )}

              <View style={{ padding: 14 }}>
                {/* Pill Text */}
                <View style={{ 
                  paddingVertical: 10, 
                  paddingHorizontal: 16, 
                  borderRadius: 20, 
                  backgroundColor: colors.petrol100,
                  marginBottom: 12
                }}>
                  <Text style={{ color: colors.petrol600, fontWeight: '600', fontSize: 14 }}>
                    {item.pill_text}
                  </Text>
                </View>

                {/* Brand and Style */}
                <Text style={{ fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 4 }}>
                  {item.brand_name}
                </Text>
                <Text style={{ fontSize: 16, color: colors.textSecondary, marginBottom: 12 }}>
                  {item.style_name}
                </Text>

                {/* Size */}
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  <Text style={{ fontSize: 14, color: colors.textSecondary }}>Size:</Text>
                  <Text style={{ fontSize: 16, fontWeight: '700', color: colors.petrol600 }}>
                    {item.shared_size}
                  </Text>
                </View>
              </View>
            </View>
          ))
        )}
      </ScrollView>
      <DemoControls open={open} onClose={() => setOpen(false)} />
    </SafeAreaView>
  );
}


