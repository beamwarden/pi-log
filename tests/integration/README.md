# Pi‑Log

Pi‑Log is a serial ingestion and telemetry pipeline designed for reliability,
testability, and long‑term maintainability. It ingests data from a serial device,
parses structured readings, persists them locally, and forwards them to an API
endpoint with retry and batching support.

The project emphasizes clear responsibility boundaries, deterministic behavior,
and documentation that supports future maintainers.

---

## Project Direction

The project is evolving toward a fully automated, reproducible workflow where
every change is validated through tests and continuous integration.

Recent and forward‑looking changes focus on:

- Clear separation of responsibilities across ingestion components
- Explicit behavioral contracts enforced by unit tests
- Deterministic ingestion, retry, and push semantics
- CI‑first development to eliminate manual verification
- Documentation that reflects both current behavior and future intent

All refactors and enhancements are guided by test coverage and documented
contracts to ensure changes remain safe, reviewable, and reversible.

---

## Development Workflow

Pi‑Log uses a standard Git workflow.

Changes are made directly in the repository, validated locally with tests, and
committed normally. Reproducibility and safety are enforced through automated
testing, CI checks, and documented contracts rather than patch‑based workflows.

Key principles:

- Make changes directly in the working tree
- Run tests locally before committing
- Keep commits focused and reviewable
- Let CI enforce correctness and consistency

---

## Continuous Integration and Automation

The project is moving toward a CI‑first workflow where every push and pull
request is automatically validated.

Planned and in‑progress improvements include:

- Mandatory CI checks on every push and pull request
- Automated execution of pre‑commit hooks
- Segmented unit and integration test jobs
- Optional coverage reporting once the test suite stabilizes
- Deployment gates tied to CI status and version tagging

These changes are documented in the CI automation roadmap and are being adopted
incrementally to avoid disrupting active development.

---

## Documentation

Project documentation is organized to support onboarding, debugging, and future
maintenance. Each document has a clear scope and avoids overlapping
responsibilities.

---

## Links

- [Architecture Overview](docs/architecture.md)
- [Ingestion Flow](docs/ingestion-flow.md)
- [SerialReader Contract](docs/serial_reader_contract.md)
- [Testing Strategy and Expectations](docs/testing.md)
- [CI and Automation Roadmap](docs/ci_automation_roadmap.md)
- [Deployment Guide](docs/deployment.md)
- [Operations Guide](docs/operations.md)
- [Release Plan](docs/release-plan.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [System Diagrams](docs/diagrams/)

---

## Development Philosophy

- Prefer explicit contracts over implicit behavior
- Keep components small and testable
- Let tests define and protect behavior
- Document intent, not just implementation
- Optimize for future maintainers

This repository treats refactoring as a first‑class activity and uses automation
to ensure confidence as the system evolves.
