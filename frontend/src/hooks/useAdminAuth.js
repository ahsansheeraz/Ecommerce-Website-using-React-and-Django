import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const useAdminAuth = () => {
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated and has admin role
    if (!isAuthenticated) {
      navigate('/admin/login');
    } else if (user?.user_type !== 'admin' && user?.user_type !== 'moderator') {
      navigate('/');
    }
  }, [isAuthenticated, user, navigate]);

  return { isAdmin: user?.user_type === 'admin', isModerator: user?.user_type === 'moderator' };
};