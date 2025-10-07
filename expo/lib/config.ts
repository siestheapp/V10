export const APP_MODE = (process.env.EXPO_PUBLIC_API_MODE || 'supabase').toLowerCase() as 'render' | 'supabase';
export const API_BASE = process.env.EXPO_PUBLIC_API_URL || '';
if (__DEV__) console.log('[v10] mode:', APP_MODE, 'api:', API_BASE ? 'set' : 'unset');
