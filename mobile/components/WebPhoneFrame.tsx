import { Platform, View } from 'react-native';

export function WebPhoneFrame({ children }: { children: React.ReactNode }) {
  if (Platform.OS !== 'web') return <>{children}</>;
  return (
    <View style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', backgroundColor: '#0f172a10' }}>
      <View style={{ width: 390, height: 844, borderRadius: 46, boxShadow: '0 10px 30px rgba(0,0,0,0.2)', border: '12px solid #111827', overflow: 'hidden', backgroundColor: 'white' }}>
        {children}
      </View>
    </View>
  );
}


