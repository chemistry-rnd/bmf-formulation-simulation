# R&D Forge

Workspace and playbook for turning incomplete project inputs into a coherent, expert-facing Technology Description.

## Repository model

```text
rules/                         global requirements for every project
playbook/                      generation/research workflow
projects/
  <project>/
    input/                     everything supplied by the client/project owner
    requirements.md            current project-specific requirements
    requirements-log.md        append-only requirement/decision history
    research/                  evidence gathered during generation
      competitors.md
      patents.md
      standards.md
      sources.md
    output/
      current.md               latest accepted/review version
      versions/                immutable snapshots
      review-notes.md          issues that should not leak into main document
```

## Core rule

The main Technology Description is written as a complete technology for expert review. Internal uncertainty and work planning belong in research/review files, not in the main document.

Generation is currently manual. CI/LLM automation will implement the same playbook later.

Start with `playbook/technology-description.md`.
