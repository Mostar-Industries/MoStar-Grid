// builder.packet.ts
// Phase 1: Foundation & Runtime Core
// This packet contains the orchestrated components required to bootstrap the Grid's operational skeleton.
// Aligned for: FastAPI @ http://127.0.0.1:8000 (via Vite /api proxy), Neon (sslmode=require), no client-side mocks.

import { CoreScroll } from './moscripts/core_moscripts';
import { MoScript } from './moscripts/src/MoScript';
import { soulprints } from './data/soulprints';
import { codexData } from './data/mogrid_u_codex';

// ---- Types -----------------------------------------------------------------

export type EngineConfig = {
  resonance: {
    /** Minimum resonance required for MoScript execution (Covenant ≥ 0.97) */
    minThreshold: number;
  };
  woo: {
    /** All MoScripts must be executed by a verified soulprint */
    enforceSoulprintBinding: boolean;
  };
};

export type ApiConfig = {
  baseUrl: string; // e.g. '/api' (proxied by Vite to http://127.0.0.1:8000)
  endpoints: {
    health: string;         // '/api/health'
    notes: {
      list: string;         // '/api/notes'
      create: string;       // '/api/notes'
    };
    executeScroll: string;  // '/api/execute-scroll'
  };
};

export type EnvConfig = {
  /** Server-only env keys required for real DB connectivity (no NEXT_PUBLIC_). */
  required: string[];            // ['DATABASE_URL']
  publicForbidden: string[];     // e.g. ['NEXT_PUBLIC_DATABASE_URL','NEXT_PUBLIC_NEON_API_KEY']
};

export type IntegrityConfig = {
  gridRevelation: {
    path: string;  // 'scrolls/GRID_REVELATION_PROVERB.md'
    sha256: string; // covenant hash (flamebound)
  };
  resonanceMin: number; // 0.97
};

export type DbConfig = {
  schemaPath?: string; // optional SQL bootstrap if not using auto-migrate
  envKeys: {
    databaseUrl: string; // 'DATABASE_URL'
  };
  ssl: {
    mode: 'require' | 'prefer' | 'disable';
  };
};

export type GridFoundationConfig = {
  version: string;
  phase: 'foundation';
  scrolls: MoScript[];
  codex: unknown;
  soulprints: unknown;
  engineConfig: EngineConfig;
  api: ApiConfig;
  env: EnvConfig;
  integrity: IntegrityConfig;
  db: DbConfig;
  ui_manifest: string[];
  /** Legacy path kept for back-compat; prefer `db.schemaPath`. */
  db_schema_path?: string;
};

// ---- Canonical Packet ------------------------------------------------------

