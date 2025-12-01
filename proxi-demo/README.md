# Proxi Demo App

A peer-to-peer size comparison app that helps users find "size twins" - people who own the same products in the same size.

## Overview

This is a demo Expo app built to showcase the Proxi concept with seed data. It demonstrates:

- **Closet Screen**: Browse your owned products with proxy counts
- **Proxy Matching**: See which users own the same items in the same size
- **Enhanced Design System**: Consumer-grade UI built for scale

## Quick Start

```bash
# Install dependencies
npm install

# Start the development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android

# Run on web
npm run web
```

## Project Structure

```
proxi-demo/
├── app/
│   ├── _layout.tsx                 # Root layout
│   └── (tabs)/                      # Tab navigation
│       ├── _layout.tsx              # Tab bar
│       ├── closet.tsx               # Closet screen (main)
│       ├── find.tsx                 # Find screen (placeholder)
│       ├── feed.tsx                 # Feed screen (placeholder)
│       └── profile.tsx              # Profile screen (placeholder)
├── src/
│   ├── components/                  # Reusable UI components
│   │   ├── ProductCard.tsx
│   │   └── ProxyPill.tsx
│   ├── data/                        # Seed data
│   │   ├── products.ts              # Product catalog
│   │   ├── users.ts                 # Users and ownership data
│   │   └── proxies.ts               # Proxy matching logic
│   ├── theme/                       # Design system
│   │   └── tokens.ts                # Design tokens
│   └── types/                       # TypeScript types
│       └── index.ts
└── assets/                          # Images and icons
```

## Design System

The app uses a custom design system built on:

- **Colors**: Petrol (teal-cyan) brand color with ink/canvas neutrals
- **Typography**: Inter font family with responsive sizing
- **Spacing**: 4px base unit with consistent scale
- **Shadows**: Subtle elevations for depth
- **Animation**: Smooth transitions and interactions

See `src/theme/tokens.ts` for the complete design system.

## Seed Data

The app includes seed data for:

- **Demo User**: @you with 8 owned products
- **Proxy Users**: 7 other users with overlapping product ownership
- **Products**: 8 fashion items from various brands

### Proxy Matching Logic

Users become "proxies" when they:
1. Own the same product
2. In the same size
3. As the demo user

The app calculates and displays how many products each proxy shares with the demo user.

## Key Features

### Closet Screen
- Grid/list view toggle
- Category filters (All, Tops, Bottoms, Dresses)
- Product cards with images, size badges, and proxy counts
- Proxy modal showing matching users
- Smooth animations and interactions

### Design Highlights
- Linear gradient brand header
- Shadow elevations for depth
- Consistent spacing and typography
- Accessible touch targets (44px minimum)
- Smooth modal transitions

## Tech Stack

- **Expo SDK 54** - Cross-platform React Native framework
- **Expo Router** - File-based navigation
- **TypeScript** - Type safety
- **React Native SVG** - Vector icons
- **Expo Linear Gradient** - Brand gradients

## Next Steps

To continue building:

1. **Find Screen**: Add product URL input and matching logic
2. **Feed Screen**: Show feed of size twin activity
3. **Profile Screen**: User profile and settings
4. **Authentication**: Add user sign-up/sign-in
5. **Backend**: Connect to real API instead of seed data

## License

MIT
