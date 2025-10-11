import { router } from 'expo-router';
import { View, FlatList } from 'react-native';
import { colors, space } from '../../theme/tokens';
import Section from '../../components/Section';
import { SizeCard } from '../../components/SizeCard';
import { closetItems } from '../../features/mocks/closet';

export default function Closet() {
  return (
    <View style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff' }}>
      <Section title="Closet">
        {closetItems.length === 0 ? (
          <View style={{ paddingHorizontal: space[16], paddingVertical: space[12] }}>
            <View style={{ height: 120, borderRadius: 16, backgroundColor: '#F3F4F6' }} />
            <View style={{ height: 8 }} />
            <View style={{ height: 16, width: 160, backgroundColor: '#E5E7EB', borderRadius: 4 }} />
          </View>
        ) : (
          <FlatList
            data={closetItems}
            numColumns={2}
            keyExtractor={(i) => String(i.id)}
            columnWrapperStyle={{ gap: space[12], paddingHorizontal: space[16] }}
            contentContainerStyle={{ gap: space[12], paddingVertical: space[16] }}
            renderItem={({ item }) => (
              <SizeCard
                model={{ hero: item.image, bestFit: item.size }}
                onPress={() => router.push(`/item/${item.id}`)}
              />
            )}
          />
        )}
      </Section>
    </View>
  );
}


