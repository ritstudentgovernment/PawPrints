'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { API_URL } from '../api/specialRoute';
import type { UserProfile } from '@/types/UserProfile';

interface AuthContextType {
  isLoggedIn: boolean;
  isAdmin: boolean;
  isCommitteeMember: boolean;
  user: UserProfile | null;
  logIn: (ref?: string) => void;
  logOut: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const checkRoles = (user: UserProfile | null) => {
  if (!user?.roles) {
    return { isAdmin: false, isCommitteeMember: false };
  }

  const hasRole = (role: string) =>
    user.roles.some(r => r.name.toLowerCase() === role.toLowerCase());

  return {
    isAdmin: hasRole('admin'),
    isCommitteeMember: hasRole('committee_member'),
  };
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const isDev =
    (typeof window !== 'undefined' ? (window as any).__ALWAYS_LOGGED_IN__ === true : false);

  const stubUser: UserProfile = {
    username: 'am7504',
    first_name: 'Anjan',
    last_name: 'Maharjan',
    roles: [{ id: 1, name: 'admin', description: 'Administrator' }],
    committees: [],
  };

  const [user, setUser] = useState<UserProfile | null>(
    isDev ? stubUser : null
  );

  useEffect(() => {
    if (isDev) return;

    const fetchUser = async () => {
      try {
        const res = await fetch(
          `${API_URL}/api/v1/users/me`,
          {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        if (!res.ok) {
          setUser(null);
          return;
        }

        const data: UserProfile = await res.json();
        setUser(data);
      } catch (err) {
        console.error('Auth fetch failed:', err);
        setUser(null);
      }
    };

    fetchUser();
  }, [isDev]);

  const logIn = (ref: string = "") => {
    console.log(ref)
    if (!isDev) {
      window.location.href = `${API_URL}/saml2/?ref=${ref}`;
    }
  };

  const logOut = () => {
    setUser(null);

    if (!isDev) {
      window.location.href = `${API_URL}/saml2/logout`;
    }
  };

  const { isAdmin, isCommitteeMember } = checkRoles(user);

  const value: AuthContextType = {
    user,
    isLoggedIn: !!user,
    isAdmin,
    isCommitteeMember,
    logIn,
    logOut,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
};
