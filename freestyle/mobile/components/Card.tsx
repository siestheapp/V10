import { Pressable, View, Text, Image, ViewStyle } from 'react-native';
import { colors, radii, space } from '../theme/tokens';

type Props = {
  title: string;
  subtitle?: string;
  image: any;
  tags?: string[];
  ctaLabel?: string;
  onPress?: () => void;
  style?: ViewStyle;
  imageAspectRatio?: number;
};

export default function Card({ title, subtitle, image, tags, ctaLabel = 'Open', onPress, style, imageAspectRatio }: Props) {
  return (
    <Pressable
      onPress={onPress}
      style={[
        {
          backgroundColor: '#fff',
          borderRadius: radii.card,
          overflow: 'hidden',
          borderWidth: 1,
          borderColor: '#E5E7EB',
        },
        style,
      ]}
    >
      <Image source={image} style={{ width: '100%', height: imageAspectRatio ? 200 * imageAspectRatio : 160 }} resizeMode="cover" />
      <View style={{ padding: space[12] }}>
        <Text style={{ fontWeight: '700' }}>{title}</Text>
        {!!subtitle && <Text style={{ color: '#6B7280', marginTop: 2 }}>{subtitle}</Text>}
        {!!tags?.length && (
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: space[8], marginTop: space[8] }}>
            {tags.map(t => (
              <View key={t} style={{ backgroundColor: '#F3F4F6', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 999 }}>
                <Text style={{ fontSize: 12, color: '#374151' }}>{t}</Text>
              </View>
            ))}
          </View>
        )}
        <Text style={{ color: colors.petrol600, fontWeight: '600', marginTop: space[8] }}>{ctaLabel} →</Text>
      </View>
    </Pressable>
  );
}


