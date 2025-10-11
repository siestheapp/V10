import { View, Text, Pressable, ScrollView } from 'react-native';
import { colors, space, typography } from '../../theme/tokens';
import Section from '../../components/Section';
import { profileMeasurements } from '../../features/mocks/iframe';

export default function Profile() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: colors.backgroundAlt }} contentContainerStyle={{ padding: space[20], paddingBottom: 96 }}>
      <Text style={{ ...typography.h2, color: colors.text, marginBottom: 8 }}>Profile Strength</Text>
      <View style={{ backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: '#E0F2FE', padding: 16, marginBottom: 8 }}>
        <View style={{ height: 6, backgroundColor: '#E5E7EB', borderRadius: 3, overflow: 'hidden' }}>
          <View style={{ height: '100%', width: '85%', backgroundColor: colors.petrol500, borderRadius: 3 }} />
        </View>
        <Text style={{ ...typography.subtle, marginTop: 6 }}>Add 2 more items to unlock premium fit insights</Text>
      </View>

      <Text style={{ ...typography.h2, color: colors.text, marginTop: 14, marginBottom: 8 }}>Measurements</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 12 }}>
        {profileMeasurements.map(m => (
          <Pressable key={m.label} style={{ padding: 14, backgroundColor: '#fff', borderRadius: 16, minWidth: 160, borderWidth: 1, borderColor: colors.border }}>
            <Text style={{ ...typography.subtle }}>{m.label}</Text>
            <Text style={{ ...typography.h2, color: colors.text }}>{m.value}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </ScrollView>
  );
}


