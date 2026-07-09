import { ProductManager } from "@/components/organisms/ProductManager";
import { PageShell } from "@/components/templates/PageShell";

export default function ProductsPage() {
  return (
    <PageShell title="Products" requireAdmin>
      <ProductManager />
    </PageShell>
  );
}
