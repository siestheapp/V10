import { View, Text, StyleSheet } from 'react-native';

export default function ClosetScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Closet Screen</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F7F9FB',
  },
  text: {
    fontSize: 24,
    fontWeight: '600',
  },
});
