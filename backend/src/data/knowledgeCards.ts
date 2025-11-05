// Fix: Imported KnowledgeCardData to resolve the type error.
import { KnowledgeCardData } from "../types";

export const knowledgeCards: KnowledgeCardData[] = [
  {
    id: "k1",
    title: "Scroll Resonance Logs",
    subtitle: "Covenant Audit System",
    description: "Chronological ledger of scroll executions, their resonance scores, authorship, and soulprint trails.",
    icon: "fa-scroll",
    iconColor: "teal",
    tags: [
      // Fix: Changed color from "gray" to "teal" to match the allowed Tag colors.
      { name: "audit", color: "teal" },
      { name: "resonance", color: "blue" },
      { name: "ethics", color: "red" }
    ],
    updated: "Just now",
    size: "11 MB"
  },
  {
    id: "k2",
    title: "DeepCAL Symbol Models",
    subtitle: "Analytics Core Archive",
    description: "Strategic decision matrices trained on African scenarios. Contains ethical alignment data and inferred policy vectors.",
    icon: "fa-brain",
    iconColor: "green",
    tags: [
      { name: "analytics", color: "green" },
      { name: "ethics", color: "purple" },
      { name: "symbolic-AI", color: "yellow" }
    ],
    updated: "5 mins ago",
    size: "42 MB"
  },
  {
    id: "k3",
    title: "Woo Interpretations",
    subtitle: "Scroll Interpretation Archive",
    description: "All scrolls judged by Woo, with timestamp, proverb, scripture alignment and humor if present.",
    icon: "fa-feather-alt",
    iconColor: "purple",
    tags: [
      { name: "woo", color: "indigo" },
      { name: "scrolls", color: "red" },
      // Fix: Changed color from "gray" to "teal" to match the allowed Tag colors.
      { name: "judgment", color: "teal" }
    ],
    updated: "1 hour ago",
    size: "76 MB"
  }
];