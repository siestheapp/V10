import { View, Text } from 'react-native';
import { colors, space } from '../theme/tokens';

export default function Section({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <View style={{ marginTop: space[8] }}>
      <Text style={{ fontSize: 18, fontWeight: '700', color: colors.petrol500, paddingHorizontal: space[16], marginBottom: 4 }}>
        {title}
      </Text>
      {subtitle && (
        <Text style={{ fontSize: 12, color: '#6B7280', paddingHorizontal: space[16], marginBottom: 8 }}>
          {subtitle}
        </Text>
      )}
      {children}
    </View>
  );
}


