import { View, Text, Image, Pressable } from 'react-native';
import { colors, radii, space } from '../theme/tokens';

export function SizeCard({ model, onPress }: { model: any; onPress?: () => void }) {
  return (
    <View style={{ gap: space[12] }}>
      <View style={{ position: 'relative' }}>
        <Image
          source={model.hero}
          style={{ width: '100%', height: 440, borderRadius: radii.card }}
          resizeMode="cover"
        />
        <View
          style={{
            position: 'absolute', left: 16, bottom: 16,
            paddingVertical: 8, paddingHorizontal: 12,
            borderRadius: radii.pill, borderWidth: 1, borderColor: '#E8E4DE',
            backgroundColor: 'rgba(255,255,255,0.88)'
          }}>
          <Text style={{ fontWeight: '600', fontSize: 12, color: '#4C4C50' }}>
            Confidence: High
          </Text>
        </View>
      </View>

      <Pressable
        style={{
          flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
          paddingVertical: 16, paddingHorizontal: 24, borderRadius: 24,
          backgroundColor: colors.petrol500, shadowOpacity: 0.2, shadowRadius: 8, shadowOffset: { width: 0, height: 8 }
        }}
        onPress={onPress}
      >
        <Text style={{ color: '#fff', fontWeight: '700' }}>
          Best Fit: {model.bestFit}
        </Text>
        <Text style={{ color: '#fff', fontSize: 18 }}>›</Text>
      </Pressable>
    </View>
  );
}
