"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { NavBar } from "@/components/organisms/NavBar";
import { useAuth } from "@/lib/auth";

interface Props {
  children: React.ReactNode;
  requireAdmin?: boolean;
  title?: string;
}

/** Page template: nav + auth guard + centered content. */
export function PageShell({ children, requireAdmin = false, title }: Props) {
  const { isAuthenticated, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) router.replace("/login");
    else if (requireAdmin && !isAdmin) router.replace("/companies");
  }, [isAuthenticated, isAdmin, requireAdmin, router]);

  if (!isAuthenticated || (requireAdmin && !isAdmin)) return null;

  return (
    <div className="min-h-screen">
      <NavBar />
      <main className="mx-auto max-w-5xl px-4 py-8">
        {title && <h1 className="mb-6 text-2xl font-bold text-slate-900">{title}</h1>}
        {children}
      </main>
    </div>
  );
}