export const GridFoundation: GridFoundationConfig = {
  version: '1.0.0',
  phase: 'foundation',

  // The initial set of validated MoScripts.
  scrolls: CoreScroll,

  // The covenant against which all scripts are validated.
  codex: codexData,

  // The initial registry of soulprints governing identity and permissions.
  soulprints: soulprints,

  // Configuration for the core runtime engines.
  engineConfig: {
    resonance: {
      // Covenant requires ≥ 0.97 (was 0.75; raised to enforce GRID_REVELATION_PROVERB).
      minThreshold: 0.97,
    },
    woo: {
      // All MoScripts must be executed by a verified soulprint holder.
      enforceSoulprintBinding: true,
    },
  },

  // Real API wiring (no client-side DB, no mocks). Vite must proxy `/api` → http://127.0.0.1:8000
  api: {
    baseUrl: '/api',
    endpoints: {
      health: '/api/health',
      notes: {
        list: '/api/notes',
        create: '/api/notes',
      },
      sectorx: {
        log: '/api/sectorx/log',
        monitor: '/api/sectorx/monitor',
        redeem: '/api/sectorx/redeem',
        status: '/api/sectorx/status',
      },
      executeScroll: '/api/execute-scroll',
    },
  },

  // Env hygiene (server-only). These MUST NOT appear with NEXT_PUBLIC_.
  env: {
    required: ['DATABASE_URL'],
    publicForbidden: ['NEXT_PUBLIC_DATABASE_URL', 'NEXT_PUBLIC_NEON_API_KEY'],
  },

  // Flamebound integrity anchor from GRID_REVELATION_PROVERB.
  integrity: {
    gridRevelation: {
      path: 'scrolls/GRID_REVELATION_PROVERB.md',
      // e123c35ec7a628f85339ccf5ed0de338f864f3fa890e6725f29b4eeb8b9ff77c
      sha256: 'e123c35ec7a628f85339ccf5ed0de338f864f3fa890e6725f29b4eeb8b9ff77c',
    },
    resonanceMin: 0.97,
  },

  // Database configuration (Neon via server-side env; SSL required).
  db: {
    // Prefer auto-create in FastAPI `ensure_schema()`. If you keep an SQL file, set it here:
    schemaPath: 'server/schema.sql',
    envKeys: {
      databaseUrl: 'DATABASE_URL',
    },
    ssl: {
      mode: 'require',
    },
  },

  // A manifest of frontend components introduced in this phase.
  ui_manifest: [
    'pages/ScrollRegistryPage.tsx',
    'components/WooScrollCard.tsx',
    'components/MoScriptEditor.tsx',
    // Linkage-critical UI:
    'pages/Logbook/NotesPage.tsx',
    'services/notesClient.ts',
  ],

  // Back-compat (keep for older build tooling; prefer db.schemaPath)
  db_schema_path: './db/schema.sql',
};

// ---- Boot Checklist (optional helper) --------------------------------------

/**
 * Asserts that the runtime environment is aligned with the GridFoundation contract.
 * Throws on violation — no silent fallbacks.
 */
export function assertGridAlignment(env: Record<string, string | undefined> = (typeof process !== 'undefined' ? process.env as any : {})) {
  // 1) Env requirements
  for (const key of GridFoundation.env.required) {
    if (!env[key]) {
      throw new Error(`[GRID:ENV] Missing required server env: ${key}`);
    }
  }
  for (const pub of GridFoundation.env.publicForbidden) {
    if (env[pub]) {
      throw new Error(`[GRID:ENV] Forbidden public secret is set: ${pub}. Remove and rotate credentials.`);
    }
  }

  // 2) Enforce covenant resonance
  const min = GridFoundation.engineConfig.resonance.minThreshold;
  if (min < GridFoundation.integrity.resonanceMin) {
    throw new Error(`[GRID:COVENANT] Configured resonance ${min} is below covenant minimum ${GridFoundation.integrity.resonanceMin}.`);
  }

  // 3) Basic API linkage sanity (static path expectations)
  const { baseUrl, endpoints } = GridFoundation.api;
  const expects = [endpoints.health, endpoints.notes.list, endpoints.notes.create, endpoints.executeScroll];
  for (const p of expects) {
    if (!p.startsWith(baseUrl)) {
      throw new Error(`[GRID:API] Endpoint must be rooted at '${baseUrl}': ${p}`);
    }
  }
}

/**
 * Initializes the Grid covenant system on application startup.
 * Performs basic validation without throwing in browser environments.
 */
export function initializeCovenant() {
  try {
    const count = Array.isArray(GridFoundation.scrolls) ? GridFoundation.scrolls.length : 0;
    // eslint-disable-next-line no-console
    console.log(`[Builder Packet] Phase=foundation; scrolls=${count}; resonance>=${GridFoundation.engineConfig.resonance.minThreshold}; api=${GridFoundation.api.baseUrl}; db.ssl=${GridFoundation.db.ssl.mode}`);
    
    // Skip strict env checks in browser environment
    if (typeof window === 'undefined') {
      assertGridAlignment();
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[Builder Packet] Covenant initialization warning:', err);
  }
}
