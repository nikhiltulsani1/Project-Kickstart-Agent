# Project Kickstart Agent

Describe your project in plain English, get a real GitHub repo back in about a minute and a half.

## Problem

I kept noticing that the first hour of any new project is always the same. Make the folders. Write the throwaway README. Copy the `.env.example` from the last thing I built. Open the same five issues I always open. None of it is hard, it's just friction, and it's the worst possible thing to be doing when you actually have momentum on a new idea.

So I wanted something that takes that whole first hour off my plate.

## Solution

It's a single CLI command. You give it a sentence about what you want to build, and it does the boring setup for you:

1. Works out what you're actually building (the name, the stack, what kind of project it is)
2. Writes a README that fits that project
3. Lays out a starter folder structure with real files in it
4. Spins up the GitHub repo
5. Pushes everything up
6. Opens five issues so you've got a backlog waiting

By the time it's done you've got a repo you can clone and start working in, instead of a blank `git init`.

## Architecture

The whole thing runs as a sequence of steps inside `ProjectKickstartAgent.run()`. Each step either works or fails loudly and stops, which made debugging a lot less painful.

```
main.py  →  ProjectKickstartAgent.run()
               │
               ├── parse_intent()         → ask GPT-4o for name, stack, type, language
               ├── architecture patterns  → a hardcoded list of good defaults (for now)
               ├── generate README        → GPT-4o writes the README
               ├── generate file tree      → GPT-4o returns JSON of path → contents
               ├── create repo            → PyGithub makes the public repo
               ├── push files             → PyGithub commits everything
               └── create issues          → GPT-4o drafts 5 issues, PyGithub opens them
```

Two pieces do most of the work. `CopilotClient` talks to the GitHub Models API and is responsible for anything that needs the model to think. `GitHubClient` wraps PyGithub and handles the repo, the file commits, and the issues.

One thing worth calling out: the architecture-patterns step is hardcoded right now. The plan is to swap that for real retrieval through Azure AI Foundry IQ, but the hackathon version just ships a sensible list.

## Tech Stack

- Python 3.11
- GitHub Models API (GPT-4o) for all the generation
- PyGithub for talking to GitHub
- click for the CLI
- rich for the terminal output
- python-dotenv for config
- Azure AI Foundry IQ for pattern retrieval (still on the to-do list)

## How to Run

Clone it and set up a virtual environment:

```bash
git clone https://github.com/nikhiltulsani1/project-kickstart-agent.git
cd project-kickstart-agent
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy the example env file and fill in your details:

```bash
cp .env.example .env
```

```
GITHUB_TOKEN=your_pat_with_repo_scope
GITHUB_USERNAME=your_github_username
```

The token needs `repo` scope. The same one is used for both the Models API and creating the repo, so you only need the one.

Then point it at an idea:

```bash
python main.py "A FastAPI task manager with Postgres and JWT auth"
```

You'll watch the steps tick by in the terminal, and at the end it hands you a link to the new repo.

## Demo

Coming soon.

## What I Learned

A few things that surprised me building this:

- Making the model return strict JSON and then validating the keys myself was way more reliable than trying to parse freeform text. If the shape is wrong I'd rather fail fast than guess.
- PyGithub behaves differently on an empty repo than one that already has files. The first push throws a 404 on `get_contents`, so I had to special-case that instead of treating it as a real error.
- Splitting "understand the project" from "generate the artifacts" paid off. When something broke I always knew which step did it.

## AI Tools Used During Development

- GitHub Copilot (VS Code) for day-to-day coding
- GitHub Models API, which is also what powers the agent itself
- Claude Code for setting up the project and some of the architecture decisions
- Azure AI Foundry IQ for pattern retrieval (planned)
