"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/atoms/Button";
import { Card } from "@/components/atoms/Card";
import { FormField } from "@/components/molecules/FormField";
import { ai, django } from "@/lib/api";
import type { InventoryGroup } from "@/types";

export function InventoryTable() {
  const [groups, setGroups] = useState<InventoryGroup[]>([]);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    django.get<InventoryGroup[]>("/products/inventory/").then(setGroups).catch(() => {});
  }, []);

  const downloadPdf = async () => {
    const blob = await ai.postBlob("/inventory/pdf", {});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "inventory.pdf";
    a.click();
    URL.revokeObjectURL(url);
  };

  const sendPdf = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      await ai.post("/inventory/send", { to_email: email });
      setStatus(`Queued to ${email}`);
      setEmail("");
    } catch (err) {
      setStatus(String(err));
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="font-semibold">Export</h2>
            <p className="text-sm text-slate-500">Download the inventory PDF or email it.</p>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <Button onClick={downloadPdf}>Download PDF</Button>
            <form onSubmit={sendPdf} className="flex items-end gap-2">
              <FormField
                label="Send to email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" variant="secondary">
                Send
              </Button>
            </form>
          </div>
        </div>
        {status && <p className="mt-2 text-sm text-indigo-600">{status}</p>}
      </Card>

      {groups.map((g) => (
        <Card key={g.nit}>
          <h3 className="mb-3 font-semibold">
            {g.name} <span className="font-mono text-sm text-slate-400">({g.nit})</span>
          </h3>
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b text-slate-500">
                <th className="py-1">Code</th>
                <th>Name</th>
                <th>Characteristics</th>
                <th>Prices</th>
              </tr>
            </thead>
            <tbody>
              {g.products.map((p) => (
                <tr key={p.code} className="border-b last:border-0">
                  <td className="py-1 font-mono">{p.code}</td>
                  <td>{p.name}</td>
                  <td>{p.characteristics}</td>
                  <td>{p.prices.map((pr) => `${pr.amount} ${pr.currency}`).join(" · ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ))}
      {groups.length === 0 && <p className="text-center text-slate-400">No inventory yet</p>}
    </div>
  );
}
