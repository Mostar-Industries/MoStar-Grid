// builder.packet.ts
// Phase 1: Foundation & Runtime Core
// This packet contains the orchestrated components required to bootstrap the Grid's operational skeleton.

import { CoreScroll } from './moscripts/core_moscripts';
import { MoScript } from './moscripts/MoScript';
import { soulprints } from './data/soulprints';
import { codexData } from './data/mogrid_u_codex';

// --- CORE DEFINITIONS ---

/**
 * Defines the foundational elements of the Grid.
 * This is the primary export for the builder to consume.
 */
export const GridFoundation = {
    // The initial set of validated MoScripts.
    scrolls: CoreScroll,

    // The covenant against which all scripts are validated.
    codex: codexData,

    // The initial registry of soulprints governing identity and permissions.
    soulprints: soulprints,

    // Configuration for the core runtime engines.
    engineConfig: {
        resonance: {
            minThreshold: 0.75, // Minimum resonance required for SASS-enabled script execution.
        },
        woo: {
            enforceSoulprintBinding: true, // If true, all SASS scripts must be executed by a verified soulprint.
        },
    },

    // A manifest of frontend components introduced in this phase.
    ui_manifest: [
        'pages/ScrollRegistryPage.tsx',
        'components/WooScrollCard.tsx',
        'components/MoScriptEditor.tsx',
    ],

    // The database schema to be provisioned.
    db_schema_path: './db/schema.sql',
};

console.log(`[Builder Packet] Assembled for Phase 1. ${GridFoundation.scrolls.length} core scrolls loaded. Covenant sourced. Soulprints registered.`);
