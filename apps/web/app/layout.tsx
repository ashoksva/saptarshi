import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAPTARSHI",
  description: "Voice-first council of seven rishi specialists",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
