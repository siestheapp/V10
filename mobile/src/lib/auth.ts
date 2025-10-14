import { User } from '@supabase/supabase-js';
import { supabase } from './supabase';

/**
 * Links a real Supabase auth user to a demo profile.
 * Creates a demo profile if one doesn't exist for this user ID.
 */
export async function linkToDemoProfile(user: User): Promise<void> {
  try {
    // Check if demo profile already exists for this user
    const { data: existing, error: fetchError } = await supabase
      .from('user_profile')
      .select('*')
      .eq('id', user.id)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      // PGRST116 is "no rows returned", which is expected for new users
      console.error('Error checking existing profile:', fetchError);
      return;
    }

    if (existing) {
      // Profile already exists, no need to create
      console.log('Demo profile already exists for user:', user.id);
      return;
    }

    // Create demo profile with real auth user ID
    const username = user.email?.split('@')[0] || `user${Math.floor(Math.random() * 900) + 100}`;
    
    const { data, error } = await supabase.rpc('api_signup', {
      p_username: username,
      p_user_id: user.id
    });

    if (error) {
      console.error('Error creating demo profile:', error);
      return;
    }

    console.log('Demo profile created:', data);
  } catch (err) {
    console.error('Unexpected error in linkToDemoProfile:', err);
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

