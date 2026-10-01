import type { Metadata } from "next";
import { SessionProvider } from "@/lib/session";

export const metadata: Metadata = {
  title: { template: "AdderHub | %s", default: "AdderHub" },
  icons: { icon: "/images/favicon.png" },
};

// Same stylesheets as backend/templates/base.html.
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="/static/css/base.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css" />
      </head>
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
