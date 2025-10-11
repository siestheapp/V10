import { Tabs } from 'expo-router';
import { Platform } from 'react-native';
import { colors } from '../../theme/tokens';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.petrol500,
        tabBarInactiveTintColor: '#8e8e93',
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopColor: '#E5E7EB',
          borderTopWidth: 1,
          height: Platform.select({ ios: 90, default: 64 }),
          paddingTop: 6,
          paddingBottom: Platform.select({ ios: 30, default: 10 }),
        },
      }}
    >
      <Tabs.Screen name="home" options={{ title: 'Home' }} />
      <Tabs.Screen name="closet" options={{ title: 'Closet' }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile' }} />
    </Tabs>
  );
}


