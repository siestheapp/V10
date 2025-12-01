import { View, Text, Image, Pressable, StyleSheet } from 'react-native';
import { theme } from '../theme/tokens';
import { ProductWithOwnership } from '../types';
import { ProxyPill } from './ProxyPill';

interface ProductCardProps {
  product: ProductWithOwnership;
  onPress?: () => void;
  onProxyPress?: () => void;
}

export function ProductCard({ product, onPress, onProxyPress }: ProductCardProps) {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.card,
        pressed && styles.cardPressed,
      ]}
      onPress={onPress}
    >
      {/* Product Image */}
      <Image
        source={{ uri: product.imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />

      {/* Size Badge */}
      <View style={styles.sizeBadge}>
        <Text style={styles.sizeText}>{product.userSize}</Text>
      </View>

      {/* Proxy Pill (top-right) */}
      {product.proxyCount > 0 && (
        <View style={styles.proxyPillContainer}>
          <ProxyPill count={product.proxyCount} onPress={onProxyPress} />
        </View>
      )}

      {/* Gradient Overlay */}
      <View style={styles.overlay}>
        <Text style={styles.brand}>{product.brand}</Text>
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    backgroundColor: theme.colors.canvas[100],
    ...theme.shadows.md,
  },
  cardPressed: {
    transform: [{ scale: 0.98 }],
    opacity: 0.9,
  },
  image: {
    width: '100%',
    aspectRatio: theme.layout.productCard.aspectRatio,
  },
  sizeBadge: {
    position: 'absolute',
    top: 10,
    left: 10,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.full,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    backdropFilter: 'blur(2px)',
  },
  sizeText: {
    ...theme.textStyles.caption,
    color: theme.colors.canvas[0],
    fontWeight: '700',
  },
  proxyPillContainer: {
    position: 'absolute',
    top: 10,
    right: 10,
    zIndex: 3,
  },
  overlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
  },
  brand: {
    ...theme.textStyles.caption,
    color: theme.colors.canvas[0],
    fontWeight: '700',
    letterSpacing: 0.04,
    opacity: 0.95,
    marginBottom: 2,
  },
  name: {
    ...theme.textStyles.small,
    color: theme.colors.canvas[0],
    fontWeight: '600',
    lineHeight: theme.textStyles.small.fontSize * 1.2,
  },
});
