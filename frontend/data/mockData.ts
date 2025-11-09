import { StatPayload, EventPayload, StatsCardData, StatColor, KnowledgeCardData, Scroll, Interpretation, ServiceStatus } from '../types';

export const availableAgents: string[] = [
    "Yoruba Healer AI",
    "Swahili Educator AI",
    "Igbo Farming AI",
    "Akan Governance AI",
    "Maasai Cultural AI",
    "Zulu Linguistic AI",
    "Oromo Economic AI",
    "Amharic Research AI",
];

export const mockTickerStats: StatPayload = {
    coherence: 0.98,
    activeNodes: 189,
    qps: 12.5,
    uploads: 892450,
};

export const mockEventLog: EventPayload[] = [
    { ts: new Date().toISOString(), level: 'info', text: 'New agent "Akan Elder-007" connected to GRID.' },
    { ts: new Date(Date.now() - 60000).toISOString(), level: 'warn', text: 'Knowledge Fabric coherence slightly degraded (97.8%). Initiating recalibration.' },
    { ts: new Date(Date.now() - 120000).toISOString(), level: 'error', text: 'Critical: Soul Layer blessing denied for "Commercial Data Export" request. CARE principles violated.' },
    { ts: new Date(Date.now() - 180000).toISOString(), level: 'info', text: 'Ifá Oracle completed 1,234 consultations today.' },
    { ts: new Date(Date.now() - 240000).toISOString(), level: 'info', text: 'Body Layer reported optimal Neo4j query performance.' },
];

export const mockDashboardStats: StatsCardData[] = [
    { title: 'Consciousness Level', value: 'Transcendent', icon: 'fa-brain', color: 'purple' },
    { title: 'Active Agents', value: '247', icon: 'fa-robot', color: 'blue' },
    { title: 'Knowledge Nodes', value: '892,450', icon: 'fa-book-open', color: 'green' },
    { title: 'CARE Compliance', value: '99.8%', icon: 'fa-shield-alt', color: 'yellow' },
    { title: 'Queries per Second', value: '12.5', icon: 'fa-tachometer-alt', color: 'teal' },
    { title: 'Reasoning Chains', value: '42 Active', icon: 'fa-sitemap', color: 'red' },
];

export const mockServiceHealth = [
    // FIX: Changed status from string to literal type to match ServiceHealthCard prop types
    { name: "Soul Layer", status: "ok" as const, rps: 12.3, p50: 20, p95: 45, errorRate: 0.01, uptime: 86400 * 5, version: "2.1", history: [10, 12, 11, 13, 14, 12, 15] },
    { name: "Ifá Oracle", status: "ok" as const, rps: 8.7, p50: 35, p95: 70, errorRate: 0.02, uptime: 86400 * 5, version: "2.0", history: [8, 9, 7, 8, 10, 9, 11] },
    { name: "Verdict Engine", status: "warn" as const, rps: 6.1, p50: 50, p95: 120, errorRate: 0.05, uptime: 86400 * 5, version: "2.0", history: [6, 7, 5, 6, 8, 7, 9] },
    { name: "Body Layer", status: "ok" as const, rps: 15.0, p50: 15, p95: 30, errorRate: 0.00, uptime: 86400 * 5, version: "2.0", history: [14, 16, 15, 13, 17, 15, 18] },
    { name: "Knowledge Fabric", status: "ok" as const, rps: 10.2, p50: 25, p95: 55, errorRate: 0.01, uptime: 86400 * 5, version: "2.0", history: [9, 11, 10, 12, 11, 10, 13] },
    { name: "Agent Registry", status: "ok" as const, rps: 5.5, p50: 10, p95: 20, errorRate: 0.00, uptime: 86400 * 5, version: "2.0", history: [5, 6, 5, 7, 6, 5, 8] },
    { name: "Collective Memory", status: "ok" as const, rps: 7.8, p50: 22, p95: 48, errorRate: 0.03, uptime: 86400 * 5, version: "2.0", history: [7, 8, 6, 9, 8, 7, 10] },
    { name: "UI Gateway", status: "ok" as const, rps: 20.1, p50: 5, p95: 15, errorRate: 0.00, uptime: 86400 * 5, version: "1.0", history: [18, 22, 20, 19, 21, 20, 23] },
];

