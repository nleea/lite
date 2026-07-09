"use client";

/**
 * Auth context: holds the decoded role from the JWT so the UI can adapt.
 * The `rol` claim rides inside the token Django issued.
 */

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { getToken, login as apiLogin, setToken } from "@/lib/api";
import type { Role } from "@/types";

interface AuthState {
  role: Role | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

function decodeRole(token: string | null): Role | null {
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return (payload.rol as Role) ?? null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<Role | null>(null);

  useEffect(() => {
    setRole(decodeRole(getToken()));
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      role,
      isAuthenticated: role !== null,
      isAdmin: role === "admin",
      login: async (email, password) => {
        await apiLogin(email, password);
        setRole(decodeRole(getToken()));
      },
      logout: () => {
        setToken(null);
        setRole(null);
      },
    }),
    [role],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
