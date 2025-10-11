import { FeedItem } from './types';

export const allItems: FeedItem[] = [
  { id: 1, title: 'Coastal Petrol', subtitle: 'Soft gradients & sheen', image: require('../../assets/hero1.jpg'), tags: ['Design', 'Inspo'], shopUrl: 'https://example.com/a' },
  { id: 2, title: 'Shade Study', subtitle: 'Petrol palette in action', image: require('../../assets/hero1.jpg'), tags: ['Design'], shopUrl: 'https://example.com/b' },
  { id: 3, title: 'Material Mix', subtitle: 'Cards, chips, and pills', image: require('../../assets/hero1.jpg'), tags: ['Components'], shopUrl: 'https://example.com/c' },
];

export function getItemById(id: number) {
  return allItems.find(i => i.id === id);
}


