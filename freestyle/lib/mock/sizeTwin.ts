export type ClosetItem = {
  id: string
  imageUrl: string
  brand: string
  item: string
  sizeLabel: string
}

export type SizeTwinMatch = {
  you: { name: string; avatarUrl?: string }
  twin: { name: string; avatarUrl?: string }
  sizeBadge: string
  brandItem: { brand: string; line?: string; item: string; sizeLabel: string }
  stats: { overlappingBrands: number; fitMatchPct: number }
  closetPreview: ClosetItem[]
  privacy: { shareLevel: 'public' | 'mutuals' | 'private' }
}

const CLOSET_PLACEHOLDERS = [
  {
    id: 'closet-aritzia-tempest',
    image: '/mockups/placeholders/aritzia-tempest.svg',
    brand: 'Aritzia',
    item: 'Wilfred Tempest Dress',
    sizeLabel: 'S',
  },
  {
    id: 'closet-reformation-dolci',
    image: '/mockups/placeholders/reformation-dolci.svg',
    brand: 'Reformation',
    item: 'Dolci Midi',
    sizeLabel: '2',
  },
  {
    id: 'closet-abercrombie-satin',
    image: '/mockups/placeholders/abercrombie-satin.svg',
    brand: 'Abercrombie',
    item: 'Satin Slip Midi',
    sizeLabel: 'S',
  },
  {
    id: 'closet-skims-soft-lounge',
    image: '/mockups/placeholders/skims-soft-lounge.svg',
    brand: 'Skims',
    item: 'Soft Lounge Dress',
    sizeLabel: 'S',
  },
  {
    id: 'closet-jcrew-resort',
    image: '/mockups/placeholders/jcrew-resort.svg',
    brand: 'J.Crew',
    item: 'Resort Romper',
    sizeLabel: '2',
  },
  {
    id: 'closet-babaton-sorrento',
    image: '/mockups/placeholders/babaton-sorrento.svg',
    brand: 'Babaton',
    item: 'Sorrento Mini',
    sizeLabel: 'S',
  },
]

export function getMockSizeTwin(): SizeTwinMatch {
  return {
    you: {
      name: 'You',
      avatarUrl: '/mockups/placeholders/avatar-you.svg',
    },
    twin: {
      name: 'Maya',
      avatarUrl: '/mockups/placeholders/avatar-maya.svg',
    },
    sizeBadge: 'S',
    brandItem: {
      brand: 'Aritzia',
      line: 'Wilfred',
      item: 'Tempest Dress',
      sizeLabel: 'S',
    },
    stats: {
      overlappingBrands: 8,
      fitMatchPct: 92,
    },
    closetPreview: CLOSET_PLACEHOLDERS.map((item) => ({
      id: item.id,
      imageUrl: item.image,
      brand: item.brand,
      item: item.item,
      sizeLabel: item.sizeLabel,
    })),
    privacy: {
      shareLevel: 'mutuals',
    },
  }
}
