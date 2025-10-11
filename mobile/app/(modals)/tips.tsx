import { View, Text } from 'react-native';
import { colors, space } from '../../theme/tokens';

export default function TipsModal() {
  return (
    <View style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff', padding: space[16], gap: 8 }}>
      <Text style={{ fontSize: 20, fontWeight: '700', color: (colors as any).ink900 ?? '#111827', marginBottom: 8 }}>Tips</Text>
      <Text>- Use petrol500 for primary CTAs.</Text>
      <Text>- Use radius.card for surfaces; pill for chips.</Text>
      <Text>- Spacing rhythm: 16/20/24 as in mocks.</Text>
    </View>
  );
}


