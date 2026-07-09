"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/atoms/Button";
import { Card } from "@/components/atoms/Card";
import { FormField } from "@/components/molecules/FormField";
import { Label } from "@/components/atoms/Label";
import { PriceInput } from "@/components/molecules/PriceInput";
import { django } from "@/lib/api";
import type { Company, Product } from "@/types";

const EMPTY: Product = {
  code: "",
  name: "",
  characteristics: "",
  company: "",
  quantity: 0,
  prices: [{ currency: "USD", amount: "" }],
};

export function ProductManager() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState<Product>(EMPTY);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    django.get<Company[]>("/companies/").then(setCompanies).catch(() => {});
    django.get<Product[]>("/products/").then(setProducts).catch(() => {});
  };
  useEffect(load, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await django.post("/products/", { ...form, quantity: Number(form.quantity) });
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(String(err));
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <h2 className="mb-4 font-semibold">New product</h2>
        <form onSubmit={submit} className="space-y-3">
          <div>
            <Label htmlFor="company">Company</Label>
            <select
              id="company"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              value={form.company}
              onChange={(e) => setForm({ ...form, company: e.target.value })}
              required
            >
              <option value="">Select…</option>
              {companies.map((c) => (
                <option key={c.nit} value={c.nit}>
                  {c.name} ({c.nit})
                </option>
              ))}
            </select>
          </div>
          <FormField
            label="Code"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            required
          />
          <FormField
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <FormField
            label="Characteristics"
            value={form.characteristics}
            onChange={(e) => setForm({ ...form, characteristics: e.target.value })}
          />
          <FormField
            label="Quantity"
            type="number"
            value={form.quantity}
            onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })}
          />
          <PriceInput prices={form.prices} onChange={(prices) => setForm({ ...form, prices })} />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit">Save product</Button>
        </form>
      </Card>

      <Card>
        <h2 className="mb-4 font-semibold">Products</h2>
        <ul className="space-y-2 text-sm">
          {products.map((p) => (
            <li key={p.id} className="rounded border border-slate-100 p-2">
              <span className="font-mono">{p.code}</span> — {p.name}
              <div className="text-xs text-slate-500">
                {p.prices.map((pr) => `${pr.amount} ${pr.currency}`).join(" · ")}
              </div>
            </li>
          ))}
          {products.length === 0 && (
            <li className="py-4 text-center text-slate-400">No products yet</li>
          )}
        </ul>
      </Card>
    </div>
  );
}
