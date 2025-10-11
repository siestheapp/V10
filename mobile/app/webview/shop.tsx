import { useLocalSearchParams } from 'expo-router';
import { View, Text, Pressable, Linking, Alert } from 'react-native';
import { colors, space } from '../../theme/tokens';

export default function ShopProxy() {
  const { url } = useLocalSearchParams<{ url?: string }>();

  const open = async () => {
    if (!url) return Alert.alert('Missing URL');
    const supported = await Linking.canOpenURL(url);
    if (supported) Linking.openURL(url);
    else Alert.alert('Cannot open link', url);
  };

  return (
    <View style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff', padding: space[16], gap: space[12] }}>
      <Text style={{ fontSize: 20, fontWeight: '700', color: (colors as any).ink900 ?? '#111827' }}>Shop</Text>
      <Text>We’ll open this in your browser:</Text>
      <Text style={{ color: '#6B7280' }}>{url}</Text>
      <Pressable onPress={open} style={{ backgroundColor: '#00A3A3', padding: space[12], borderRadius: 12 }}>
        <Text style={{ color: '#fff', fontWeight: '700' }}>Open</Text>
      </Pressable>
    </View>
  );
}


