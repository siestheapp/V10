// Freestyle App Mockup Data
// Consistent data model for all mockup screens

const MOCKUP_DATA = {
  // Primary User Profile (Lily)
  user: {
    id: 'lily_001',
    name: 'Lily',
    age: 26,
    height: '5\'5"',
    weight: '122 lbs',
    measurements: {
      bust: 34,
      waist: 26,
      hips: 37
    },
    typicalSize: '2', // Reformation size 2, translates to S in most brands
    fitPreference: 'fitted', // fitted, relaxed, or perfect
    location: 'San Francisco, CA'
  },

  // Lily's Closet Items (reference pieces for size matching)
  closet: [
    {
      id: 'bryson_dress',
      name: 'Bryson Dress',
      brand: 'Reformation',
      size: '2',
      category: 'dress',
      measurements: {
        bust: 34,
        waist: 26,
        hips: 37
      },
      fit: 'perfect',
      image: 'https://media.thereformation.com/image/upload/f_auto,q_auto:eco,dpr_2.0/w_500/PRD-SFCC/1312619/MYKONOS/1312619.2.MYKONOS?_s=RAABAB0',
      purchaseDate: '2024-03-20',
      details: {
        pattern: 'Mykonos',
        style: 'Fitted bodice with A-line skirt',
        neckline: 'Sweetheart',
        length: 'Midi (above ankle)',
        fabric: '53% Viscose, 47% LENZING™ ECOVERO™ Viscose'
      }
    },
    {
      id: 'alexis_dress',
      name: 'Briette Satin Maxi Dress',
      brand: 'ALEXIS',
      size: 'S',
      category: 'dress',
      measurements: {
        bust: 33,
        waist: 27,
        hips: 37
      },
      fit: 'perfect',
      image: 'https://cdn.modaoperandi.com/assets/images/products/1039207/685257/c/large_alexis-blue-briette-dress.jpg?_v=1755195214',
      purchaseDate: '2024-01-15'
    },
    {
      id: 'reformation_dress',
      name: 'Taryn Two Piece',
      brand: 'Reformation',
      size: '2',
      category: 'dress',
      measurements: {
        bust: 33,
        waist: 26,
        hips: 36
      },
      fit: 'perfect',
      image: 'https://media.thereformation.com/image/upload/f_auto,q_auto:eco,dpr_2.0/w_500/PRD-SFCC/1314122/BLACK/1314122.1.BLACK?_s=RAABAB0',
      purchaseDate: '2023-11-20'
    },
    {
      id: 'alfie_top',
      name: 'Open Back Cotton Poplin Top',
      brand: 'ALFIE',
      size: 'Small',
      category: 'top',
      measurements: {
        bust: 34,
        waist: 30,
        hips: 38
      },
      fit: 'perfect',
      image: 'https://cdn.modaoperandi.com/assets/images/products/1028958/674197/c/large_alfie-white-backless-top.jpg?_v=1755087491',
      purchaseDate: '2024-02-10'
    },
    {
      id: 'ayr_jeans',
      name: 'The Secret Sauce',
      brand: 'AYR',
      size: '26S',
      category: 'bottom',
      measurements: {
        waist: 27,
        hips: 37,
        inseam: 28
      },
      fit: 'perfect',
      image: 'https://www.ayr.com/cdn/shop/files/secretsauce-goodmood_CAT_d634f664-cb49-4e61-abef-5d94b707075e.jpg?crop=center&height=1440&v=1755036845&width=950',
      purchaseDate: '2023-12-05'
    },
    {
      id: 'cos_tshirt',
      name: 'Shrunken T-shirt',
      brand: 'COS',
      size: 'XS',
      category: 'top',
      measurements: {
        bust: 35,
        waist: 28,
        hips: 38
      },
      fit: 'relaxed',
      image: 'https://media.cos.com/assets/001/6e/d0/6ed0142c6e69ad42e826224d9a8d013f6d3f4685_xxl-1.jpg?imwidth=2160',
      purchaseDate: '2024-01-30'
    }
  ],

  // Size Twins (users with similar measurements)
  sizeTwins: [
    {
      id: 'emma_002',
      name: 'Emma',
      age: 24,
      location: 'Los Angeles, CA',
      measurements: {
        bust: 34,
        waist: 26,
        hips: 37
      },
      typicalSize: '2',
      matchScore: 98,
      sharedItems: 12,
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face'
    },
    {
      id: 'sophia_003',
      name: 'Sophia',
      age: 28,
      location: 'New York, NY',
      measurements: {
        bust: 33,
        waist: 26,
        hips: 36
      },
      typicalSize: '2',
      matchScore: 95,
      sharedItems: 8,
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face'
    },
    {
      id: 'maya_004',
      name: 'Maya',
      age: 25,
      location: 'Austin, TX',
      measurements: {
        bust: 35,
        waist: 27,
        hips: 38
      },
      typicalSize: '4',
      matchScore: 92,
      sharedItems: 6,
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop&crop=face'
    }
  ],

  // Product Catalog for Feed
  products: [
    {
      id: 'jocelyn_dress',
      name: 'The Jocelyn Sleeveless Slip Midi Dress',
      brand: 'Maeve',
      retailer: 'Anthropologie',
      price: 168.00,
      category: 'dress',
      image: 'https://images.urbndata.com/is/image/Anthropologie/4130652010091_256_b?$redesign-zoom-5x$',
      url: 'https://www.anthropologie.com/shop/the-jocelyn-sleeveless-slip-midi-dress-by-maeve?category=top-rated-dresses&color=256&type=STANDARD&quantity=1',
      sizeGuide: {
        S: { bust: '35-36', waist: '27-28', hips: '37-38' },
        XS: { bust: '33-34', waist: '25-26', hips: '35-36' },
        M: { bust: '37-38', waist: '29-30', hips: '39-40' }
      },
      recommendation: {
        bestSize: 'S',
        confidence: 98,
        comparisonItem: 'bryson_dress',
        fitNotes: {
          bust: { status: 'looser', difference: '+1-2"', description: 'Slightly roomier bust' },
          waist: { status: 'looser', difference: '+1-2"', description: 'More relaxed at waist' },
          hips: { status: 'matches', difference: '≈', description: 'Perfect hip fit' }
        },
        tip: 'Similar to your Bryson dress with a bit more room through the bodice.',
        alternativeSize: {
          size: 'XS',
          reason: 'For a fitted look like your Bryson, try XS (closer to your exact measurements)'
        }
      },
      peerData: {
        sizeTwins: [
          { userId: 'emma_002', size: 'S', rating: 5, comment: 'Perfect fit!' },
          { userId: 'sophia_003', size: 'S', rating: 5, comment: 'Love this dress' },
          { userId: 'maya_004', size: 'S', rating: 4, comment: 'Great for date night' }
        ],
        totalWearers: 15,
        averageRating: 4.8
      }
    },
    {
      id: 'reformation_camille',
      name: 'Camille Midi Dress',
      brand: 'Reformation',
      retailer: 'Reformation',
      price: 218.00,
      category: 'dress',
      image: 'https://images.urbndata.com/is/image/Anthropologie/4130652010091_256_b?$redesign-zoom-5x$',
      url: 'https://www.thereformation.com/products/camille-midi-dress',
      sizeGuide: {
        S: { bust: '33-34', waist: '26-27', hips: '36-37' },
        XS: { bust: '31-32', waist: '24-25', hips: '34-35' },
        M: { bust: '35-36', waist: '28-29', hips: '38-39' }
      },
      recommendation: {
        bestSize: '2',
        confidence: 100,
        comparisonItem: 'bryson_dress',
        fitNotes: {
          bust: { status: 'matches', difference: '≈', description: 'Exact same bust fit' },
          waist: { status: 'matches', difference: '≈', description: 'Perfect waist match' },
          hips: { status: 'matches', difference: '≈', description: 'Identical hip fit' }
        },
        tip: 'Same size as your Bryson dress — guaranteed perfect fit in Reformation.',
        alternativeSize: null
      },
      peerData: {
        sizeTwins: [
          { userId: 'emma_002', size: 'S', rating: 5, comment: 'So flattering' },
          { userId: 'sophia_003', size: 'S', rating: 5, comment: 'Worth every penny' }
        ],
        totalWearers: 8,
        averageRating: 4.9
      }
    },
    {
      id: 'everlane_tee',
      name: 'The Cotton V-Neck Tee',
      brand: 'Everlane',
      retailer: 'Everlane',
      price: 18.00,
      category: 'top',
      image: 'https://images.urbndata.com/is/image/Anthropologie/4130652010091_256_b?$redesign-zoom-5x$',
      url: 'https://www.everlane.com/products/womens-cotton-v-neck-tee-white',
      sizeGuide: {
        S: { bust: '34-35', waist: '30-31', hips: '38-39' },
        XS: { bust: '32-33', waist: '28-29', hips: '36-37' },
        M: { bust: '36-37', waist: '32-33', hips: '40-41' }
      },
      recommendation: {
        bestSize: 'S',
        confidence: 100,
        comparisonItem: 'cotton_vneck',
        fitNotes: {
          bust: { status: 'matches', difference: '≈', description: 'Identical to your current tee' },
          waist: { status: 'matches', difference: '≈', description: 'Same relaxed fit' },
          hips: { status: 'matches', difference: '≈', description: 'Perfect length and drape' }
        },
        tip: 'Exact same fit as your current Everlane tee — guaranteed to work.',
        alternativeSize: null
      },
      peerData: {
        sizeTwins: [
          { userId: 'emma_002', size: 'S', rating: 5, comment: 'Basic but perfect' },
          { userId: 'maya_004', size: 'S', rating: 4, comment: 'Great for layering' }
        ],
        totalWearers: 23,
        averageRating: 4.6
      }
    }
  ],

  // Filter Options
  filters: {
    categories: ['Wedding guest', 'Midi', 'Under $250', 'Quick ship', 'New in'],
    brands: ['Reformation', 'Anthropologie', 'Everlane', 'Madewell', 'J.Crew'],
    priceRanges: ['Under $50', '$50-100', '$100-200', '$200+'],
    sizes: ['XS', 'S', 'M', 'L']
  },

  // User's Fit Profile Summary
  fitProfile: {
    totalItems: 6,
    mostWornBrand: 'Reformation',
    averageSize: '2',
    fitAccuracy: 98,
    lastUpdated: '2024-03-20',
    measurements: {
      bust: { min: 33, max: 35, avg: 34 },
      waist: { min: 26, max: 28, avg: 26 },
      hips: { min: 36, max: 38, avg: 37 }
    }
  }
};

