// data/soulprints.ts
export interface Soulprint {
    id: string;
    identity: string;
    description: string;
}

export const defaultSoulprints: Soulprint[] = [
    { id: "soulprint-001", identity: "Ancestral Guardian", description: "Protector of ancient wisdom and cultural heritage." },
    { id: "soulprint-002", identity: "Knowledge Weaver", description: "Synthesizes diverse knowledge into coherent narratives." },
];
// Add any relevant data or exports here if needed
