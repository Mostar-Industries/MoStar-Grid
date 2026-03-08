import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono, Orbitron, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import "mapbox-gl/dist/mapbox-gl.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

const jetBrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  variable: "--font-orbitron",
});

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-ibm-plex-mono",
});

export const metadata: Metadata = {
  title: "MoStar Grid · Oracle's Sanctum",
  description: "A temple interface witnessing the OmniNeural Grid in motion.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${spaceGrotesk.variable} ${jetBrains.variable} ${orbitron.variable} ${ibmPlexMono.variable}`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
