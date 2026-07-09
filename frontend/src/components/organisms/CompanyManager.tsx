"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/atoms/Button";
import { Card } from "@/components/atoms/Card";
import { FormField } from "@/components/molecules/FormField";
import { django } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Company } from "@/types";

const EMPTY: Company = { nit: "", name: "", address: "", phone: "" };

export function CompanyManager() {
  const { isAdmin } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [form, setForm] = useState<Company>(EMPTY);
  const [error, setError] = useState<string | null>(null);

  const load = () => django.get<Company[]>("/companies/").then(setCompanies).catch(() => {});
  useEffect(() => {
    load();
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await django.post("/companies/", form);
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(String(err));
    }
  };

  const remove = async (nit: string) => {
    await django.del(`/companies/${nit}/`);
    load();
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {isAdmin && (
        <Card>
          <h2 className="mb-4 font-semibold">New company</h2>
          <form onSubmit={submit} className="space-y-3">
            <FormField
              label="NIT (primary key)"
              value={form.nit}
              onChange={(e) => setForm({ ...form, nit: e.target.value })}
              required
            />
            <FormField
              label="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            <FormField
              label="Address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              required
            />
            <FormField
              label="Phone"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              required
            />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit">Save company</Button>
          </form>
        </Card>
      )}

      <Card className={isAdmin ? "" : "md:col-span-2"}>
        <h2 className="mb-4 font-semibold">Companies</h2>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b text-slate-500">
              <th className="py-2">NIT</th>
              <th>Name</th>
              <th>Phone</th>
              {isAdmin && <th></th>}
            </tr>
          </thead>
          <tbody>
            {companies.map((c) => (
              <tr key={c.nit} className="border-b last:border-0">
                <td className="py-2 font-mono">{c.nit}</td>
                <td>{c.name}</td>
                <td>{c.phone}</td>
                {isAdmin && (
                  <td className="text-right">
                    <Button variant="danger" onClick={() => remove(c.nit)}>
                      Delete
                    </Button>
                  </td>
                )}
              </tr>
            ))}
            {companies.length === 0 && (
              <tr>
                <td colSpan={4} className="py-4 text-center text-slate-400">
                  No companies yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
