import { View, Text, Pressable, ScrollView, Alert } from 'react-native';
import { colors, space } from '../../theme/tokens';
import Section from '../../components/Section';

export default function Profile() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff' }} contentContainerStyle={{ padding: space[16] }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: space[16], justifyContent: 'space-between' }}>
        <Text style={{ fontSize: 20, fontWeight: '700', color: (colors as any).ink900 ?? '#111827' }}>Fit Profile</Text>
        <Pressable onPress={() => Alert.alert('Settings')} style={{ paddingHorizontal: 12, paddingVertical: 8, backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: '#E5E7EB' }}>
          <Text>Settings</Text>
        </Pressable>
      </View>

      <Section title="Measurements">
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 12, paddingHorizontal: space[16] }}>
          {[{label:'Chest',value:'—'},{label:'Waist',value:'—'},{label:'Inseam',value:'—'}].map(m => (
            <Pressable key={m.label} onPress={() => Alert.alert(m.label, m.value)} style={{ padding: 14, backgroundColor: '#fff', borderRadius: 16, minWidth: 160, borderWidth: 1, borderColor: '#E5E7EB' }}>
              <Text style={{ color: '#6B7280', fontSize: 12 }}>{m.label}</Text>
              <Text style={{ fontSize: 18, fontWeight: '700', color: (colors as any).ink900 ?? '#111827' }}>{m.value}</Text>
            </Pressable>
          ))}
        </ScrollView>
      </Section>
    </ScrollView>
  );
}


