import { CompanyManager } from "@/components/organisms/CompanyManager";
import { PageShell } from "@/components/templates/PageShell";

export default function CompaniesPage() {
  return (
    <PageShell title="Companies">
      <CompanyManager />
    </PageShell>
  );
}