// Helper functions for mockup data
const MockupHelpers = {
  // Get user's recommended size for a product
  getRecommendedSize(productId) {
    const product = MOCKUP_DATA.products.find(p => p.id === productId);
    return product ? product.recommendation.bestSize : 'S';
  },

  // Get fit comparison text
  getFitComparison(productId) {
    const product = MOCKUP_DATA.products.find(p => p.id === productId);
    if (!product) return 'Size S recommended';
    
    const comparison = product.recommendation;
    const closetItem = MOCKUP_DATA.closet.find(item => item.id === comparison.comparisonItem);
    
    return {
      comparisonItem: closetItem ? closetItem.name : 'your closet',
      tip: comparison.tip,
      fitNotes: comparison.fitNotes
    };
  },

  // Get peer data for a product
  getPeerData(productId) {
    const product = MOCKUP_DATA.products.find(p => p.id === productId);
    return product ? product.peerData : null;
  },

  // Get size twin recommendations
  getSizeTwinRecommendations(productId, size) {
    const product = MOCKUP_DATA.products.find(p => p.id === productId);
    if (!product) return [];
    
    return product.peerData.sizeTwins.filter(twin => twin.size === size);
  },

  // Format price
  formatPrice(price) {
    return `$${price.toFixed(2)}`;
  },

  // Get confidence percentage
  getConfidence(productId) {
    const product = MOCKUP_DATA.products.find(p => p.id === productId);
    return product ? product.recommendation.confidence : 95;
  }
};

// Export for use in mockups
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MOCKUP_DATA, MockupHelpers };
}
