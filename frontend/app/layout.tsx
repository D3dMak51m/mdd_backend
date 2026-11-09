import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "./providers"; // <-- Импорт

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MDD Control Panel",
  description: "Operational Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers> {/* <-- Обертка */}
          {children}
        </Providers>
      </body>
    </html>
  );
}