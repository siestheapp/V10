import { useInfiniteQuery } from '@tanstack/react-query';
import { supabase } from '../../lib/supabase';
import { View, Text, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FlashList } from '@shopify/flash-list';
import { Image } from 'expo-image';
import { Link } from 'expo-router';

type ClosetRow = {
id: number | string;
name?: string | null;
brand?: string | null;
image_url?: string | null; // rename later if your column differs
created_at?: string | null;
};

const PAGE = 50;

async function fetchPage({ pageParam = 0 }): Promise<ClosetRow[]> {
const from = pageParam * PAGE, to = from + PAGE - 1;
const { data, error } = await supabase
.from('user_garments')
.select('id,name,brand,image_url,created_at')
.order('created_at', { ascending: false })
.range(from, to);
if (error) throw error;
return data ?? [];
}

export default function Closet() {
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
queryKey: ['closet'],
queryFn: fetchPage,
initialPageParam: 0,
getNextPageParam: (last, pages) => (last.length === PAGE ? pages.length : undefined),
});

const items = (data?.pages || []).flat();

return (
<SafeAreaView style={{ flex: 1, backgroundColor: '#fff' }} edges={['top']}>
<View style={{ flex: 1, padding: 12 }}>
<Link href="/camera/capture" asChild>
<TouchableOpacity style={{ padding: 14, backgroundColor: '#111', borderRadius: 10, marginBottom: 12 }}>
<Text style={{ color: 'white', textAlign: 'center' }}>Log Try-On</Text>
</TouchableOpacity>
</Link>

  <FlashList
    data={items}
    estimatedItemSize={280}
    onEndReachedThreshold={0.6}
    onEndReached={() => hasNextPage && !isFetchingNextPage && fetchNextPage()}
    keyExtractor={(x) => String(x.id)}
    renderItem={({ item }) => (
      <View style={{ marginBottom: 12 }}>
        {item.image_url ? (
          <Image
            source={item.image_url}
            style={{ width: '100%', height: 220, borderRadius: 12, backgroundColor: '#eee' }}
            contentFit="cover"
            transition={150}
            cachePolicy="memory-disk"
          />
        ) : null}
        <Text style={{ marginTop: 6, fontWeight: '600' }}>{item.name ?? 'Untitled garment'}</Text>
        {item.brand ? <Text style={{ color: '#666' }}>{item.brand}</Text> : null}
      </View>
    )}
  />
</View>
</SafeAreaView>


);
}
