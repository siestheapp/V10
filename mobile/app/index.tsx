import { View, Text, ScrollView, Image, Pressable } from 'react-native';

// inline tokens for now (or import from ../theme/tokens)
const colors = {
  ink900: '#0B0F14',
  ink700: '#121A22',
  petrol600: '#009090',
  petrol500: '#00A3A3',
  petrol400: '#16B5B5',
  petrol100: '#E0F7F7',
};
const radii = { card: 16, pill: 999 };
const space = { 12: 12, 16: 16, 24: 24 };

const mock = {
  hero: require('../assets/hero1.jpg'),
  bestFit: 'S',
  tips: ['Runs slightly narrow at the toe.', 'Material relaxes after first wear.'],
  shops: [{ label: 'Shop this in S' }, { label: 'See more colors' }],
};

export default function Home() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.ink900 }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: space[24], paddingBottom: 96 }}>
        <View style={{ paddingVertical: 8 }}>
          <Text style={{ fontSize: 32, fontWeight: '600', color: '#E7FFFF' }}>Freestyle</Text>
        </View>

        {/* Chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 6 }}>
          {['All', 'Tops', 'Jeans', 'Shoes'].map((label, i) => (
            <View
              key={i}
              style={{
                borderWidth: 1,
                borderColor: i === 0 ? colors.petrol500 : '#E8E4DE',
                backgroundColor: i === 0 ? colors.petrol100 : '#fff',
                paddingVertical: space[12],
                paddingHorizontal: space[16],
                borderRadius: radii.pill,
                marginRight: 12,
              }}
            >
              <Text
                style={{
                  color: i === 0 ? colors.petrol600 : '#0B0F14',
                  fontWeight: i === 0 ? '600' : '500',
                }}
              >
                {label}
              </Text>
            </View>
          ))}
        </ScrollView>

        {/* Card */}
        <View style={{ height: 12 }} />
        <View style={{ gap: space[12] }}>
          <View style={{ position: 'relative' }}>
            <Image
              source={mock.hero}
              style={{ width: '100%', height: 440, borderRadius: radii.card }}
              resizeMode="cover"
            />
            <View
              style={{
                position: 'absolute',
                left: 16,
                bottom: 16,
                paddingVertical: 8,
                paddingHorizontal: 12,
                borderRadius: radii.pill,
                borderWidth: 1,
                borderColor: '#E8E4DE',
                backgroundColor: 'rgba(255,255,255,0.88)',
              }}
            >
              <Text style={{ fontWeight: '600', fontSize: 12, color: '#4C4C50' }}>Confidence: High</Text>
            </View>
          </View>

          <Pressable
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingVertical: 16,
              paddingHorizontal: space[24],
              borderRadius: 24,
              backgroundColor: colors.petrol500,
            }}
          >
            <Text style={{ color: '#fff', fontWeight: '700' }}>Best Fit: {mock.bestFit}</Text>
            <Text style={{ color: '#fff', fontSize: 18 }}>›</Text>
          </Pressable>
        </View>

        {/* Tips */}
        {mock.tips.map((tip, i) => (
          <View
            key={i}
            style={{
              marginTop: 12,
              padding: 14,
              borderRadius: 12,
              backgroundColor: colors.petrol100,
              borderWidth: 1,
              borderColor: colors.petrol400,
            }}
          >
            <Text style={{ color: colors.ink700, fontSize: 13 }}>{tip}</Text>
          </View>
        ))}

        {/* Shop links */}
        <View
          style={{
            marginTop: 12,
            padding: 14,
            borderRadius: 12,
            backgroundColor: colors.petrol100,
            borderWidth: 1,
            borderColor: colors.petrol400,
          }}
        >
          <Text
            style={{ color: colors.ink700, fontSize: 14, fontWeight: '600', marginBottom: 8 }}
          >
            Where to buy
          </Text>
          {mock.shops.map((s, i) => (
            <Text key={i} style={{ color: colors.petrol600, marginTop: 6 }}>
              {s.label}
            </Text>
          ))}
        </View>
      </ScrollView>

      {/* Tab bar placeholder */}
      <View
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          paddingTop: 8,
          paddingBottom: 34,
          backgroundColor: colors.ink900,
          flexDirection: 'row',
          justifyContent: 'space-around',
        }}
      >
        <Text style={{ color: colors.petrol600, fontWeight: '600' }}>Home</Text>
        <Text style={{ color: '#8e8e93' }}>Explore</Text>
        <Text style={{ color: '#8e8e93' }}>Me</Text>
      </View>
    </View>
  );
}
