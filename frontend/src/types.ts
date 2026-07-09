export type Role = "admin" | "external";

export interface Company {
  nit: string;
  name: string;
  address: string;
  phone: string;
}

export interface Price {
  currency: string;
  amount: string;
}

export interface Product {
  id?: number;
  code: string;
  name: string;
  characteristics: string;
  company: string; // company NIT
  quantity: number;
  prices: Price[];
}

export interface InventoryGroup {
  nit: string;
  name: string;
  products: Product[];
}

export interface ChatResponse {
  answer: string;
  tools_used: string[];
  sources: { code: string; product_id: number }[];
}

export interface AnchorResult {
  hash: string;
  tx_hash: string;
  block: number;
  anchored_at: number;
}

export interface VerifyResult {
  hash: string;
  anchored: boolean;
  anchored_at: number;
}

export interface ChainInfo {
  connected: boolean;
  chain_id?: number;
  contract_address?: string;
  rpc_url?: string;
  detail?: string;
}
