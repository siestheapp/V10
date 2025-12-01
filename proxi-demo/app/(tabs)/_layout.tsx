import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="find" />
      <Tabs.Screen name="feed" />
      <Tabs.Screen name="closet" />
      <Tabs.Screen name="profile" />
    </Tabs>
  );
}
