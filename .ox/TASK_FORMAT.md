# Ox delegated task format

The Ox worker accepts JSON task files under `.ox/tasks/`.

## Required fields

```json
{
  "id": "task-002",
  "type": "feature_trace",
  "status": "PENDING",
  "repository": "owner/repo",
  "objective": "Bounded forensic objective",
  "questions": ["Question 1"],
  "expected_output": ["Executive summary"],
  "output": ".ox/reports/task-002.md"
}
```

`repository` may be `current` or a public GitHub repository in `owner/repo` form.

## Optional source-selection fields

```json
{
  "ref": "main",
  "include_paths": [
    "src/**",
    "tests/**",
    "docs/architecture.md"
  ],
  "exclude_paths": [
    "assets/**",
    "fixtures/large/**"
  ],
  "focus_terms": [
    "svg",
    "drawingml",
    "convert"
  ],
  "max_files": 50,
  "max_file_bytes": 100000,
  "max_context_chars": 350000
}
```

The worker shallow-clones public reference repositories, uses tracked text files only, discovers files matching `focus_terms` with `git grep`, ranks likely-relevant files, adds a bounded number of neighboring implementation files, and stops at the configured file/context budgets.

## Evidence contract

Ox must distinguish:

- `DIRECT EVIDENCE`
- `INFERENCE`
- `RECOMMENDATION`
- `UNKNOWN / NEEDS MORE SOURCE`

If the bounded package is insufficient, Ox should name the exact paths/symbols required in a follow-up task instead of inventing an answer.

## Task lifecycle

`PENDING` -> `COMPLETE` on success.

`PENDING` -> `FAILED` on runner/API/repository failure. The workflow persists task/report state even when the worker job fails.

## Security

Do not place secrets in tasks. The OpenRouter key is provided only through the GitHub Actions `OPENROUTER_API_KEY` secret.

The current worker supports public reference repositories. Private reference repository cloning should be added later with a separate read-only token or GitHub App installation token.
