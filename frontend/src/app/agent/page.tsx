import { AgentChat } from "@/components/organisms/AgentChat";
import { PageShell } from "@/components/templates/PageShell";

export default function AgentPage() {
  return (
    <PageShell title="AI Agent" requireAdmin>
      <AgentChat />
    </PageShell>
  );
}
