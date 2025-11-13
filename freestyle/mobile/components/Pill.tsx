import { View, Text, ViewStyle } from 'react-native';
import { colors, space } from '../theme/tokens';

export default function Pill({ children, style }: { children: string; style?: ViewStyle }) {
  return (
    <View style={[{ backgroundColor: '#E0F7F7', paddingHorizontal: space[12], paddingVertical: space[8], borderRadius: 999 }, style]}>
      <Text style={{ fontSize: 12, color: '#0B0F14' }}>{children}</Text>
    </View>
  );
}


