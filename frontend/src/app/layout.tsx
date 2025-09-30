import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import React from "react";
import { NuqsAdapter } from "nuqs/adapters/next/app";

const inter = Inter({
  subsets: ["latin"],
  preload: true,
  display: "swap",
});

export const metadata: Metadata = {
  title: "DropAndChat - Chat with Your PDFs",
  description:
    "Upload any PDF and get a shareable link for AI-powered conversations. No signup required. Perfect for document analysis, research, and collaboration.",
  keywords: [
    "PDF chat",
    "document AI",
    "PDF analysis",
    "AI chat",
    "document sharing",
    "PDF questions",
  ],
  authors: [{ name: "DropAndChat" }],
  creator: "DropAndChat",
  publisher: "DropAndChat",
  robots: "index, follow",
  openGraph: {
    title: "DropAndChat - Chat with Your PDFs",
    description:
      "Upload any PDF and get a shareable link for AI-powered conversations. No signup required.",
    type: "website",
    siteName: "DropAndChat",
    images: [
      {
        url: "/logo.png",
        width: 512,
        height: 512,
        alt: "DropAndChat Logo",
      },
    ],
  },
  twitter: {
    card: "summary",
    title: "DropAndChat - Chat with Your PDFs",
    description:
      "Upload any PDF and get a shareable link for AI-powered conversations. No signup required.",
    images: ["/logo.png"],
  },
  icons: {
    icon: "/logo.ico",
    shortcut: "/logo.ico",
    apple: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NuqsAdapter>{children}</NuqsAdapter>
      </body>
    </html>
  );
}
