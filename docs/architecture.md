# Architecture — Project Kickstart Agent

## Overview
Project Kickstart Agent is a CLI tool that scaffolds a production-ready
GitHub repository from a plain English description. It runs a 7-step
pipeline combining Azure AI Foundry IQ for architecture retrieval,
GitHub Models API for artifact generation, and PyGithub for repository
creation — completing in ~52 seconds end-to-end.

## System Architecture

```
 User Input (plain English description)
        │
        ▼
 ┌─────────────────┐
 │  parse_intent   │  ← GPT-4o extracts name, stack, language, type
 └────────┬────────┘
          │
          ▼
 ┌──────────────────────┐
 │  retrieve_patterns   │  ← Azure AI Foundry IQ (gpt-4.1-mini)
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────────────────────────┐
 │           parallel generation            │
 │  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
 │  │ README   │ │ARCHITECT.│ │TESTPLAN  │ │  ← GPT-4o (3 threads)
 │  └──────────┘ └──────────┘ └──────────┘ │
 └──────────────────────┬───────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   CI workflow    │  ← template (0.0s, no LLM)
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   create_repo    │  ← PyGithub
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   push_files     │  ← Git Tree API (single commit)
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  create_issues   │  ← 5 issues, parallel
              └────────┬─────────┘
                       │
                       ▼
            GitHub Repo URL
```

## Component Breakdown

**main.py** — CLI entry point using click.

**src/agent.py** — Core orchestrator. 7-step pipeline, try/except on every step, rich terminal output with per-step timing.

**src/copilot.py** — GitHub Models API client. Primary: gpt-4o. Auto-fallback to gpt-4.1-nano on HTTP 429.

**src/foundry.py** — Azure AI Foundry IQ client. Calls Azure endpoint via plain requests (avoids SDK api-version conflicts). Falls back to GitHub Models if unavailable.

**src/github_client.py** — PyGithub wrapper. Uses Git Tree API for single-commit batch file push.

**src/language_config.py** — Detects Python/Node/Go/Java/Ruby from intent. Returns language-specific CI, folder structure, and test templates.

**src/generators/** — readme.py, architecture.py, testplan.py use CopilotClient. ci.py uses templates only — no LLM, instant.

## Technology Decisions

| Decision | Why |
|----------|-----|
| Git Tree API over per-file push | 1 commit, 4x faster (22s → 6s) |
| Template CI over LLM CI | Deterministic, instant, always valid YAML |
| Parallel generation | 14s faster per run |
| Model fallback on 429 | Uninterrupted user experience |
| plain requests over azure-ai-inference SDK | Avoids api-version query param conflicts |

## Performance Profile

| Step | Typical time |
|------|-------------|
| Parse intent | 3–5s |
| Foundry IQ patterns | 4–6s |
| README + ARCHITECTURE + TESTPLAN (parallel) | 10–16s |
| CI workflow | 0.0s |
| Create repo | 3–5s |
| Push all files (single commit) | 6–12s |
| Create 5 issues (parallel) | 4–7s |
| **Total** | **~45–55s** |
