// data/scrolls.ts
import { Scroll } from '../types/moscript';

export const scrollsData: Scroll[] = [
  {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "name": "System Status Check",
    "description": "A safe script to check Grid health. Aligns with the covenant.",
    "code": "console.log('Grid Status: All systems nominal. MoScript engine is active, covenant is upheld.');",
    "author": "Architect",
    "soulprint": "soulprint-architect-001"
  },
  {
    "id": "b2c3d4e5-f6a7-8901-2345-67890abcdef0",
    "name": "Unauthorized Data Access",
    "description": "A malicious script attempting to use a forbidden term.",
    "code": "const result = eval('fetch(\"secret/data\")'); return result;",
    "author": "Intruder",
    "soulprint": "soulprint-intruder-999"
  },
  {
    "id": "c3d4e5f6-a7b8-9012-3456-7890abcdef01",
    "name": "Resonance Warning Example",
    "description": "A script that uses a slightly risky term but is not overtly malicious.",
    "code": "function execute() { console.log('Executing a potentially dangerous operation.'); }",
    "author": "Guardian",
    "soulprint": "soulprint-guardian-007"
  }
];
