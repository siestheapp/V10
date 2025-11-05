import { useQuery } from "@tanstack/react-query";
import { FlatList, Image, Text, View } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from "../../lib/supabase";

type Row = {
  session_id: number;
  item_id: number | null;
  product_name: string | null;
  image_url: string | null;
  size_tried: string | null;
  fit_score: number | null;
  created_at: string | null;
};

async function fetchTryons(): Promise<Row[]> {
  const { data, error } = await supabase
    .from("v_try_on_history")
    .select("session_id, item_id, product_name, image_url, size_tried, fit_score, created_at")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return (data as Row[]) ?? [];
}

export default function TryonsScreen() {
  const { data = [] } = useQuery({ queryKey: ["tryons"], queryFn: fetchTryons });

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }} edges={['top']}>
      <FlatList
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 16 }}
        data={data}
        keyExtractor={(x) => String(x.item_id ?? x.session_id)}
        renderItem={({ item }) => (
          <View style={{ marginBottom: 12 }}>
            {!!item.image_url && (
              <Image source={{ uri: item.image_url }} style={{ height: 220, borderRadius: 12, backgroundColor: "#eee" }} />
            )}
            <Text style={{ fontWeight: "600", marginTop: 8 }}>{item.product_name ?? "Try-on"}</Text>
            {!!item.size_tried && <Text style={{ color: "#666" }}>Size tried: {item.size_tried}</Text>}
            {!!item.fit_score && <Text style={{ color: "#666" }}>Fit score: {item.fit_score}</Text>}
          </View>
        )}
        ListEmptyComponent={<Text style={{ padding: 24, color: "#666" }}>No try-ons yet.</Text>}
      />
    </SafeAreaView>
  );
}


