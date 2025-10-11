import { View, Text, ScrollView } from 'react-native';
import { mockSizeTwin } from '../features/mocks/sizeTwin';
import { SizeCard } from '../components/SizeCard';
import { Chip } from '../components/Chip';
import { colors, space } from '../theme/tokens';
// If you installed expo-linear-gradient, you can uncomment this for a proper sheen:
// import { LinearGradient } from 'expo-linear-gradient';

export default function Home() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.ink900 }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: space[24], paddingBottom: 96 }}>
        {/* Header */}
        <View style={{ paddingVertical: 8 }}>
          {/* Simple solid as a fallback. Replace with gradient for brand sheen if desired. */}
          <Text style={{ fontSize: 32, fontWeight: '600', color: '#E7FFFF' }}>Freestyle</Text>
        </View>

        {/* Chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 6 }}>
          <Chip label="All" active />
          <Chip label="Tops" />
          <Chip label="Jeans" />
          <Chip label="Shoes" />
        </ScrollView>

        {/* Main card */}
        <View style={{ height: 12 }} />
        <SizeCard model={mockSizeTwin} />

        {/* Tips */}
        {mockSizeTwin.tips.map((tip, i) => (
          <View key={i} style={{
            marginTop: 12, padding: 14, borderRadius: 12,
            backgroundColor: colors.petrol100, borderWidth: 1, borderColor: colors.petrol400
          }}>
            <Text style={{ color: colors.ink700, fontSize: 13 }}>{tip}</Text>
          </View>
        ))}

        {/* Shop links */}
        <View style={{ marginTop: 12, padding: 14, borderRadius: 12,
          backgroundColor: colors.petrol100, borderWidth: 1, borderColor: colors.petrol400 }}>
          <Text style={{ color: colors.ink700, fontSize: 14, fontWeight: '600', marginBottom: 8 }}>Where to buy</Text>
          {mockSizeTwin.shops.map((s, i) => (
            <Text key={i} style={{ color: colors.petrol600, marginTop: 6 }}>{s.label}</Text>
          ))}
        </View>
      </ScrollView>

      {/* Tab bar placeholder */}
      <View style={{
        position: 'absolute', left: 0, right: 0, bottom: 0,
        paddingTop: 8, paddingBottom: 34, backgroundColor: colors.ink900,
        flexDirection: 'row', justifyContent: 'space-around'
      }}>
        <Text style={{ color: colors.petrol600, fontWeight: '600' }}>Home</Text>
        <Text style={{ color: '#8e8e93' }}>Explore</Text>
        <Text style={{ color: '#8e8e93' }}>Me</Text>
      </View>
    </View>
  );
}
