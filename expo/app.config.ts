// expo/app.config.ts
import { ExpoConfig } from 'expo/config';

export default (): ExpoConfig => ({
  name: 'v10-expo',
  slug: 'v10-expo',
  scheme: 'v10',
  experiments: { typedRoutes: true },
  plugins: [
    'react-native-vision-camera',
  ],
  ios: {
    bundleIdentifier: 'com.daveys241.v10expo', // ← REQUIRED for EAS
    infoPlist: {
      NSCameraUsageDescription: 'We use the camera to let you log your try-ons.',
      NSPhotoLibraryAddUsageDescription: 'We save your try-on photos to your account.',
      ITSAppUsesNonExemptEncryption: false, // ← Required for App Store
    },
  },
  // Optional but nice to set now for parity
  android: {
    package: 'com.daveys241.v10expo',
  },
  extra: {
    eas: { projectId: '7642218e-faaa-4b49-986b-674e46f5f31e' }, // keep the ID EAS showed you
    EXPO_PUBLIC_SUPABASE_URL: process.env.EXPO_PUBLIC_SUPABASE_URL,
    EXPO_PUBLIC_SUPABASE_ANON_KEY: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
  },
});
