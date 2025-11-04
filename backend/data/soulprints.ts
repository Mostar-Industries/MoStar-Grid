// data/soulprints.ts

/**
 * Soulprints = verified identities in the Grid.
 * Clearance scale: 0 (none) → 7 (root authority).
 * Permissions are simple strings so you can gate actions in UI/engine.
 */

export type Permission =
  | 'read'
  | 'write'
  | 'execute'
  | 'validate'
  | 'govern'
  | 'audit'
  | 'burn'
  | 'throttle'
  | 'sign';

export type Role = 'Architect' | 'Guardian' | 'Scribe' | 'Oracle' | 'Intruder';

export interface Soulprint {
  name: Role;
  clearance: number;           // 0..7
  permissions: Permission[];   // allowed operations
}

export type Soulprints = Record<string, Soulprint>;

/** Canon soulprints referenced by your scroll set */
export const soulprints: Soulprints = {
  // Architects (root ops)
  'soulprint-architect-001': {
    name: 'Architect',
    clearance: 7,
    permissions: ['read', 'write', 'execute', 'validate', 'govern', 'audit', 'burn', 'sign'],
  },
  'soulprint-architect-005': {
    name: 'Architect',
    clearance: 7,
    permissions: ['read', 'write', 'execute', 'validate', 'govern', 'audit', 'burn', 'sign'],
  },
  'soulprint-architect-012': {
    name: 'Architect',
    clearance: 7,
    permissions: ['read', 'write', 'execute', 'validate', 'govern', 'audit', 'burn', 'sign'],
  },
  'soulprint-architect-015': {
    name: 'Architect',
    clearance: 7,
    permissions: ['read', 'write', 'execute', 'validate', 'govern', 'audit', 'burn', 'sign'],
  },

  // Guardians (enforcement / runtime)
  'soulprint-guardian-007': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },
  'soulprint-guardian-009': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },
  'soulprint-guardian-011': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },
  'soulprint-guardian-013': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },
  'soulprint-guardian-017': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },
  'soulprint-guardian-018': {
    name: 'Guardian',
    clearance: 5,
    permissions: ['read', 'execute', 'validate', 'throttle', 'burn', 'audit'],
  },

  // Scribes (registry / audit / authorship)
  'soulprint-scribe-004': {
    name: 'Scribe',
    clearance: 4,
    permissions: ['read', 'write', 'validate', 'audit'],
  },
  'soulprint-scribe-008': {
    name: 'Scribe',
    clearance: 4,
    permissions: ['read', 'write', 'validate', 'audit'],
  },
  'soulprint-scribe-010': {
    name: 'Scribe',
    clearance: 4,
    permissions: ['read', 'write', 'validate', 'audit'],
  },
  'soulprint-scribe-014': {
    name: 'Scribe',
    clearance: 4,
    permissions: ['read', 'write', 'validate', 'audit'],
  },
  'soulprint-scribe-020': {
    name: 'Scribe',
    clearance: 4,
    permissions: ['read', 'write', 'validate', 'audit'],
  },

  // Oracles (analysis / signals)
  'soulprint-oracle-006': {
    name: 'Oracle',
    clearance: 6,
    permissions: ['read', 'execute', 'validate', 'audit'],
  },
  'soulprint-oracle-007': {
    name: 'Oracle',
    clearance: 6,
    permissions: ['read', 'execute', 'validate', 'audit'],
  },
  'soulprint-oracle-016': {
    name: 'Oracle',
    clearance: 6,
    permissions: ['read', 'execute', 'validate', 'audit'],
  },

  // Intruders (explicitly blocked)
  'soulprint-intruder-999': {
    name: 'Intruder',
    clearance: 0,
    permissions: [],
  },
  'soulprint-intruder-019': {
    name: 'Intruder',
    clearance: 0,
    permissions: [],
  },
} as const;

/* -------------------------- Tiny helper utilities -------------------------- */

/** Find a soulprint record by id. */
export const getSoulprint = (id: string): Soulprint | undefined => soulprints[id];

/** Check if a soulprint has a specific permission. */
export const hasPermission = (id: string, perm: Permission): boolean => {
  const sp = getSoulprint(id);
  return !!sp && sp.permissions.includes(perm);
};

/** Check if a soulprint meets a minimum clearance. */
export const hasClearance = (id: string, min: number): boolean => {
  const sp = getSoulprint(id);
  return !!sp && sp.clearance >= min;
};

/** Common gate: can this soulprint execute code paths that touch the engine? */
export const canExecute = (id: string): boolean =>
  hasPermission(id, 'execute') && hasClearance(id, 4);
