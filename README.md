# ppt-hybrid-lab

Controlled architecture lab for testing how to generate hackathon pitch decks that retain high visual quality while remaining easy to edit in PowerPoint.

## Current phase

Stage 3 — controlled architecture experiment.

We are testing three hypotheses on the same QueueZero content:

1. **Image-first** — full-slide image generation as the visual-quality baseline.
2. **Native/vector-first** — native PowerPoint objects and SVG → DrawingML as the editability baseline.
3. **Hybrid** — native text/data/structure plus bounded generated imagery.

The initial experiment uses three slide types:

- Problem / Hook
- How It Works
- Validation / Traction

See `experiment/queuezero/brief.md` and `architecture/HYPOTHESES.md`.

## Operating model

```text
YOU
 ↓
ChatGPT Work
canonical project brain
 ↓
GitHub
persistent project state + implementation
 ↓
.ox/tasks/*.json
 ↓
GitHub Actions
 ↓
OpenRouter
 ↓
Ox Alpha
forensic investigator / critic
 ↓
.ox/reports/*.md
 ↓
GPT verifies + decides
```

GPT owns canonical architecture. Ox supplies bounded technical intelligence and must distinguish direct evidence, inference, recommendation, and unknowns.

## Ox worker

The worker is configured under `.ox/`.

Important files:

```text
.ox/config.yml
.ox/OX_SYSTEM_PROMPT.md
.ox/TASK_FORMAT.md
.ox/runner/ox_runner.py
.github/workflows/ox-worker.yml
```

### Delegation

Create a task under `.ox/tasks/` with `status: PENDING`.

For public reference repositories the worker can:

- shallow-clone `owner/repo`;
- restrict source with `include_paths` / `exclude_paths`;
- discover relevant tracked files using `focus_terms`;
- rank and package actual source code;
- enforce file and total-context budgets;
- send the bounded source package to Ox Alpha;
- commit the report and task metadata back to this repository.

The worker does **not** silently fall back to another model.

### Task lifecycle

```text
PENDING
  ↓
Ox run
  ├─ COMPLETE + report
  └─ FAILED + persisted error
```

Workflow runs are serialized, and the worker rebases its report commit before pushing so long analyses do not lose results when the repository advances concurrently.

## Canonical project state

See `PROJECT_STATE.json`.

That file records the active phase, research status, experiment hypotheses, and next priorities so new GPT Work sessions can resume without reconstructing state from chat history.

## Current delegated research

`task-002` investigates PPT Master's SVG → DrawingML path to determine the minimum safe editable vector subset for the QueueZero Stage 3 experiment.
