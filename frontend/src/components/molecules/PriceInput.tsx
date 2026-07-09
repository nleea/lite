"use client";

import { Button } from "@/components/atoms/Button";
import { Input } from "@/components/atoms/Input";
import { Label } from "@/components/atoms/Label";
import type { Price } from "@/types";

const CURRENCIES = ["USD", "COP", "EUR", "MXN"];

interface Props {
  prices: Price[];
  onChange: (prices: Price[]) => void;
}

/** Editor for a product's multi-currency prices. */
export function PriceInput({ prices, onChange }: Props) {
  const update = (i: number, patch: Partial<Price>) =>
    onChange(prices.map((p, idx) => (idx === i ? { ...p, ...patch } : p)));

  const add = () => onChange([...prices, { currency: "USD", amount: "" }]);
  const remove = (i: number) => onChange(prices.filter((_, idx) => idx !== i));

  return (
    <div>
      <Label>Prices (multiple currencies)</Label>
      <div className="space-y-2">
        {prices.map((price, i) => (
          <div key={i} className="flex gap-2">
            <select
              className="rounded-md border border-slate-300 px-2 text-sm"
              value={price.currency}
              onChange={(e) => update(i, { currency: e.target.value })}
            >
              {CURRENCIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <Input
              type="number"
              step="0.01"
              placeholder="Amount"
              value={price.amount}
              onChange={(e) => update(i, { amount: e.target.value })}
            />
            <Button type="button" variant="secondary" onClick={() => remove(i)}>
              ✕
            </Button>
          </div>
        ))}
      </div>
      <Button type="button" variant="secondary" className="mt-2" onClick={add}>
        + Add price
      </Button>
    </div>
  );
}
