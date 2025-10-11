import { router } from 'expo-router';
import { View, Text, Image, Pressable, FlatList, Platform } from 'react-native';
import { colors, radii, space, typography } from '../../theme/tokens';
import { Chip } from '../../components/Chip';
import Card from '../../components/Card';
import Section from '../../components/Section';
import { useMemo, useState } from 'react';
import { homeFeed, chips } from '../../features/mocks/home';
import { WebPhoneFrame } from '../../components/WebPhoneFrame';

function Body() {
  const [active, setActive] = useState<string>('All');
  const data = useMemo(
    () => (active === 'All' ? homeFeed : homeFeed.filter(i => i.tags?.includes(active))),
    [active]
  );

  return (
    <View style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff' }}>
      <View style={{ paddingHorizontal: space[16], paddingTop: space[16], paddingBottom: space[8] }}>
        <Text style={{ fontSize: 32, fontWeight: '700', color: (colors as any).petrol500 }}>Freestyle</Text>
      </View>

      <FlatList
        horizontal
        data={chips}
        keyExtractor={c => c}
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingHorizontal: space[16], gap: space[12], paddingBottom: space[8] }}
        renderItem={({ item }) => (
          <Chip label={item} active={active === item} onPress={() => setActive(item)} />
        )}
      />

      {!!data[0] && (
        <Pressable
          onPress={() => router.push(`/item/${data[0]?.id}`)}
          style={{
            margin: space[16],
            borderRadius: radii.card,
            overflow: 'hidden',
            backgroundColor: (colors as any).surface ?? '#fff',
          }}
        >
          <Image source={require('../../assets/hero1.jpg')} style={{ width: '100%', height: 200 }} resizeMode="cover" />
        </Pressable>
      )}

      <Section title="Featured">
        {data.length === 0 ? (
          <View style={{ paddingHorizontal: space[16], paddingVertical: space[12] }}>
            <Text style={{ color: '#6B7280' }}>No items yet.</Text>
          </View>
        ) : (
          <FlatList
            data={data}
            keyExtractor={(it) => String(it.id)}
            contentContainerStyle={{ padding: space[16], gap: space[12] }}
            renderItem={({ item }) => (
              <Card
                title={item.title}
                subtitle={item.subtitle}
                image={item.image}
                tags={item.tags}
                ctaLabel="View"
                onPress={() => router.push(`/item/${item.id}`)}
              />
            )}
          />
        )}
      </Section>
    </View>
  );
}

export default function Home() {
  if (Platform.OS === 'web') {
    return <WebPhoneFrame><Body /></WebPhoneFrame>;
  }
  return <Body />;
}


