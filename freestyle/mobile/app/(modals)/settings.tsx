import { View, Text, Switch } from 'react-native';
import { colors, space } from '../../theme/tokens';
import { useState } from 'react';

export default function SettingsModal() {
  const [enabled, setEnabled] = useState(true);
  return (
    <View style={{ flex: 1, backgroundColor: (colors as any).background ?? '#fff', padding: space[16] }}>
      <Text style={{ fontSize: 20, fontWeight: '700', color: (colors as any).ink900 ?? '#111827', marginBottom: 12 }}>Settings</Text>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
        <Switch value={enabled} onValueChange={setEnabled} />
        <Text>Enable recommendations</Text>
      </View>
    </View>
  );
}