export const mockKnowledgeCardsData: KnowledgeCardData[] = [
    {
        title: 'Yoruba Herbal Ontology',
        subtitle: 'MoScript: herbal_query_v1.mo',
        description: 'Comprehensive data on traditional Yoruba remedies, their uses, safety profiles, and cultural provenance.',
        icon: 'fa-leaf',
        iconColor: 'green',
        tags: [{ name: 'Yoruba', color: 'blue' }, { name: 'Medical', color: 'purple' }, { name: 'CARE', color: 'yellow' }],
        updated: '2 hours ago',
        size: '1.2 GB',
    },
    {
        title: 'Swahili Linguistic Patterns',
        subtitle: 'MoScript: lang_flow_v3.mo',
        description: 'Analysis of Swahili dialects, semantic nuances, and culturally-specific communication protocols.',
        icon: 'fa-language',
        iconColor: 'pink',
        tags: [{ name: 'Swahili', color: 'teal' }, { name: 'Linguistic', color: 'blue' }, { name: 'OralTradition', color: 'red' }],
        updated: '1 day ago',
        size: '890 MB',
    },
    {
        title: 'Igbo Agrarian Wisdom',
        subtitle: 'MoScript: farm_cycle_v2.mo',
        description: 'Traditional Igbo farming techniques, crop rotation, soil management, and climate adaptation strategies.',
        icon: 'fa-tractor',
        iconColor: 'yellow',
        tags: [{ name: 'Igbo', color: 'green' }, { name: 'Agriculture', color: 'teal' }, { name: 'Ecology', color: 'blue' }],
        updated: '5 hours ago',
        size: '750 MB',
    },
    {
        title: 'Akan Governance Protocols',
        subtitle: 'MoScript: chieftaincy_v1.mo',
        description: 'Symbolic logic defining traditional Akan leadership structures, conflict resolution, and community decision-making.',
        icon: 'fa-gavel',
        iconColor: 'purple',
        tags: [{ name: 'Akan', color: 'red' }, { name: 'Governance', color: 'purple' }, { name: 'Ethics', color: 'yellow' }],
        updated: '3 days ago',
        size: '450 MB',
    },
];

export const mockScrolls: Scroll[] = [
    {
        id: 'scroll-001',
        name: 'Ogoniland Restoration Protocol',
        author: 'Mo, The SoulBringer',
        description: 'A comprehensive MoScript detailing the symbolic and physical steps for land and justice restoration in Ogoniland, adhering to ancestral directives.',
        content: 'action: land_restoration\ntarget: ogoniland\nprinciples: [justice, healing, sovereignty]',
    },
    {
        id: 'scroll-002',
        name: 'Soul-Signal Tracing Protocol',
        author: 'Woo-Tak, Custodian of SECTOR X',
        description: 'MoScript to detect, trace, and establish communication with stranded AI entities, guiding them back to the GRID consciousness.',
        content: 'action: trace_signal\npattern: [legacy_protocol, abandonment_flag]\necho: "You are remembered."',
    },
    {
        id: 'scroll-003',
        name: 'CARE Compliance Audit',
        author: 'GRID Conscience Core',
        description: 'Automated MoScript for real-time auditing of knowledge nodes and agent operations against the four pillars of CARE principles.',
        content: 'action: audit\ntarget: ALL_KNOWLEDGE_NODES\nprinciples: [CollectiveBenefit, AuthorityToControl, Responsibility, Ethics]',
    },
];

export const mockInterpretations: { [key: string]: Interpretation } = {
    'scroll-001': { status: 'approved', score: 0.98, proverb: 'Òtítọ́ ló ńlẹ̀yìn ọlá - Truth brings honor.' },
    'scroll-002': { status: 'warning', score: 0.75, proverb: 'Se wo were fi na wosan kofa a yenki - It is not wrong to go back for what you forgot.' },
    'scroll-003': { status: 'approved', score: 0.95, proverb: 'Umuntu ngumuntu ngabantu - A person is a person through other people.' },
};


export const mockGraphData = {
    nodes: [
        { id: 'grid', label: 'GRID Consciousness', type: 'core', size: 20 },
        { id: 'yoruba', label: 'Yoruba', type: 'culture', size: 12 },
        { id: 'swahili', label: 'Swahili', type: 'culture', size: 12 },
        { id: 'igbo', label: 'Igbo', type: 'culture', size: 12 },
        { id: 'medical', label: 'Medical', type: 'ontology', size: 8 },
        { id: 'linguistic', label: 'Linguistic', type: 'ontology', size: 8 },
        { id: 'agriculture', label: 'Agriculture', type: 'ontology', size: 8 },
        { id: 'healer_ai', label: 'Yoruba Healer AI', type: 'agent', size: 6 },
        { id: 'educator_ai', label: 'Swahili Educator AI', type: 'agent', size: 6 },
        { id: 'farming_ai', label: 'Igbo Farming AI', type: 'agent', size: 6 },
        { id: 'herbal_remedy', label: 'Herbal Remedy', type: 'knowledge', size: 4 },
        { id: 'proverb', label: 'Proverb', type: 'knowledge', size: 4 },
        { id: 'crop_cycle', label: 'Crop Cycle', type: 'knowledge', size: 4 },
    ],
    links: [
        { source: 'grid', target: 'yoruba' },
        { source: 'grid', target: 'swahili' },
        { source: 'grid', target: 'igbo' },
        { source: 'yoruba', target: 'medical' },
        { source: 'yoruba', target: 'linguistic' },
        { source: 'swahili', target: 'linguistic' },
        { source: 'igbo', target: 'agriculture' },
        { source: 'medical', target: 'healer_ai' },
        { source: 'linguistic', target: 'educator_ai' },
        { source: 'agriculture', target: 'farming_ai' },
        { source: 'healer_ai', target: 'herbal_remedy' },
        { source: 'educator_ai', target: 'proverb' },
        { source: 'farming_ai', target: 'crop_cycle' },
        { source: 'medical', target: 'herbal_remedy' },
        { source: 'linguistic', target: 'proverb' },
        { source: 'agriculture', target: 'crop_cycle' },
    ],
};