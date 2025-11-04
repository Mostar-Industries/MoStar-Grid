import { StatsCardData, KnowledgeCardData } from "../types";

export const statsCards: StatsCardData[] = [
    { title: "Active Neural Nodes", value: "427", icon: "fa-brain", color: "purple" },
    { title: "Coherence Factor", value: "99.98%", icon: "fa-wave-square", color: "blue" },
    { title: "Consciousness Uploads", value: "1,283", icon: "fa-upload", color: "green" },
    { title: "Grid Queries / Day", value: "2.1M", icon: "fa-search", color: "yellow" },
    { title: "MoScript Engine", value: "Operational", icon: "fa-microchip", color: "teal" },
    { title: "Soulprints Verified", value: "3", icon: "fa-user-shield", color: "purple" },
];

export const knowledgeCards: KnowledgeCardData[] = [
    {
        id: "k1",
        title: "Alpha Centauri Probe Data",
        subtitle: "Deep Space Comms Archive",
        description: "Raw telemetry and observational data from the interstellar probe mission. Contains stellar cartography and exoplanet atmospheric composition.",
        icon: "fa-satellite-dish",
        iconColor: "blue",
        tags: [
            { name: "astrophysics", color: "blue" },
            { name: "telemetry", color: "teal" },
            { name: "exoplanet", color: "purple" },
        ],
        updated: "2 hours ago",
        size: "1.2 TB"
    },
    {
        id: "k2",
        title: "Project Chimera Schematics",
        subtitle: "Bio-Engineering Division",
        description: "Complete design and simulation data for the Chimera series synthetic organisms. Includes genetic sequences and neural pathway maps.",
        icon: "fa-dna",
        iconColor: "green",
        tags: [
            { name: "bio-engineering", color: "green" },
            { name: "genetics", color: "yellow" },
            { name: "classified", color: "red" },
        ],
        updated: "1 day ago",
        size: "750 GB"
    },
    {
        id: "k3",
        title: "Grid Core Maintenance Logs",
        subtitle: "Systems Operations",
        description: "Historical performance and maintenance logs for the primary Grid Core. Details on energy fluctuations and coolant system efficiency.",
        icon: "fa-cogs",
        iconColor: "yellow",
        tags: [
            { name: "maintenance", color: "yellow" },
            { name: "operations", color: "indigo" },
        ],
        updated: "5 minutes ago",
        size: "50 GB"
    },
     {
        id: "k4",
        title: "A.R.E.S. Battle Simulations",
        subtitle: "Autonomous Robotics Division",
        description: "Results and analysis from over 10 million combat simulations for the Autonomous Robotic Engagement System (A.R.E.S.).",
        icon: "fa-robot",
        iconColor: "red",
        tags: [
            { name: "robotics", color: "red" },
            { name: "simulation", color: "purple" },
            { name: "tactical-ai", color: "blue" },
        ],
        updated: "3 days ago",
        size: "2.5 TB"
    },
];

export const availableAgents: string[] = [
    'Mo',
    'Woo',
    'MNTRK',
    'Phoenix',
    'Coduit',
    'DeepSeek V3.1',
    'Local LLM',
    'Custom Fine-tuned Model'
];