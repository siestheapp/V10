import { View, Text, TextInput, Pressable, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { supabase } from '../src/lib/supabase';

export default function AddItem() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleResolve() {
    if (!url.trim()) {
      Alert.alert('Error', 'Please enter a product URL');
      return;
    }

    setLoading(true);
    try {
      // Call Supabase RPC to resolve URL to variant
      const { data, error } = await supabase.rpc('api_resolve_by_url', { p_url: url.trim() });
      
      if (error) {
        Alert.alert('Error', error.message);
        return;
      }

      if (data && data.length > 0 && data[0].variant_id) {
        const variant = data[0];
        // Navigate to confirmation screen with variant data
        router.push({
          pathname: '/confirm-item',
          params: {
            variantId: variant.variant_id,
            brand: variant.brand,
            style: variant.style,
            imageUrl: variant.image_url || '',
            sourceUrl: url.trim(),
          },
        });
      } else {
        Alert.alert('Not Found', 'Could not find this product. Please try another URL or check that the URL is correct.');
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to resolve product URL');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1, backgroundColor: '#F7F9FB' }}
    >
      <View style={{ flex: 1, padding: 24, justifyContent: 'center' }}>
        <Text style={{ fontSize: 28, fontWeight: '700', color: '#1F1F1F', marginBottom: 8 }}>
          Add an Item
        </Text>
        <Text style={{ fontSize: 16, color: '#6F6F74', marginBottom: 32 }}>
          Paste a product URL from a brand website
        </Text>

        <TextInput
          value={url}
          onChangeText={setUrl}
          placeholder="https://..."
          placeholderTextColor="#999"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
          returnKeyType="go"
          onSubmitEditing={handleResolve}
          style={{
            backgroundColor: '#fff',
            borderWidth: 1,
            borderColor: '#E0E0E0',
            borderRadius: 12,
            paddingVertical: 14,
            paddingHorizontal: 16,
            fontSize: 16,
            color: '#1F1F1F',
            marginBottom: 16,
          }}
        />

        <Pressable
          onPress={handleResolve}
          disabled={loading || !url.trim()}
          style={{
            backgroundColor: loading || !url.trim() ? '#80D1D1' : '#00A3A3',
            paddingVertical: 14,
            paddingHorizontal: 18,
            borderRadius: 12,
            marginBottom: 12,
          }}
        >
          <Text style={{ textAlign: 'center', color: '#fff', fontWeight: '700' }}>
            {loading ? 'Finding product...' : 'Continue'}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.back()}
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
    </KeyboardAvoidingView>
  );
}

