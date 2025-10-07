import { Image } from 'expo-image';
import { Text, TouchableOpacity, View } from 'react-native';
import { useRouter } from 'expo-router';
import type { ProductResult } from '../../lib/product';

type Props = {
  product: ProductResult;
};

export default function ProductSummary({ product }: Props) {
  const router = useRouter();

  const onNext = () => {
    const payload = encodeURIComponent(JSON.stringify(product));
    router.push(`/scan/confirm?p=${payload}`);
  };

  return (
    <View style={{ marginTop: 24, gap: 12 }}>
      {product.image_url ? (
        <Image
          source={{ uri: product.image_url }}
          style={{ width: '100%', height: 240, borderRadius: 12, backgroundColor: '#eee' }}
          contentFit="cover"
          transition={150}
        />
      ) : null}
      <View style={{ gap: 4 }}>
        <Text style={{ fontSize: 18, fontWeight: '600' }}>{product.brand}</Text>
        <Text style={{ fontSize: 16, color: '#444' }}>{product.style_name}</Text>
        {product.color ? <Text style={{ color: '#666' }}>Color: {product.color}</Text> : null}
        {product.fit ? <Text style={{ color: '#666' }}>Fit: {product.fit}</Text> : null}
        {product.variant_code ? <Text style={{ color: '#666' }}>Variant: {product.variant_code}</Text> : null}
        {product.style_code ? <Text style={{ color: '#666' }}>Style Code: {product.style_code}</Text> : null}
      </View>
      <TouchableOpacity
        style={{ backgroundColor: '#111', paddingVertical: 14, borderRadius: 10, alignItems: 'center' }}
        onPress={onNext}
        activeOpacity={0.85}
      >
        <Text style={{ color: '#fff', fontWeight: '600' }}>Next</Text>
      </TouchableOpacity>
    </View>
  );
}
