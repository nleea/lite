"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Badge } from "@/components/atoms/Badge";
import { Button } from "@/components/atoms/Button";
import { useAuth } from "@/lib/auth";

const LINKS = [
  { href: "/companies", label: "Companies" },
  { href: "/products", label: "Products", adminOnly: true },
  { href: "/inventory", label: "Inventory" },
  { href: "/agent", label: "AI Agent", adminOnly: true },
];

export function NavBar() {
  const { role, isAdmin, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  if (!isAuthenticated) return null;

  return (
    <nav className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-indigo-600">Lite Thinking</span>
          {LINKS.filter((l) => !l.adminOnly || isAdmin).map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`text-sm ${
                pathname === l.href ? "font-semibold text-indigo-600" : "text-slate-600"
              } hover:text-indigo-600`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          {role && <Badge>{role}</Badge>}
          <Button
            variant="secondary"
            onClick={() => {
              logout();
              router.push("/login");
            }}
          >
            Log out
          </Button>
        </div>
      </div>
    </nav>
  );
}
