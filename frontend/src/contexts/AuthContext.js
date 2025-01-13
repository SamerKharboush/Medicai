import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenRefreshTimeout, setTokenRefreshTimeout] = useState(null);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token');
    if (token) {
      // Validate token and get user info
      validateToken();
    } else {
      setLoading(false);
    }

    // Cleanup function
    return () => {
      if (tokenRefreshTimeout) {
        clearTimeout(tokenRefreshTimeout);
      }
    };
  }, []);

  const setupTokenRefresh = (token) => {
    try {
      const decodedToken = jwtDecode(token);
      const expirationTime = decodedToken.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      const timeUntilExpiry = expirationTime - currentTime;
      
      // Refresh token 5 minutes before expiry
      const refreshTime = timeUntilExpiry - (5 * 60 * 1000);
      
      if (refreshTime > 0) {
        const timeout = setTimeout(refreshToken, refreshTime);
        setTokenRefreshTimeout(timeout);
      } else {
        // Token is already expired or about to expire
        logout();
      }
    } catch (error) {
      console.error('Error setting up token refresh:', error);
      logout();
    }
  };

  const refreshToken = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/auth/refresh`, null, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
        },
        withCredentials: true
      });

      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('token', access_token);
        setupTokenRefresh(access_token);
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  };

  const validateToken = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      // Check if token is expired
      const decodedToken = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      if (decodedToken.exp < currentTime) {
        throw new Error('Token expired');
      }

      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
        },
        withCredentials: true
      });

      setCurrentUser(response.data);
      setupTokenRefresh(token);
    } catch (error) {
      console.error('Token validation error:', error);
      localStorage.removeItem('token');
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      formData.append('grant_type', 'password');
      
      console.log('Attempting login with credentials:', { email });
      
      const response = await axios.post(`${API_URL}/auth/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
        withCredentials: true
      });

      console.log('Login response:', response.data);

      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('token', access_token);
        setupTokenRefresh(access_token);
        
        // Get user info
        const userResponse = await axios.get(`${API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${access_token}`,
            'Accept': 'application/json',
          },
          withCredentials: true
        });
        
        console.log('User info:', userResponse.data);
        setCurrentUser(userResponse.data);
        return userResponse.data;
      } else {
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Login error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      if (error.response?.status === 401) {
        throw new Error('Invalid email or password');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message === 'Network Error') {
        throw new Error('Unable to connect to the server. Please try again.');
      } else {
        throw new Error('An error occurred during login. Please try again.');
      }
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, userData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error('Registration error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message === 'Network Error') {
        throw new Error('Unable to connect to the server. Please try again.');
      } else {
        throw new Error('Registration failed. Please check your information and try again.');
      }
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    if (tokenRefreshTimeout) {
      clearTimeout(tokenRefreshTimeout);
      setTokenRefreshTimeout(null);
    }
  };

  const value = {
    currentUser,
    login,
    register,
    logout,
    loading,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
