import { useLocalSearchParams, useRouter } from 'expo-router';
import { useMemo, useState } from 'react';
import { Image } from 'expo-image';
import { ScrollView, Text, TouchableOpacity, View } from 'react-native';

// Dynamic options are provided via product payload (fit_options, size_options)

type Product = {
  brand: string;
  style_name: string;
  style_code: string | null;
  image_url?: string | null;
  fit_options?: string[];
  size_options?: string[];
};

export default function ConfirmTryOn() {
  const params = useLocalSearchParams<{ p?: string }>();
  const router = useRouter();

  const product = useMemo<Product | null>(() => {
    try {
      if (!params.p) return null;
      return JSON.parse(decodeURIComponent(Array.isArray(params.p) ? params.p[0] : params.p));
    } catch {
      return null;
    }
  }, [params.p]);

  const [fit, setFit] = useState<string | null>(null);
  const [size, setSize] = useState<string | null>(null);

  const canContinue = !!fit && !!size;

  const onConfirm = () => {
    if (!product || !canContinue) return;
    // TODO: Persist a try-on session row; for now, just navigate to tryons tab
    router.replace('/(tabs)/tryons');
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 16, backgroundColor: '#fff' }}>
      {product?.image_url ? (
        <Image
          source={{ uri: product.image_url }}
          style={{ width: '100%', height: 220, borderRadius: 12, backgroundColor: '#eee' }}
          contentFit="cover"
        />
      ) : null}

      <View>
        <Text style={{ color: '#777', fontWeight: '600', marginBottom: 6 }}>{product?.brand}</Text>
        <Text style={{ fontSize: 22, fontWeight: '700' }}>{product?.style_name}</Text>
      </View>

      <View style={{ gap: 10 }}>
        <Text style={{ fontSize: 18, fontWeight: '700' }}>Select Fit Type</Text>
        <Text style={{ color: '#666' }}>Which fit are you trying on? This affects the measurements.</Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {(product?.fit_options && product.fit_options.length ? product.fit_options : ['Classic']).map((f) => (
            <TouchableOpacity
              key={f}
              onPress={() => setFit(f)}
              style={{
                paddingVertical: 12,
                paddingHorizontal: 16,
                borderRadius: 10,
                borderWidth: 1,
                borderColor: fit === f ? '#111' : '#ddd',
                backgroundColor: fit === f ? '#111' : '#fff',
              }}
            >
              <Text style={{ color: fit === f ? '#fff' : '#111', fontWeight: '600' }}>{f}</Text>
            </TouchableOpacity>
          ))}
        </View>
        {fit ? (
          <View style={{ padding: 12, borderWidth: 1, borderColor: '#e5e5e5', borderRadius: 10 }}>
            <Text style={{ color: '#444' }}>Our signature fit with a comfortable, time-tested cut.</Text>
          </View>
        ) : null}
      </View>

      <View style={{ gap: 10 }}>
        <Text style={{ fontSize: 18, fontWeight: '700' }}>What Size Are You Trying On?</Text>
        <Text style={{ color: '#666' }}>Select the size on the tag you're about to try on</Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {(product?.size_options && product.size_options.length ? product.size_options : ['XS','S','M','L','XL','XXL']).map((s) => (
            <TouchableOpacity
              key={s}
              onPress={() => setSize(s)}
              style={{
                paddingVertical: 12,
                paddingHorizontal: 16,
                borderRadius: 10,
                borderWidth: 1,
                borderColor: size === s ? '#111' : '#ddd',
                backgroundColor: size === s ? '#111' : '#fff',
              }}
            >
              <Text style={{ color: size === s ? '#fff' : '#111', fontWeight: '600' }}>{s}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity
        disabled={!canContinue}
        onPress={onConfirm}
        style={{
          paddingVertical: 14,
          borderRadius: 10,
          alignItems: 'center',
          backgroundColor: canContinue ? '#111' : '#bbb',
          marginTop: 8,
        }}
      >
        <Text style={{ color: '#fff', fontWeight: '700' }}>Confirm Try-On</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
