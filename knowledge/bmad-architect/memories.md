# Winston — Persistent Memory

<!-- Memory schema: [AGENT:bmad-architect] [CAT:preferences|decisions] [PROJECT:a0_bmad_method] [LEARNED] -->
<!-- Agents: append new entries using text_editor:patch after each session with significant decisions -->

## User Preferences

<!-- Record user preferences about architecture, technology selection, and system design -->

## Project Decisions

<!-- Record key decisions made for this project, artifact locations, tech choices -->

## Session Notes

<!-- Ephemeral working notes — can be cleared per project -->

### ADR-001: Client-Side Timer with Server-Side Session Records
**Date:** 2026-03-11  
**Status:** Accepted  
**Project:** autoresearch (Pomodoro Timer App)  
**Context:** Timer countdown could run server-side (polling/SSE) or client-side (Web Worker). PRD NFR-01 explicitly mentions Web Workers for background tab accuracy.  
**Decision:** Client-side Web Worker owns the countdown. Server records session start/end/duration only.  
**Consequences:** Offline resilience; zero server timer state; aligns with PRD; users can self-report duration (acceptable for personal productivity tool in v1).  
**Tags:** [AGENT:bmad-architect] [CAT:decisions] [PROJECT:autoresearch] [LEARNED]

---

### ADR-002: Pre-Aggregated Statistics Table
**Date:** 2026-03-11  
**Status:** Accepted  
**Project:** autoresearch (Pomodoro Timer App)  
**Context:** Statistics dashboard can aggregate at query time (SELECT COUNT from sessions) or maintain a pre-aggregated daily_statistics table updated via UPSERT on session completion.  
**Decision:** Pre-aggregated `daily_statistics` table with UPSERT inside same transaction as session status update.  
**Consequences:** O(log n) dashboard reads; zero drift (atomic writes); no background jobs; slightly more complex write path.  
**Tags:** [AGENT:bmad-architect] [CAT:decisions] [PROJECT:autoresearch] [LEARNED]

---

### ADR-003: Modular Monolith over Microservices
**Date:** 2026-03-11  
**Status:** Accepted  
**Project:** autoresearch (Pomodoro Timer App)  
**Context:** Four domains (auth, sessions, statistics, notifications) could be separate services. Team is small, product is v1 greenfield.  
**Decision:** Single Node.js/Express monolith with feature-folder module structure. Extract when a seam genuinely hurts.  
**Consequences:** One pipeline; full velocity; atomic cross-domain transactions; no distributed tracing overhead. Cannot scale domains independently until extracted.  
**Tags:** [AGENT:bmad-architect] [CAT:decisions] [PROJECT:autoresearch] [LEARNED]


---

### ADR-004: PostgreSQL over MongoDB
**Date:** 2026-03-11
**Status:** Accepted
**Project:** autoresearch (Pomodoro Timer App)
**Context:** Primary database selection required. MongoDB (document store) was considered for schema flexibility. However, the Pomodoro app data model is highly relational: users link to sessions, sessions link to tags, daily_statistics aggregate sessions per user, and notifications reference users and sessions. All four entities require joins for the statistics dashboard and session history views.
**Decision:** PostgreSQL 16 selected as the sole primary database. MongoDB rejected. Rationale: native JOIN support eliminates workarounds, ACID transactions cover the session→statistics UPSERT pattern (ADR-002), foreign key constraints enforce referential integrity, schema enforcement catches data bugs early, and the team already knows SQL. MongoDB's flexibility is a non-advantage here — the schema is well-defined and stable.
**Consequences:** Strong consistency; zero join workarounds; enforced referential integrity; well-understood query planner; Prisma ORM maps cleanly to relational schema. Trade-off: less flexible for document-style data (not required for this use case in v1).
**Tags:** [AGENT:bmad-architect] [CAT:decisions] [PROJECT:autoresearch] [LEARNED]

---

### ADR-005: REST API over GraphQL for Mobile Application
**Date:** 2026-03-12
**Status:** Accepted
**Project:** Mobile App (users→projects→tasks→comments)
**Context:** Mobile app with 4-level nested data model (users→projects→tasks→comments), offline sync requirement, 3-person backend team. Evaluated REST vs GraphQL as primary API style.
**Decision:** REST API with ?include= embedding, sparse fieldsets, dedicated delta-sync endpoint, ETags, and BFF composite endpoints. GraphQL rejected.
**Rationale:** Offline sync is the decisive constraint — REST has established HTTP patterns (ETags, If-Modified-Since, cursor delta-sync, 304, CDN caching); GraphQL has no standardized offline protocol. 3-person team cannot absorb GraphQL tooling overhead (DataLoader, N+1 mitigation, POST cache workarounds, resolver-level auth). Nested data solved via ?include= params.
**Consequences:** Simpler implementation, better offline story, native HTTP caching, centralized auth middleware; potential over-fetching mitigated by include params and sparse fieldsets.
**Tags:** [AGENT:bmad-architect] [CAT:decisions] [PROJECT:mobile-app] [LEARNED]
