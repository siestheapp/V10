/**
 * Proxi Design System
 *
 * A consumer-grade design system built for scale.
 * Designed for hundreds of millions of users with agency-level polish.
 */

export const colors = {
  // Ink — Primary text colors (dark charcoal palette)
  ink: {
    900: '#0B0F14',  // Headings, primary text
    700: '#121A22',  // Secondary text
    500: '#2A3642',  // Tertiary text
    300: '#6A7683',  // Muted text, captions
    100: '#A0A8B1',  // Disabled text
  },

  // Canvas — Background colors (light neutral palette)
  canvas: {
    0: '#FFFFFF',    // Pure white surfaces
    50: '#F7F9FB',   // Page background
    100: '#EFF3F6',  // Subtle background
    200: '#E9EEF1',  // Dividers, borders
  },

  // Petrol — Primary brand color (teal-cyan spectrum)
  petrol: {
    700: '#007777',  // Darkest petrol
    600: '#009090',  // Deep petrol
    500: '#00A3A3',  // Primary brand (main CTA)
    400: '#16B5B5',  // Hover state
    300: '#3ECFD5',  // Light petrol
    100: '#E0F7F7',  // Lightest tint (backgrounds)
    50: '#F0FBFB',   // Ultra-light background
  },

  // Accent colors
  mint: {
    500: '#7FFFBF',
    400: '#A6FFCB',
    300: '#C2FFE0',
  },

  ice: {
    400: '#5DD6EB',
    300: '#7FE1FF',
    200: '#A8EBFF',
  },

  // Semantic colors
  success: {
    500: '#10B981',
    100: '#D1FAE5',
  },

  warning: {
    500: '#F59E0B',
    100: '#FEF3C7',
  },

  error: {
    500: '#EF4444',
    100: '#FEE2E2',
  },

  // Overlay colors (for modals, bottom sheets)
  overlay: {
    dark: 'rgba(11, 15, 20, 0.75)',
    medium: 'rgba(11, 15, 20, 0.50)',
    light: 'rgba(11, 15, 20, 0.25)',
  },
};

export const gradients = {
  // Primary brand gradient (petrol → ice → mint)
  brandSheen: 'linear-gradient(135deg, #00A3A3 0%, #7FE1FF 50%, #A6FFCB 100%)',

  // Alternative gradients
  petrolGlow: 'linear-gradient(135deg, #009090 0%, #3ECFD5 50%, #7FE1FF 100%)',
  subtleSheen: 'linear-gradient(180deg, #F7F9FB 0%, #FFFFFF 100%)',

  // Overlay gradients
  imageOverlay: 'linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.7) 100%)',
};

export const spacing = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  7: 28,
  8: 32,
  10: 40,
  12: 48,
  16: 64,
  20: 80,
  24: 96,
};

export const borderRadius = {
  none: 0,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  full: 9999,
};

export const shadows = {
  // Subtle elevations for cards and surfaces
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 3,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 24,
    elevation: 5,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.16,
    shadowRadius: 40,
    elevation: 8,
  },
};

export const typography = {
  // Font families
  fontFamily: {
    base: 'Inter',
    // Fallback for system fonts on React Native
    system: 'System',
  },

  // Font sizes (optimized for mobile)
  fontSize: {
    xs: 11,
    sm: 12,
    base: 14,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 28,
    '4xl': 32,
    '5xl': 40,
    '6xl': 48,
  },

  // Font weights
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
    extrabold: '800' as const,
  },

  // Line heights (as multipliers)
  lineHeight: {
    tight: 1.1,
    snug: 1.2,
    normal: 1.4,
    relaxed: 1.5,
    loose: 1.6,
  },

  // Letter spacing
  letterSpacing: {
    tighter: -0.03,
    tight: -0.02,
    normal: -0.01,
    wide: 0.01,
    wider: 0.02,
  },
};

// Pre-composed text styles for common use cases
export const textStyles = {
  // Display / Hero text
  display: {
    fontSize: typography.fontSize['5xl'],
    fontWeight: '700' as const,
    lineHeight: typography.lineHeight.tight * typography.fontSize['5xl'],
    letterSpacing: typography.letterSpacing.tighter,
    color: colors.ink[900],
  },

  // Page titles
  h1: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: '700' as const,
    lineHeight: typography.lineHeight.snug * typography.fontSize['3xl'],
    letterSpacing: typography.letterSpacing.tight,
    color: colors.ink[900],
  },

  // Section titles
  h2: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '600' as const,
    lineHeight: typography.lineHeight.snug * typography.fontSize['2xl'],
    letterSpacing: typography.letterSpacing.tight,
    color: colors.ink[900],
  },

  // Subsection titles
  h3: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    lineHeight: typography.lineHeight.normal * typography.fontSize.lg,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.ink[900],
  },

  // Body text
  body: {
    fontSize: typography.fontSize.base,
    fontWeight: '400' as const,
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.base,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.ink[700],
  },

  // Medium body text (slightly emphasized)
  bodyMedium: {
    fontSize: typography.fontSize.base,
    fontWeight: '500' as const,
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.base,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.ink[900],
  },

  // Small text
  small: {
    fontSize: typography.fontSize.sm,
    fontWeight: '400' as const,
    lineHeight: typography.lineHeight.normal * typography.fontSize.sm,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.ink[500],
  },

  // Caption / metadata
  caption: {
    fontSize: typography.fontSize.xs,
    fontWeight: '500' as const,
    lineHeight: typography.lineHeight.normal * typography.fontSize.xs,
    letterSpacing: typography.letterSpacing.wide,
    color: colors.ink[300],
  },

  // Button text
  button: {
    fontSize: typography.fontSize.md,
    fontWeight: '600' as const,
    lineHeight: typography.fontSize.md,
    letterSpacing: typography.letterSpacing.normal,
  },

  // Tab bar labels
  tabLabel: {
    fontSize: typography.fontSize.xs,
    fontWeight: '500' as const,
    lineHeight: typography.fontSize.xs,
    letterSpacing: typography.letterSpacing.normal,
  },
};

// Animation/timing values
export const animation = {
  duration: {
    instant: 0,
    fast: 150,
    normal: 250,
    slow: 350,
    slower: 500,
  },

  easing: {
    // Standard easing curves
    easeIn: [0.4, 0, 1, 1] as const,
    easeOut: [0, 0, 0.2, 1] as const,
    easeInOut: [0.4, 0, 0.2, 1] as const,

    // Custom easing for bouncy effects
    spring: [0.34, 1.56, 0.64, 1] as const,
  },
};

// Layout constants
export const layout = {
  // Screen padding
  screenPadding: {
    horizontal: spacing[6],  // 24px
    vertical: spacing[4],    // 16px
  },

  // Safe area padding (for iOS notch, etc)
  safeArea: {
    top: 44,
    bottom: 34,
  },

  // Grid columns for product grids
  grid: {
    columns: 2,
    gap: spacing[3],  // 12px
  },

  // Common dimensions
  tabBar: {
    height: 83,
    iconSize: 28,
  },

  // Product card aspect ratios
  productCard: {
    aspectRatio: 0.75,  // 3:4 ratio (portrait)
  },
};

// Export everything as default theme object
export const theme = {
  colors,
  gradients,
  spacing,
  borderRadius,
  shadows,
  typography,
  textStyles,
  animation,
  layout,
};

export default theme;
