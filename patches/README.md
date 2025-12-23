# Patch Workflow

This directory stores reproducible Git patches for core refactors, structural
changes, and maintenance operations. Patches provide a disciplined, traceable,
and reversible way to evolve the codebase without relying on manual copy/paste
or ambiguous commit histories.

This workflow is designed for long-term maintainability, onboarding clarity,
and reproducibility across environments (including the Raspberry Pi).

---

## Naming Convention

All patches follow this strict format:

```bash
YYYYMMDD-slug.patch
```

Where:

- `YYYYMMDD` is the date the patch was created (no hyphens)
- `slug` is a short, lowercase, hyphen-separated description
- `.patch` is the required extension

Examples:

```bash
20251223-ingestion-refactor.patch
20251223-logexp-wrapper.patch
20251224-api-cleanup.patch
```

This naming scheme ensures patches sort chronologically and remain easy to
reference in documentation, commit messages, and Makefile helpers.

---

## Creating a Patch

Use the Makefile helper:

```bash
make diff
```

This generates a patch of all uncommitted changes and saves it as:

```bash
patches/YYYYMMDD-changes.patch
```

You may rename the file afterward to give it a more descriptive slug.

---

## Applying a Patch

To apply a patch from this directory:

```bash
make apply-patch FILE=YYYYMMDD-slug.patch
```

This runs:

```bash
git apply patches/<file>
```

Patches must be applied from the repository root.

---

## Verifying a Patch Before Applying

To check whether a patch will apply cleanly:

```bash
git apply --check patches/20251223-ingestion-refactor.patch
```

To preview the changes:

```bash
git apply --stat patches/20251223-ingestion-refactor.patch
```

---

## Reverting a Patch

If a patch introduces issues, revert all uncommitted changes:

```bash
git reset --hard HEAD
```

If the patch was committed, use:

```bash
git revert <commit>
```

---

## When to Use Patches

Use patches for:

- refactors that touch multiple files
- structural changes (e.g., new ingestion architecture)
- reproducible Pi-side fixes
- changes that must be reviewed or shared
- onboarding improvements that should be traceable

Avoid patches for:

- trivial edits
- single-line fixes
- changes that are easier to commit directly

---

## Best Practices

- Keep patches small and focused.
- Document the purpose of each patch in the commit message.
- Never modify files inside `patches/` using a patch.
- Always run tests after applying a patch.
- Commit patches themselves so they become part of the project history.

---

## Example Workflow

```bash
# Make changes
vim app/ingestion_loop.py

# Generate a patch
make diff

# Rename it
mv patches/YYYYMMDD-changes.patch patches/YYYYMMDD-ingestion-refactor.patch

# Apply it on another machine
make apply-patch FILE=20251223-ingestion-refactor.patch

# Run tests
pytest
```

---

This directory is a core part of the project's reproducibility and long-term
maintainability. Treat patches as first-class artifacts.
