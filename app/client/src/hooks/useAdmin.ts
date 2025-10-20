
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';

export const useAdmin = () => {
  const { user } = useAuth();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAdminStatus = async () => {
      if (!user) {
        setIsAdmin(false);
        setLoading(false);
        return;
      }

      try {
        const { data, error } = await supabase
          .from('user_profiles')
          .select('is_admin')
          .eq('id', user.id)
          .maybeSingle(); // Use maybeSingle() instead of single() to handle missing profiles

        if (error) {
          // Enhanced error logging
          console.error('❌ Error checking admin status:', {
            message: error.message,
            code: error.code,
            details: error.details,
            hint: error.hint,
            userId: user.id
          });
          console.log('STDOUT ERROR:', JSON.stringify({
            error: error.message,
            code: error.code,
            userId: user.id,
            timestamp: new Date().toISOString()
          }, null, 2));
          setIsAdmin(false);
        } else if (!data) {
          // Profile doesn't exist yet - this is okay for new users
          console.warn(`⚠️ No user profile found for user ${user.id} - profile will be created on first login`);
          setIsAdmin(false);
        } else {
          setIsAdmin(data.is_admin || false);
        }
      } catch (error) {
        console.error('❌ Unexpected error checking admin status:', error);
        setIsAdmin(false);
      } finally {
        setLoading(false);
      }
    };

    checkAdminStatus();
  }, [user]);

  return { isAdmin, loading };
};
