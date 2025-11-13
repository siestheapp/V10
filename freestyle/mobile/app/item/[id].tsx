import { useLocalSearchParams, router } from 'expo-router';
import { View, Text, Image, Pressable, ScrollView } from 'react-native';
import { colors, radii, space } from '../../theme/tokens';
import { getItemById } from '../../features/mocks/common';

export default function ItemDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const item = getItemById(Number(id));

  if (!item) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: (colors as any).background ?? '#fff' }}>
        <Text style={{ color: '#111827' }}>Not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff' }}>
      <Image source={item.image} style={{ width: '100%', height: 320 }} resizeMode="cover" />
      <View style={{ padding: space[16], gap: space[12] }}>
        <Text style={{ fontSize: 24, fontWeight: '700', color: (colors as any).ink900 ?? '#111827' }}>{item.title}</Text>
        {!!item.subtitle && <Text style={{ color: '#6B7280' }}>{item.subtitle}</Text>}
        <View style={{ flexDirection: 'row', gap: space[12], marginTop: space[12] }}>
          <Pressable
            onPress={() => router.back()}
            style={{ backgroundColor: colors.petrol500, padding: space[12], borderRadius: radii.card }}
          >
            <Text style={{ color: '#fff', fontWeight: '700' }}>Back</Text>
          </Pressable>
          <Pressable
            onPress={() => router.push({ pathname: '/webview/shop', params: { url: item.shopUrl || 'https://example.com' } })}
            style={{ backgroundColor: '#fff', padding: space[12], borderRadius: radii.card, borderWidth: 1, borderColor: '#E5E7EB' }}
          >
            <Text style={{ color: colors.petrol500, fontWeight: '700' }}>Shop</Text>
          </Pressable>
        </View>
      </View>
    </ScrollView>
  );
}


