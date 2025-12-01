export type Category = 'tops' | 'bottoms' | 'dresses';

export interface Product {
  id: string;
  name: string;
  brand: string;
  imageUrl: string;
  category: Category;
  url: string;
}

export interface UserOwnedProduct {
  productId: string;
  size: string;
  userId: string;
}

export interface User {
  id: string;
  username: string;
  totalPieces: number;
}

export interface ProxyMatch {
  user: User;
  sharedProducts: number;  // How many products in common
}

export interface ProductWithOwnership extends Product {
  userSize: string;
  proxyCount: number;
}
