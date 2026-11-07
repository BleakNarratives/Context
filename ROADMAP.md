# Roadmap

## North star

Build a lightweight, environment-aware host that lets existing development tools, local models, agents, visualizers, and services work together as composable instruments. Keep their source projects independent. Make the experience welcoming and familiar while exposing the patchbay and evidence when needed.

## Phase 0 — Safe discovery (started)

- [x] Establish project purpose and non-goals.
- [x] Add a local metadata-only inventory prototype.
- [ ] Run it manually on one explicitly selected directory and inspect the output.
- [ ] Add tests for exclusions, symlinks, path handling, and deterministic summaries.
- [ ] Define a user-reviewed manifest format for candidate capabilities.

**Boundary:** discovery is local and read-only. No automatic upload, file-content harvesting, credential access, browser-profile access, or recursive scan of all mounted storage.

## Phase 1 — Prove one composition

- [ ] Inspect existing candidate projects and record their real entry points, runtimes, dependencies, and license.
- [ ] Pick one small workflow that runs on a constrained device (for example: invoke an existing local CLI and render its result).
- [ ] Define a minimal capability manifest: name, version, invocation interface, declared permissions, inputs/outputs, platform needs.
- [ ] Build a local session runner that can call one explicitly enabled adapter and save a provenance record.
- [ ] Demonstrate that the host can use an existing tool without copying or rewriting it.

## Phase 2 — Adapter patchbay

- [ ] Add adapters as isolated modules with explicit permission declarations.
- [ ] Start with local process and local HTTP adapters; add browser integration only through a user-installed extension and supported/authorized interfaces.
- [ ] Use OS credential stores or user-provided secret references; never collect browser cookies or scrape tokens.
- [ ] Add cancellation, timeouts, resource budgets, and clear previews for side effects.
- [ ] Preserve each adapter's native behavior and report failures honestly.

## Phase 3 — Session surface

- [ ] Create a simple session canvas with lateral, stackable nodes and visible data flow.
- [ ] Keep a compact “play” path for common presets and an inspectable advanced patchbay.
- [ ] Show source, transformations, uncertainty, and evidence for generated outputs.
- [ ] Support offline/local workflows first; make remote services opt-in.

## Phase 4 — Field-ready composition

- [ ] Prototype a five-minute local-business workflow using existing scouting, analysis, boardroom, visualization, and pitch components where they actually work.
- [ ] Separate observed facts, estimates, and model-generated suggestions.
- [ ] Produce a human-reviewable presentation and follow-up package; never claim predictive accuracy without evaluation data.
- [ ] Test on phone/Termux and at least one desktop environment before making cross-platform claims.

## Operating rules

1. Reuse before rebuilding, but verify before integrating.
2. No monorepo requirement; integration is through adapters and contracts.
3. No silent installs, network calls, commits, pushes, or data sharing.
4. Device inventories remain local unless the operator reviews and explicitly exports a sanitized artifact.
5. Keep the first vertical slice small enough to run and explain on the actual target device.
