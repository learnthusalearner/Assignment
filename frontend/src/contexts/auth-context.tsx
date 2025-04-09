import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '@/types';
import { toast } from "sonner";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('jwt_token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const mockUser: User = { id: '1', email };
      const mockToken = 'mock_jwt_token_' + Math.random().toString(36).substring(2);
      
      localStorage.setItem('jwt_token', mockToken);
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      setUser(mockUser);
      setToken(mockToken);
      
      toast.success("Login successful!");
      return true;
    } catch (error) {
      console.error('Login error:', error);
      toast.error("Login failed. Please check your credentials.");
      return false;
    }
  };

  const signup = async (email: string, password: string): Promise<boolean> => {
    try {
      const mockUser: User = { id: '1', email };
      const mockToken = 'mock_jwt_token_' + Math.random().toString(36).substring(2);
      
      localStorage.setItem('jwt_token', mockToken);
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      setUser(mockUser);
      setToken(mockToken);
      
      toast.success("Account created successfully!");
      return true;
    } catch (error) {
      console.error('Signup error:', error);
      toast.error("Signup failed. Please try again.");
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
    
    setUser(null);
    setToken(null);
    
    toast.info("You've been logged out");
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
