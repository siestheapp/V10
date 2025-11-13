import { useQuery } from "@tanstack/react-query";
import { FlatList, Image, Text, View } from "react-native";
import { supabase } from "../../lib/supabase";

type ClosetRow = {
  user_garment_id: number;
  garment_id: number | null;
  product_name: string | null;
  product_url: string | null;
  image_url: string | null;
  primary_photo_url: string | null;
  created_at: string | null;
};

async function fetchCloset(): Promise<ClosetRow[]> {
  const { data, error } = await supabase
    .from("v_user_closet")
    .select("user_garment_id, garment_id, product_name, product_url, image_url, primary_photo_url, created_at")
    .order("created_at", { ascending: false });
  if (error) throw error;
  return (data as ClosetRow[]) ?? [];
}

export default function ClosetScreen() {
  const { data = [] } = useQuery({ queryKey: ["closet"], queryFn: fetchCloset });

  return (
    <FlatList
      style={{ flex: 1, backgroundColor: "#fff" }}
      contentContainerStyle={{ padding: 16 }}
      data={data}
      keyExtractor={(x) => String(x.user_garment_id)}
      renderItem={({ item }) => (
        <View style={{ marginBottom: 12, borderRadius: 12, backgroundColor: "#fff" }}>
          {!!(item.primary_photo_url || item.image_url) && (
            <Image
              source={{ uri: item.primary_photo_url ?? item.image_url ?? undefined }}
              style={{ height: 220, borderRadius: 12, backgroundColor: "#eee" }}
              resizeMode="cover"
            />
          )}
          <View style={{ paddingTop: 8 }}>
            <Text style={{ fontWeight: "600" }}>{item.product_name ?? "Garment"}</Text>
            {!!item.product_url && <Text style={{ color: "#666" }}>{item.product_url}</Text>}
          </View>
        </View>
      )}
      ListEmptyComponent={
        <View style={{ padding: 24 }}>
          <Text style={{ color: "#666" }}>No items yet.</Text>
        </View>
      }
    />
  );
}


