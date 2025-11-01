import { Text, Pressable } from 'react-native';
import { colors, radii, space } from '../theme/tokens';

export function Chip({ label, active=false, onPress }: { label: string; active?: boolean; onPress?: () => void }) {
  return (
    <Pressable
      onPress={onPress}
      style={{
        borderWidth: 1,
        borderColor: active ? colors.petrol500 : '#E8E4DE',
        backgroundColor: active ? colors.petrol100 : '#fff',
        paddingVertical: space[12], paddingHorizontal: space[16],
        borderRadius: radii.pill, marginRight: 12
      }}
    >
      <Text style={{ color: active ? colors.petrol600 : colors.ink900, fontWeight: active ? '600' : '500' }}>
        {label}
      </Text>
    </Pressable>
  );
}
