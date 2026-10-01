import Shell from "@/components/Shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <link rel="stylesheet" href="/static/css/style.css" />
      <Shell>{children}</Shell>
    </>
  );
}
