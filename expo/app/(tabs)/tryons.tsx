import { useEffect, useState } from 'react';
import { View, Text, RefreshControl, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Image } from 'expo-image';
import { supabase } from '../../lib/supabase';

type Row = { id: number; photo_url: string | null; created_at: string | null };

export default function TryOns() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    const { data, error } = await supabase
      .from('user_garment_photos')
      .select('id, photo_url, created_at')
      .order('id', { ascending: false })
      .limit(50);
    if (error) { console.log('TRYONS SELECT ERROR', error); setRows([]); }
    else setRows(data ?? []);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  if (!rows.length && !loading) {
    return <SafeAreaView style={{ flex:1, backgroundColor:'#fff' }} edges={['top']}>
      <View style={{ flex:1, alignItems:'center', justifyContent:'center' }}>
      <Text style={{ color:'#888' }}>No try-ons yet.</Text>
      </View>
    </SafeAreaView>;
  }

  return (
    <SafeAreaView style={{ flex:1, backgroundColor:'#fff' }} edges={['top']}>
    <ScrollView
      style={{ flex:1 }}
      contentInsetAdjustmentBehavior="automatic"
      contentContainerStyle={{ padding:12 }}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={load} />}
    >
      <Text style={{ color:'#666', marginBottom:8 }}>Loaded {rows.length} photos</Text>
      {rows.map(r => {
        return (
          <View key={r.id} style={{ marginBottom:12 }}>
            {r.photo_url ? (
              <Image
                source={{ uri: r.photo_url ?? '' }}
                style={{ width:'100%', height:220, borderRadius:12, backgroundColor:'#eee' }}
                contentFit="cover"
                transition={120}
                cachePolicy="memory-disk"
                onError={(e) => console.log('IMAGE ERROR', r.id, r.photo_url, e?.nativeEvent ?? e)}
              />
            ) : <Text style={{ color:'#999' }}>No URL on row {r.id}</Text>}
            {r.created_at ? <Text style={{ color:'#666', marginTop:6 }}>{new Date(r.created_at).toLocaleString()}</Text> : null}
          </View>
        );
      })}
    </ScrollView>
    </SafeAreaView>
  );
}
