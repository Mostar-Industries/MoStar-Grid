# MoStar Grid Architecture - Service-Oriented Refactoring

## Overview
This document describes the service-oriented restructuring of the MoStar Grid repository. The goal of this refactoring was to separate the development workbench from the production runtime and establish clear service boundaries between core components.

## Workbench vs. Deployment Model
- **Workbench (`/home/idona/MoStar/MoStar-Grid`)**: The development source of truth. All refactoring, editing, and version control happen here.
- **Deployment (`/opt/mostar/mostar-grid`)**: The runnable instance. Files are synced from the workbench to this directory via `scripts/deploy.sh`. Production configs (`.env`) and runtime logs reside here.

## Service Boundaries

### 1. Mostar API (`core/mostar-api`)
- **Thin Ingress Wrapper**: `core/mostar-api/main.py`.
- **Purpose**: Acts as the public entry point, handling HTTP request forwarding to the orchestrator layer.

### 2. Grid Orchestrator (`core/grid-orchestrator`)
- **Runtime Core**: `mo_executor.py`, `start_grid.py`, `core_engine/`.
- **Sacred Handshake**: The security and identity layer.
- **Purpose**: Manages agent registration, runtime loops, and service orchestration.

### 3. Idim Ikang Engine (`engines/idim-ikang`)
- **Reasoning Components**: `mind_layer/`, `soul_layer/`, `truth_engine/`, `evidence_machine/`.
- **Intelligence**: symbolic logic and unified proof engines.
- **Purpose**: The "brain" of the grid, handling cognition and ritual verification.

### 4. Neo4j Mindgraph (`memory/neo4j-mindgraph`)
- **Memory Service**: `memory_layer/`, `seed_neo4j.py`.
- **Database Tools**: Specialized Neo4j drivers and seeding scripts.
- **Purpose**: Persistence layer for the grid's consciousness and agent memory.

## Operational Workflow

### Deployment
To sync the workbench to the runtime folder:
```bash
./scripts/deploy.sh
```

### Running Services
Use the provided run scripts which handle `PYTHONPATH` resolution:
- **API**: `./scripts/run-api.sh`
- **Orchestrator**: `./scripts/run-orchestrator.sh`
- **CLI/Vitals**: `./scripts/run-grid.sh --vitals`

## Import Resolution
Internal imports are resolved by setting `PYTHONPATH` to include the service directories. This allows services to import from each other while maintaining loose coupling.
