import { ProxyMatch, UserOwnedProduct } from '../types';
import { demoUserCloset, allUserProducts, otherUsers } from './users';

/**
 * Get proxy matches for a specific product and size
 * Returns users who own the same product in the same size
 */
export function getProxiesForProduct(productId: string, size: string): ProxyMatch[] {
  // Find all users who own this product in this size (excluding demo user)
  const matchingUsers = allUserProducts
    .filter(
      (owned) =>
        owned.productId === productId &&
        owned.size === size &&
        owned.userId !== 'demo-user'
    )
    .map((owned) => owned.userId);

  // Get unique user IDs
  const uniqueUserIds = Array.from(new Set(matchingUsers));

  // Calculate shared products for each matching user
  const proxies: ProxyMatch[] = uniqueUserIds.map((userId) => {
    const user = otherUsers.find((u) => u.id === userId)!;

    // Count how many products this user shares with demo user (same product, same size)
    const sharedCount = countSharedProducts(userId);

    return {
      user,
      sharedProducts: sharedCount,
    };
  });

  // Sort by most shared products first
  return proxies.sort((a, b) => b.sharedProducts - a.sharedProducts);
}

/**
 * Count how many products a user shares with the demo user (same product, same size)
 */
function countSharedProducts(userId: string): number {
  let count = 0;

  for (const demoOwned of demoUserCloset) {
    const hasMatch = allUserProducts.some(
      (owned) =>
        owned.userId === userId &&
        owned.productId === demoOwned.productId &&
        owned.size === demoOwned.size
    );

    if (hasMatch) {
      count++;
    }
  }

  return count;
}

/**
 * Get proxy count for a specific product and size
 */
export function getProxyCount(productId: string, size: string): number {
  return getProxiesForProduct(productId, size).length;
}

/**
 * Get all products owned by demo user with proxy counts
 */
export function getDemoUserClosetWithProxies() {
  return demoUserCloset.map((owned) => ({
    ...owned,
    proxyCount: getProxyCount(owned.productId, owned.size),
  }));
}
