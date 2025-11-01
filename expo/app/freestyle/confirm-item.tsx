import { View, Text, Pressable, Alert, Image, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { supabase } from '../src/lib/supabase';

const SIZES = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL'];

export default function ConfirmItem() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { variantId, brand, style, imageUrl, sourceUrl } = params as {
    variantId: string;
    brand: string;
    style: string;
    imageUrl: string;
    sourceUrl: string;
  };

  async function handleClaim() {
    if (!selectedSize) {
      Alert.alert('Select Size', 'Please select a size');
      return;
    }

    setLoading(true);
    try {
      // Get real auth session
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) {
        Alert.alert('Error', 'User not found. Please sign in again.');
        router.replace('/auth/signin');
        return;
      }

      // Call Supabase RPC to claim ownership with real user ID
      const { data, error } = await supabase.rpc('api_claim', {
        p_user_id: session.user.id,
        p_variant_id: variantId, // Keep as string, Supabase will convert to bigint
        p_size_label: selectedSize,
        p_url: sourceUrl,
      });

      if (error) {
        Alert.alert('Error', error.message);
        return;
      }

      // Success - navigate to home
      Alert.alert('Success', 'Item added to your closet!', [
        {
          text: 'OK',
          onPress: () => router.replace('/(tabs)/home'),
        },
      ]);
    } catch (err) {
      Alert.alert('Error', 'Failed to add item');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#F7F9FB' }}>
      <View style={{ padding: 24 }}>
        <Text style={{ fontSize: 28, fontWeight: '700', color: '#1F1F1F', marginBottom: 8 }}>
          Confirm Item
        </Text>
        <Text style={{ fontSize: 16, color: '#6F6F74', marginBottom: 24 }}>
          Select your size to add this to your closet
        </Text>

        {/* Product Info */}
        <View style={{ backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 24 }}>
          {imageUrl && (
            <Image
              source={{ uri: imageUrl }}
              style={{ width: '100%', height: 200, borderRadius: 12, marginBottom: 16 }}
              resizeMode="cover"
            />
          )}
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#1F1F1F', marginBottom: 4 }}>
            {brand}
          </Text>
          <Text style={{ fontSize: 16, color: '#6F6F74' }}>
            {style}
          </Text>
        </View>

        {/* Size Selector */}
        <Text style={{ fontSize: 18, fontWeight: '700', color: '#1F1F1F', marginBottom: 12 }}>
          Select Size
        </Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 32 }}>
          {SIZES.map((size) => (
            <Pressable
              key={size}
              onPress={() => setSelectedSize(size)}
              style={{
                paddingVertical: 12,
                paddingHorizontal: 20,
                borderRadius: 12,
                borderWidth: 2,
                borderColor: selectedSize === size ? '#00A3A3' : '#E0E0E0',
                backgroundColor: selectedSize === size ? '#E6F7F7' : '#fff',
              }}
            >
              <Text
                style={{
                  fontSize: 16,
                  fontWeight: '600',
                  color: selectedSize === size ? '#00A3A3' : '#6F6F74',
                }}
              >
                {size}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* Action Buttons */}
        <Pressable
          onPress={handleClaim}
          disabled={loading || !selectedSize}
          style={{
            backgroundColor: loading || !selectedSize ? '#80D1D1' : '#00A3A3',
            paddingVertical: 14,
            paddingHorizontal: 18,
            borderRadius: 12,
            marginBottom: 12,
          }}
        >
          <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
            {loading ? 'Adding...' : 'Add to Closet'}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.back()}
          disabled={loading}
          style={{
            paddingVertical: 14,
            paddingHorizontal: 18,
          }}
        >
          <Text style={{ textAlign: 'center', color: '#6F6F74', fontWeight: '600' }}>
            Cancel
          </Text>
        </Pressable>
      </View>
    </ScrollView>
  );
}

