import { View, Text, Pressable, StyleSheet } from 'react-native';
import { theme } from '../theme/tokens';
import Svg, { Path } from 'react-native-svg';

interface ProxyPillProps {
  count: number;
  onPress?: () => void;
}

export function ProxyPill({ count, onPress }: ProxyPillProps) {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.pill,
        pressed && styles.pillPressed,
      ]}
      onPress={onPress}
    >
      {/* Proxi Icon (triple bars) */}
      <Svg width="14" height="14" viewBox="0 0 256 256" style={styles.icon}>
        <Path
          fill={theme.colors.petrol[600]}
          d="M225.24,174.74a12,12,0,0,1-1.58,16.89C205.49,206.71,189.06,212,174.15,212c-19.76,0-36.86-9.29-51.88-17.44-25.06-13.62-44.86-24.37-74.61.3a12,12,0,1,1-15.32-18.48c42.25-35,75-17.23,101.39-2.92,25.06,13.61,44.86,24.37,74.61-.3A12,12,0,0,1,225.24,174.74Zm-16.9-57.59c-29.75,24.67-49.55,13.91-74.61.3-26.35-14.3-59.14-32.11-101.39,2.92a12,12,0,0,0,15.32,18.48c29.75-24.67,49.55-13.92,74.61-.3,15,8.15,32.12,17.44,51.88,17.44,14.91,0,31.34-5.29,49.51-20.36a12,12,0,0,0-15.32-18.48ZM47.66,82.84c29.75-24.67,49.55-13.92,74.61-.3,15,8.15,32.12,17.44,51.88,17.44,14.91,0,31.34-5.29,49.51-20.36a12,12,0,0,0-15.32-18.48c-29.75,24.67-49.55,13.92-74.61.3-26.35-14.3-59.14-32.11-101.39,2.93A12,12,0,1,0,47.66,82.84Z"
        />
      </Svg>

      {/* Count */}
      <Text style={styles.count}>{count}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.canvas[0],
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.16)',
    ...theme.shadows.md,
  },
  pillPressed: {
    opacity: 0.8,
    transform: [{ scale: 0.95 }],
  },
  icon: {
    width: 14,
    height: 14,
  },
  count: {
    ...theme.textStyles.caption,
    fontWeight: '700',
    color: theme.colors.ink[700],
    fontVariant: ['tabular-nums'],
  },
});
