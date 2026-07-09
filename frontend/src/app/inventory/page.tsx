import { BlockchainPanel } from "@/components/organisms/BlockchainPanel";
import { InventoryTable } from "@/components/organisms/InventoryTable";
import { PageShell } from "@/components/templates/PageShell";

export default function InventoryPage() {
  return (
    <PageShell title="Inventory">
      <div className="space-y-6">
        <BlockchainPanel />
        <InventoryTable />
      </div>
    </PageShell>
  );
}
