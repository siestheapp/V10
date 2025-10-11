import { router } from 'expo-router';
import { View, Text, FlatList, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, radii, space, typography } from '../../theme/tokens';
import { closet as mockCloset } from '../../features/mocks/iframe';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';
import { IS_DEMO } from '../../src/config';

export default function Closet() {
  const [data, setData] = useState<any[]>(mockCloset);
  useEffect(() => {
    AsyncStorage.getItem('demo:closet').then(raw => {
      try {
        const arr = raw ? JSON.parse(raw) : null;
        if (Array.isArray(arr)) setData(arr);
      } catch {}
    });
  }, []);
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ paddingHorizontal: space[24] }}>
        <Text style={{ ...typography.h1, color: colors.petrol500 }}>freestyle</Text>
      </View>
      <Text style={{ ...typography.h2, color: colors.text, paddingHorizontal: space[24], marginTop: 6 }}>Your Closet</Text>
      <FlatList
        data={data}
        numColumns={2}
        keyExtractor={(i) => String(i.id)}
        columnWrapperStyle={{ gap: 12, paddingHorizontal: space[24] }}
        contentContainerStyle={{ gap: 12, paddingVertical: space[16], paddingBottom: 96 }}
        renderItem={({ item }) => (
          <View style={{ flex: 1, borderRadius: radii.card, overflow: 'hidden', backgroundColor: '#f8f8fb', borderWidth: 1, borderColor: '#eee6' }}>
            <View style={{ position: 'relative' }}>
              <Image source={item.hero} style={{ width: '100%', height: 400 }} resizeMode="cover" />
              <LinearGradient colors={['transparent','rgba(0,0,0,.55)']} style={{ position: 'absolute', left:0,right:0,bottom:0, height: 120 }} />
              <View style={{ position: 'absolute', top: 10, left: 10, paddingVertical: 6, paddingHorizontal: 10, backgroundColor: 'rgba(0,0,0,.45)', borderRadius: 999 }}>
                <Text style={{ color: '#fff', fontWeight: '700', fontSize: 12 }}>{item.size}</Text>
              </View>
              <View style={{ position: 'absolute', left: 10, right: 10, bottom: 10 }}>
                <Text style={{ fontWeight: '700', fontSize: 11, color: '#fff', opacity: .95 }}>{item.brand}</Text>
                <Text style={{ fontWeight: '600', fontSize: 14, color: '#fff', marginTop: 2 }}>{item.name}</Text>
              </View>
            </View>
          </View>
        )}
      />
    </SafeAreaView>
  );
}


