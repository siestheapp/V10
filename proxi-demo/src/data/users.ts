import { User, UserOwnedProduct } from '../types';

// Main demo user
export const demoUser: User = {
  id: 'demo-user',
  username: '@you',
  totalPieces: 8,
};

// Other users who will be "proxies" (size twins)
export const otherUsers: User[] = [
  {
    id: 'ellaa76',
    username: '@ellaa76',
    totalPieces: 12,
  },
  {
    id: 'vera',
    username: '@vera',
    totalPieces: 6,
  },
  {
    id: 'may_98',
    username: '@may_98',
    totalPieces: 3,
  },
  {
    id: 'srd24',
    username: '@srd24',
    totalPieces: 1,
  },
  {
    id: 'ava_kim',
    username: '@ava_kim',
    totalPieces: 9,
  },
  {
    id: 'jules_22',
    username: '@jules_22',
    totalPieces: 7,
  },
  {
    id: 'mira_s',
    username: '@mira_s',
    totalPieces: 5,
  },
];

// Demo user's closet (what they own)
export const demoUserCloset: UserOwnedProduct[] = [
  { productId: 'jcrew-halter-mixy-dress', size: 'S', userId: 'demo-user' },
  { productId: 'georgia-hardinge-relic-dress', size: 'UK 8', userId: 'demo-user' },
  { productId: 'reformation-taryn-two-piece', size: '2', userId: 'demo-user' },
  { productId: 'alfie-open-back-top', size: 'Small', userId: 'demo-user' },
  { productId: 'ayr-secret-sauce', size: '26S', userId: 'demo-user' },
  { productId: 'zara-flare-pants', size: 'M', userId: 'demo-user' },
  { productId: 'cos-shrunken-tshirt', size: 'XS', userId: 'demo-user' },
  { productId: 'alexis-briette-dress', size: 'S', userId: 'demo-user' },
];

// Other users' closets (who owns what in what size)
// These create the "proxy" relationships
export const allUserProducts: UserOwnedProduct[] = [
  // @ellaa76 - has 4 items in common with demo user (same product, same size)
  { productId: 'jcrew-halter-mixy-dress', size: 'S', userId: 'ellaa76' },
  { productId: 'reformation-taryn-two-piece', size: '2', userId: 'ellaa76' },
  { productId: 'zara-flare-pants', size: 'M', userId: 'ellaa76' },
  { productId: 'cos-shrunken-tshirt', size: 'XS', userId: 'ellaa76' },
  // Plus other items not in demo user's closet
  { productId: 'jcrew-halter-mixy-dress', size: 'M', userId: 'ellaa76' },  // Different size

  // @vera - has 2 items in common
  { productId: 'jcrew-halter-mixy-dress', size: 'S', userId: 'vera' },
  { productId: 'alfie-open-back-top', size: 'Small', userId: 'vera' },

  // @may_98 - has 3 items in common
  { productId: 'jcrew-halter-mixy-dress', size: 'S', userId: 'may_98' },
  { productId: 'zara-flare-pants', size: 'M', userId: 'may_98' },
  { productId: 'cos-shrunken-tshirt', size: 'XS', userId: 'may_98' },

  // @srd24 - has 1 item in common
  { productId: 'jcrew-halter-mixy-dress', size: 'S', userId: 'srd24' },

  // @ava_kim - has 5 items in common (very strong proxy!)
  { productId: 'zara-flare-pants', size: 'M', userId: 'ava_kim' },
  { productId: 'cos-shrunken-tshirt', size: 'XS', userId: 'ava_kim' },
  { productId: 'reformation-taryn-two-piece', size: '2', userId: 'ava_kim' },
  { productId: 'ayr-secret-sauce', size: '26S', userId: 'ava_kim' },
  { productId: 'alexis-briette-dress', size: 'S', userId: 'ava_kim' },

  // @jules_22 - has 2 items in common
  { productId: 'zara-flare-pants', size: 'M', userId: 'jules_22' },
  { productId: 'ayr-secret-sauce', size: '26S', userId: 'jules_22' },

  // @mira_s - has 3 items in common
  { productId: 'cos-shrunken-tshirt', size: 'XS', userId: 'mira_s' },
  { productId: 'reformation-taryn-two-piece', size: '2', userId: 'mira_s' },
  { productId: 'alfie-open-back-top', size: 'Small', userId: 'mira_s' },
];
