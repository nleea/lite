"use client";

import { useEffect, useRef, useState } from "react";

import { Badge } from "@/components/atoms/Badge";
import { Button } from "@/components/atoms/Button";
import { Card } from "@/components/atoms/Card";
import { ai } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AnchorResult, ChainInfo, VerifyResult } from "@/types";

function shorten(value: string, size = 10) {
  return value.length > size * 2 ? `${value.slice(0, size)}…${value.slice(-size)}` : value;
}

export function BlockchainPanel() {
  const { isAdmin } = useAuth();
  const [info, setInfo] = useState<ChainInfo | null>(null);
  const [anchor, setAnchor] = useState<AnchorResult | null>(null);
  const [verify, setVerify] = useState<VerifyResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    ai.get<ChainInfo>("/blockchain/info").then(setInfo).catch(() => setInfo({ connected: false }));
  }, []);

  const doAnchor = async () => {
    setBusy(true);
    setError(null);
    try {
      setAnchor(await ai.post<AnchorResult>("/inventory/anchor", {}));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  };

  const doVerify = async (file: File) => {
    setBusy(true);
    setError(null);
    setVerify(null);
    try {
      const form = new FormData();
      form.append("file", file);
      setVerify(await ai.postForm<VerifyResult>("/inventory/verify", form));
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <div className="mb-3 flex items-center gap-2">
        <h2 className="font-semibold">Blockchain integrity</h2>
        {info && (
          <Badge className={info.connected ? "" : "bg-red-100 text-red-700"}>
            {info.connected ? "node online" : "node offline"}
          </Badge>
        )}
      </div>
      <p className="mb-4 text-sm text-slate-500">
        Anchor the inventory PDF&apos;s SHA-256 on-chain, then verify any PDF against it.
        {info?.contract_address && (
          <>
            {" "}Contract{" "}
            <span className="font-mono">{shorten(info.contract_address)}</span> on chain{" "}
            {info.chain_id}.
          </>
        )}
      </p>

      <div className="flex flex-wrap items-center gap-3">
        {isAdmin && (
          <Button onClick={doAnchor} disabled={busy}>
            {busy ? "…" : "Anchor inventory on blockchain"}
          </Button>
        )}
        <Button variant="secondary" onClick={() => fileRef.current?.click()} disabled={busy}>
          Verify a PDF
        </Button>
        <input
          ref={fileRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && doVerify(e.target.files[0])}
        />
      </div>

      {anchor && (
        <div className="mt-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800">
          ✓ Anchored — tx <span className="font-mono">{shorten(anchor.tx_hash)}</span>, block{" "}
          {anchor.block}, at {new Date(anchor.anchored_at * 1000).toLocaleString()}
        </div>
      )}

      {verify && (
        <div
          className={`mt-4 rounded-md p-3 text-sm ${
            verify.anchored ? "bg-emerald-50 text-emerald-800" : "bg-amber-50 text-amber-800"
          }`}
        >
          {verify.anchored
            ? `✓ This PDF is anchored (since ${new Date(verify.anchored_at * 1000).toLocaleString()}).`
            : "✗ This PDF is not anchored (unknown or altered)."}
        </div>
      )}

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </Card>
  );
}
