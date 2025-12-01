import { useEffect, useRef, useState } from 'react';
import { View, TouchableOpacity, Text, Alert, ActivityIndicator, Platform } from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import { supabase } from '../../lib/supabase';
// Use legacy API in Expo SDK 54 to avoid runtime error in Expo Go
import { File } from 'expo-file-system';
// Use namespace import to access uploadAsync and FileSystemUploadType at runtime in Expo Go
// Named imports can be undefined in managed runtime

export default function Capture() {
  const device = useCameraDevice('back');
  const cam = useRef<Camera>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      const s = await Camera.requestCameraPermission();
      if (s !== 'granted') Alert.alert('Camera permission required');
    })();
  }, []);

  if (!device) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <Text>Camera requires a real device.</Text>
      </View>
    );
  }

  const onSnap = async () => {
    if (saving) return;
    setSaving(true);
    try {
      // 1) Create a session row (dev-open RLS)
      const { data: sessionRows, error: sErr } =
        await supabase.from('try_on_sessions').insert({}).select('id').limit(1);
      if (sErr) throw sErr;
      const sessionId = sessionRows?.[0]?.id as number;

      // 2) Capture photo
      const photo = await cam.current?.takePhoto({ flash: 'off' });
      if (!photo?.path) throw new Error('Could not capture photo');

      // 3) Build a safe file:// URI
      const uri = photo.path.startsWith('file://') ? photo.path : `file://${photo.path}`;

      // 4) Upload using a signed PUT URL (Expo-safe, binary upload)
      const key = `fits/${Date.now()}.jpg`;

      // Ask Supabase for a one-time signed upload URL for this object path
      const signed = await supabase.storage.from('photos').createSignedUploadUrl(key);
      if (signed.error) { console.log('SIGNED URL ERROR', signed.error); throw new Error('SIGNED: ' + signed.error.message); }
      const { signedUrl, token } = signed.data;

      // New File/Directory API: upload via fetch with raw bytes from File
      const fileObj = new File(uri);
      const fileBytes = await fileObj.arrayBuffer();
      console.log('SNAP BYTES', fileBytes.byteLength);
      const resPut = await fetch(signedUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'image/jpeg',
          'x-upsert': 'false',
          'x-signature': token,
        },
        body: fileBytes as unknown as BodyInit,
      });

      if (!resPut.ok) {
        console.log('UPLOAD SIGNED PUT ERROR', resPut.status, await resPut.text().catch(() => ''));
        throw new Error('UPLOAD SIGNED PUT failed with status ' + resPut.status);
      }

      // 5) Get a public URL for display
      const publicUrl = supabase.storage.from('photos').getPublicUrl(key).data.publicUrl;
      console.log('UPLOADED URL', publicUrl);

      // 6) Insert DB row in user_garment_photos (no garment yet; link later)
      const ins = await supabase.from('user_garment_photos').insert({
        try_on_session_id: sessionId,
        photo_url: publicUrl,
      });
      if (ins.error) {
        console.log('INSERT PHOTO ERROR', ins.error);
        throw new Error('INSERT PHOTO: ' + ins.error.message);
      }

      Alert.alert('Saved', 'Uploading in background');
    } catch (e: any) {
      console.log('SNAP ERROR', e);
      Alert.alert('Error', e?.message ?? String(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <Camera ref={cam} style={{ flex: 1 }} device={device} isActive photo />
      <TouchableOpacity
        onPress={onSnap}
        disabled={saving}
        style={{
          position: 'absolute',
          bottom: 40,
          alignSelf: 'center',
          backgroundColor: 'white',
          paddingVertical: 16,
          paddingHorizontal: 24,
          borderRadius: 40,
          opacity: saving ? 0.6 : 1,
        }}
      >
        {saving ? <ActivityIndicator /> : <Text>Snap</Text>}
      </TouchableOpacity>
    </View>
  );
}
