# frontend

Next.js (App Router) + TypeScript + Tailwind CSS, organized with **Atomic Design**.

## Atomic structure

```
src/components/
  atoms/       Button · Input · Label · Card · Badge
  molecules/   FormField · PriceInput
  organisms/   NavBar · LoginForm · CompanyManager · ProductManager · InventoryTable · AgentChat
  templates/   PageShell (nav + auth guard)
src/app/       login · companies · products · inventory · agent
src/lib/       api.ts (one client → same Bearer to Django AND FastAPI) · auth.tsx (role from JWT)
```

## Key ideas

- **One token, two backends**: `lib/api.ts` exposes `django.*` and `ai.*` — both
  attach the same `Authorization: Bearer` from login.
- **Role-gated UI**: `auth.tsx` decodes the `rol` claim; admin-only links/pages
  (Products, AI Agent) are hidden and route-guarded for external users.

## Run locally

```bash
cp .env.local.example .env.local
npm install
npm run dev        # http://localhost:3000
```

Views: `/login`, `/companies`, `/products` (admin), `/inventory`, `/agent` (admin).
