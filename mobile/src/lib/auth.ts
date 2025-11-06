import { User } from '@supabase/supabase-js';
import { supabase } from './supabase';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Links a real Supabase auth user to a profile.
 * Profile is auto-created when user first adds an item via api_claim.
 */
export async function linkToDemoProfile(user: User): Promise<void> {
  // Profile will be auto-created on first api_claim call
  // No need to do anything here - just keeping function for backward compatibility
  console.log('User signed in:', user.email);
  // Keep app-level login check consistent with Supabase session
  // so the router can redirect immediately on next launch.
  try {
    await AsyncStorage.setItem('demo:user', JSON.stringify({ id: user.id, email: user.email }));
  } catch (err) {
    // Non-fatal; routing will still work based on Supabase session
  }
}

/**
 * Gets the current authenticated user's session.
 */
export async function getCurrentUser() {
  const { data: { session }, error } = await supabase.auth.getSession();
  
  if (error) {
    console.error('Error getting session:', error);
    return null;
  }

  return session?.user || null;
}

/**
 * Signs out the current user and clears all local data.
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut();
  
  if (error) {
    console.error('Error signing out:', error);
    throw error;
  }
}

