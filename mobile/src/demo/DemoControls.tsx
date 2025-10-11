import { View, Text, Pressable, Modal } from 'react-native';
import { useState } from 'react';
import { demoBootstrap, demoClearAll } from './demoStore';
import { IS_DEMO } from '../config';

export function useDemoTrigger() {
  const [taps, setTaps] = useState(0);
  const [open, setOpen] = useState(false);
  function registerTap() {
    if (!IS_DEMO) return;
    const n = taps + 1; setTaps(n);
    if (n >= 3) { setOpen(true); setTaps(0); }
    setTimeout(() => setTaps(0), 1200);
  }
  return { open, setOpen, registerTap } as const;
}

export function DemoControls({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!IS_DEMO) return null;
  return (
    <Modal visible={open} animationType="slide" transparent onRequestClose={onClose}>
      <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,.3)', justifyContent: 'flex-end' }}>
        <View style={{ backgroundColor: '#fff', padding: 16, borderTopLeftRadius: 16, borderTopRightRadius: 16 }}>
          <Text style={{ fontWeight: '800', fontSize: 16, marginBottom: 8 }}>Demo Controls</Text>
          <Pressable onPress={async () => { await demoClearAll(); }} style={{ padding: 12, borderRadius: 12, backgroundColor: '#00A3A3', marginBottom: 8 }}>
            <Text style={{ color: '#fff', fontWeight: '700', textAlign: 'center' }}>Reset demo data</Text>
          </Pressable>
          <Pressable onPress={async () => { await demoBootstrap(); onClose(); }} style={{ padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB' }}>
            <Text style={{ fontWeight: '700', textAlign: 'center' }}>Re-seed without reload</Text>
          </Pressable>
          <Pressable onPress={onClose} style={{ padding: 12 }}>
            <Text style={{ textAlign: 'center' }}>Close</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}


