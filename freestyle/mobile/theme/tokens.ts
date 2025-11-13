export const colors = {
  ink900: '#0B0F14',
  ink700: '#121A22',
  ink500: '#2A3642',
  text: '#1F1F1F',
  muted: '#6F6F74',
  background: '#F7F9FB',
  backgroundAlt: '#FAF8F6',
  surface: '#FFFFFF',
  border: '#E8E4DE',
  petrol600: '#009090',
  petrol500: '#00A3A3',
  petrol400: '#16B5B5',
  petrol100: '#E0F7F7',
  ice300: '#7FE1FF',
  mint400: '#A6FFCB'
};

export const radii = { card: 18, pill: 999, button: 16 };
export const space = { 4: 4, 6: 6, 8: 8, 10: 10, 12: 12, 14: 14, 16: 16, 18: 18, 20: 20, 24: 24 };
export const typography = {
  h1: { fontSize: 26, fontWeight: '700', letterSpacing: -0.2 as const },
  h2: { fontSize: 20, fontWeight: '700' as const },
  body: { fontSize: 14, fontWeight: '600' as const },
  subtle: { fontSize: 12, color: colors.muted },
  badge: { fontSize: 12, fontWeight: '700' as const }
};
