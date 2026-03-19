"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import styles from "./CommandPalette.module.css";

interface CommandItem {
  id: string;
  label: string;
  shortcut?: string;
  icon?: string;
  href?: string;
  action?: () => void;
  category: "Navigation" | "Actions" | "System";
}

const COMMANDS: CommandItem[] = [
  // Navigation
  { id: "home", label: "Go to Sanctum", shortcut: "G H", icon: "◐", href: "/", category: "Navigation" },
  { id: "flame", label: "African Flame", shortcut: "G F", icon: "⚡", href: "/flame", category: "Navigation" },
  { id: "hyperspine", label: "Hyper-Spine Map", shortcut: "G S", icon: "⫷", href: "/hyperspine", category: "Navigation" },
  { id: "grid-vitals", label: "System Health", shortcut: "G V", icon: "◒", href: "/grid-vitals", category: "Navigation" },
  { id: "graph", label: "Graph Explorer", shortcut: "G G", icon: "✦", href: "/graph", category: "Navigation" },
  { id: "chat", label: "Oracle Chat", shortcut: "G C", icon: "⥁", href: "/chat", category: "Navigation" },

  // Actions
  { id: "refresh", label: "Refresh Data", shortcut: "⌘ R", icon: "↻", action: () => window.location.reload(), category: "Actions" },
  { id: "agents", label: "View All Agents", shortcut: "⌘ A", icon: "☥", href: "/grid-vitals", category: "Actions" },
  { id: "moments", label: "View Moments", shortcut: "⌘ M", icon: "✧", href: "/graph", category: "Actions" },

  // System
  { id: "help", label: "Help & Documentation", icon: "?", category: "System" },
  { id: "about", label: "About MoStar Grid", icon: "◈", category: "System" },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const router = useRouter();

  // Toggle with CMD+K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }

      // Close on Escape
      if (e.key === "Escape") {
        setOpen(false);
      }

      // Quick navigation shortcuts
      if (e.altKey && !open) {
        const key = e.key.toLowerCase();
        const navMap: Record<string, string> = {
          h: "/",
          f: "/flame",
          s: "/hyperspine",
          v: "/grid-vitals",
          g: "/graph",
          c: "/chat",
        };

        if (navMap[key]) {
          e.preventDefault();
          router.push(navMap[key]);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, router]);

  const handleSelect = useCallback((item: CommandItem) => {
    if (item.action) {
      item.action();
    } else if (item.href) {
      router.push(item.href);
    }
    setOpen(false);
    setSearch("");
  }, [router]);

  const groupedCommands = COMMANDS.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = [];
    }
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, CommandItem[]>);

  const categories = Object.keys(groupedCommands);

  if (!open) return null;

  return (
    <div className={styles.overlay} onClick={() => setOpen(false)}>
      <div className={styles.container} onClick={(e) => e.stopPropagation()}>
        <Command className={styles.command}>
          <div className={styles.inputWrapper}>
            <span className={styles.searchIcon}>⌘</span>
            <Command.Input
              className={styles.input}
              placeholder="Search commands, pages, actions..."
              value={search}
              onValueChange={setSearch}
              autoFocus
            />
            <kbd className={styles.escKey}>ESC</kbd>
          </div>

          <Command.List className={styles.list}>
            <Command.Empty className={styles.empty}>
              <span className={styles.emptyIcon}>◌</span>
              <p>No commands found for &ldquo;{search}&rdquo;</p>
            </Command.Empty>

            {categories.map((category) => (
              <Command.Group key={category} heading={category} className={styles.group}>
                {groupedCommands[category].map((item) => (
                  <Command.Item
                    key={item.id}
                    onSelect={() => handleSelect(item)}
                    className={styles.item}
                  >
                    <div className={styles.itemLeft}>
                      {item.icon && <span className={styles.icon}>{item.icon}</span>}
                      <span className={styles.label}>{item.label}</span>
                    </div>
                    {item.shortcut && (
                      <kbd className={styles.shortcut}>{item.shortcut}</kbd>
                    )}
                  </Command.Item>
                ))}
              </Command.Group>
            ))}
          </Command.List>

          <div className={styles.footer}>
            <div className={styles.footerHint}>
              <kbd>↑↓</kbd> to navigate
            </div>
            <div className={styles.footerHint}>
              <kbd>↵</kbd> to select
            </div>
            <div className={styles.footerHint}>
              <kbd>Alt</kbd> + <kbd>G</kbd> quick nav
            </div>
          </div>
        </Command>
      </div>
    </div>
  );
}
