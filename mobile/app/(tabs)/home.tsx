import { router } from 'expo-router';
import { View, Text, Image, Pressable, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, radii, space, typography } from '../../theme/tokens';
import { feed as mockFeed } from '../../features/mocks/iframe';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';
import { IS_DEMO } from '../../src/config';
import { DemoControls, useDemoTrigger } from '../../src/demo/DemoControls';

export default function Home() {
  const [item, setItem] = useState<any>(mockFeed[0]);
  useEffect(() => {
    if (!IS_DEMO) return;
    AsyncStorage.getItem('demo:feed').then(raw => {
      if (!raw) return;
      try {
        const arr = JSON.parse(raw);
        if (Array.isArray(arr) && arr[0]) setItem(arr[0]);
      } catch {}
    });
  }, []);
  const { open, setOpen, registerTap } = useDemoTrigger();
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ paddingHorizontal: space[24] }}>
        <Text onPress={registerTap} style={{ ...typography.h1, color: colors.text, marginTop: 6 }}>freestyle</Text>
      </View>

      <ScrollView contentContainerStyle={{ paddingHorizontal: space[24], paddingBottom: 96 }}>
        {item && (
          <View style={{ backgroundColor: colors.surface, borderWidth: 1, borderColor: '#eee6', borderRadius: radii.card, overflow: 'hidden', marginTop: 12 }}>
            <View style={{ position: 'relative' }}>
              <Image source={item.hero} style={{ width: '100%', height: 440 }} resizeMode="cover" />
              <LinearGradient colors={[ 'rgba(255,255,255,0)', 'rgba(250,248,246,.56)', '#fff' ]} locations={[0, 0.48, 1]} style={{ position: 'absolute', left:0, right:0, bottom:0, height: '20%' }} />
              <View style={{ position: 'absolute', left: 16, bottom: 16, paddingVertical: 6, paddingHorizontal: 10, borderRadius: radii.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: 'rgba(255,255,255,0.88)' }}>
                <Text style={{ fontWeight: '600', fontSize: 12, color: '#4C4C50' }}>Confidence: <Text style={{ color: colors.petrol600, fontWeight: '700' }}>High</Text></Text>
              </View>
            </View>

            <View style={{ padding: 14 }}>
              <Pressable
                onPress={() => router.push(`/item/${item.id}`)}
                style={{
                  flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
                  paddingVertical: 14, paddingHorizontal: 20, borderRadius: 24,
                  backgroundColor: colors.petrol500
                }}
              >
                <Text style={{ color: '#fff', fontWeight: '800', fontSize: 17 }}>Best Fit: {item.size}</Text>
                <View style={{ paddingVertical: 8, paddingHorizontal: 14, backgroundColor: 'rgba(255,255,255,.8)', borderRadius: 999, borderWidth: 1, borderColor: 'rgba(255,255,255,.95)' }}>
                  <Text style={{ color: colors.text, fontWeight: '600' }}>Fit details</Text>
                </View>
              </Pressable>

              <View style={{ height: 1, backgroundColor: 'rgba(0,0,0,.08)', marginVertical: 8 }} />

              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 6 }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  <Text style={{ fontSize: 12, letterSpacing: .3, color: '#555', fontWeight: '600' }}>{item.brand}</Text>
                  <Text style={{ fontWeight: '700', fontSize: 17, color: '#2d2d2d' }}>{item.price}</Text>
                </View>
                <Text style={{ fontSize: 14, color: '#4C4C50', fontWeight: '500' }}>Free returns</Text>
              </View>

              <View style={{ marginTop: 12, paddingHorizontal: 2 }}>
                <Pressable
                  onPress={() => router.push({ pathname: '/webview/shop', params: { url: item.shopUrl } })}
                  style={{ alignSelf: 'center', width: '100%', minHeight: 44, padding: 12, borderRadius: 12, borderWidth: 1, borderColor: colors.petrol400, backgroundColor: '#fff' }}
                >
                  <Text style={{ textAlign: 'center', color: colors.petrol600, fontWeight: '700' }}>Shop {item.size}</Text>
                </Pressable>
              </View>
            </View>
          </View>
        )}
      </ScrollView>
      <DemoControls open={open} onClose={() => setOpen(false)} />
    </SafeAreaView>
  );
}


