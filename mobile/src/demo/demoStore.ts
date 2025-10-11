import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import * as FileSystem from 'expo-file-system';
import * as Updates from 'expo-updates';
import * as SQLite from 'expo-sqlite';
import { DevSettings } from 'react-native';
import { IS_DEMO } from '../config';

// Import seed as plain JSON; resolve "local://hero1" at runtime to a bundled image
// eslint-disable-next-line @typescript-eslint/no-var-requires
const seed = require('./seed.json');

const DB_NAME = 'app.db';
const IMG_MAP: Record<string, any> = {
  'local://hero1': require('../../assets/hero1.jpg'),
};

function resolveImage(ref: string) {
  if (typeof ref !== 'string') return ref;
  if (ref.startsWith('local://')) return IMG_MAP[ref] ?? null;
  return { uri: ref };
}

export async function demoSignUp(email: string, _password: string) {
  if (!IS_DEMO) throw new Error('demoSignUp used outside demo mode');
  const user = { email, name: seed.user?.name ?? 'Demo User' };
  await AsyncStorage.setItem('demo:user', JSON.stringify(user));
  await SecureStore.setItemAsync('demo:token', 'demo-token');
  return user;
}

export async function demoSignOut() {
  try { await SecureStore.deleteItemAsync('demo:token'); } catch {}
}

export async function demoBootstrap() {
  if (!IS_DEMO) return;
  const seeded = await AsyncStorage.getItem('demo:seeded');
  // If previously marked seeded but data is missing (e.g., after partial clears), re-seed
  try {
    const [closetRaw, feedRaw] = await Promise.all([
      AsyncStorage.getItem('demo:closet'),
      AsyncStorage.getItem('demo:feed'),
    ]);
    const closetOk = !!closetRaw && Array.isArray(JSON.parse(closetRaw)) && JSON.parse(closetRaw).length > 0;
    const feedOk = !!feedRaw && Array.isArray(JSON.parse(feedRaw)) && JSON.parse(feedRaw).length > 0;
    if (seeded && closetOk && feedOk) return;
  } catch {
    // fall through to reseed
  }
  const closet = (seed.closet || []).map((it: any) => ({ ...it, hero: resolveImage(it.image) }));
  const feed = (seed.feed || []).map((it: any) => ({ ...it, hero: resolveImage(it.image) }));
  await AsyncStorage.multiSet([
    ['demo:closet', JSON.stringify(closet)],
    ['demo:feed', JSON.stringify(feed)],
    ['demo:seeded', '1'],
  ]);
}

export async function demoClearAll() {
  try { await AsyncStorage.clear(); } catch {}
  try { await SecureStore.deleteItemAsync('demo:token'); } catch {}
  // Avoid aggressive native file/DB operations in Expo Go—they can contribute to splash errors.
  // If needed for a dev build, re-enable the blocks below.
  // try {
  //   const db = SQLite.openDatabase(DB_NAME);
  //   // @ts-ignore SDK 51+
  //   if (db.closeAsync) await db.closeAsync();
  //   await FileSystem.deleteAsync(`${FileSystem.documentDirectory}SQLite/${DB_NAME}`, { idempotent: true });
  //   await FileSystem.deleteAsync(FileSystem.documentDirectory + 'demo/', { idempotent: true });
  // } catch {}
  try {
    if (__DEV__ && (DevSettings as any)?.reload) {
      (DevSettings as any).reload();
    } else {
      await Updates.reloadAsync();
    }
  } catch {}
}


