import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../src/theme/tokens';

export default function FindScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Find Screen</Text>
      <Text style={styles.subtext}>Coming soon...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.canvas[50],
  },
  text: {
    ...theme.textStyles.h1,
    marginBottom: theme.spacing[2],
  },
  subtext: {
    ...theme.textStyles.body,
    color: theme.colors.ink[300],
  },
});
