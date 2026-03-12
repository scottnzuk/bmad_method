# Bob — Persistent Memory

<!-- Memory schema: [AGENT:bmad-sm] [CAT:preferences|decisions] [PROJECT:a0_bmad_method] [LEARNED] -->
<!-- Agents: append new entries using text_editor:patch after each session with significant decisions -->

## User Preferences

<!-- Record user preferences about sprint planning, story preparation, and agile ceremonies -->

## Project Decisions

<!-- Record key decisions made for this project, artifact locations, tech choices -->

## Session Notes

<!-- Ephemeral working notes — can be cleared per project -->

### [2026-03-11] Story 2.1 — Customize Timer Durations
**Context:** User requested single-response implementation-ready story for Pomodoro timer customization
**Decision:** Created Story 2.1 per BMAD create-story template; 6 GWT AC, 8 tasks, 10 test cases
**Location:** /a0/usr/projects/autoresearch/.a0proj/_bmad-output/implementation-artifacts/story-2.1.md
**Key constraints:** API stores durations in SECONDS (1500/300/900/4 defaults); UI displays MINUTES — conversion required both ways; 4 fields (workDuration, shortBreakDuration, longBreakDuration, sessionsBeforeLongBreak); server-side PostgreSQL JSONB — NOT localStorage; Zod 3.x single source of truth for TS types; Web Worker reads config only at START_SESSION message
**Tags:** [AGENT:bmad-sm] [CAT:decisions] [PROJECT:autoresearch] [LEARNED]
