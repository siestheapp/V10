export type ShopLink = { label: string; href: string };
export type SizeTwin = {
  title: string;
  subtitle: string;
  hero: any; // require('…') for local asset
  bestFit: string;
  tips: string[];
  shops: ShopLink[];
};

export const mockSizeTwin: SizeTwin = {
  title: 'Your Fit Feed',
  subtitle: 'Evidence-backed size picks',
  hero: require('../../assets/hero1.jpg'),
  bestFit: 'S',
  tips: [
    'Runs slightly narrow at the toe.',
    'Material relaxes after first wear.'
  ],
  shops: [
    { label: 'Shop this in S', href: '#' },
    { label: 'See more colors', href: '#' }
  ]
};
