# Multi-Dataset Rank Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the upstream improvements into the pushed `c235c5f` baseline while preserving the male tracker and adding first-class female ranking data plus the upstream short-story recommendation page.

**Architecture:** Keep the existing root `data/` and `api/lastest/` paths as the male compatibility dataset. Move the saved female archive to `data/female/`, generate female aggregates under that root and `api/female/lastest/`, and expose both through a shared dataset configuration consumed by the scraper, builder, and frontend. Run male and female jobs sequentially in one workflow so one commit publishes both datasets.

**Tech Stack:** Python 3.9+, Playwright, static HTML/CSS/JavaScript, GitHub Actions, pytest/PyYAML where available.

**Spec:** `docs/superpowers/specs/2026-11-08-multi-dataset-rank-dashboard-design.md`

## Global Constraints

- Preserve the current male dataset behavior and legacy URLs under `data/` and `api/lastest/`.
- Keep female snapshots, trends, summaries, and APIs physically separate from male data.
- Do not commit `venv/`, `__pycache__/`, or Python bytecode.
- Preserve the male chapter-fetch step; female ranking support does not imply female chapter scraping.
- Use upstream Action upgrades, non-canceling write concurrency, and scraper initialization retry without adopting upstream female-only hard-coded behavior.
- The daily workflow must write both datasets sequentially before one commit and Pages deployment.

## Review Focus

- Dataset selection must change every data URL consistently, including historical dates, trend pages, and book details; test URL resolution for both datasets.
- The female builder must use female file prefixes and female genre prompts while the male builder remains unchanged; test both configuration branches.
- A missing or empty female dataset must produce a clear fallback instead of silently displaying male data; test the failure path.
- Workflow changes must preserve the male chapter-fetch command and must not run two auto-commit jobs concurrently; validate YAML and command presence.
- The short-story page must handle missing API configuration, empty results, malformed URLs, and request failures safely; retain upstream escaping and URL checks.

### Task 1: Merge upstream baseline and preserve the male product

**Files:**
- Modify: `.github/workflows/scrape.yml`
- Modify: `.github/workflows/force_update.yml`
- Modify: `.github/workflows/pages.yml`
- Modify: `scrape_fanqie_ranks.py`
- Modify: `scripts/build_latest.py`
- Create/modify: upstream short-story assets (`shorts.html`, `js/shorts.js`, `css/style.css`)
- Test: baseline syntax and merge result

**Interfaces:**
- Consumes: current `c235c5f` baseline and `upstream/main` at merge time.
- Produces: a merge commit whose tracked code contains upstream short-story and CI improvements while the male paths remain the active compatibility paths.

- [ ] **Step 1: Verify the merge base and clean tracked state**

Run: `git status --short --branch && git rev-parse --short HEAD && git rev-parse --short upstream/main`

Expected: `main` is at `c235c5f`, with no staged or unstaged tracked changes.

- [ ] **Step 2: Merge upstream without committing**

Run: `git merge --no-commit --no-ff upstream/main`

Expected: conflicts are limited to files touched by both branches; do not resolve by accepting the upstream female implementation wholesale.

- [ ] **Step 3: Resolve conflicts by retaining male compatibility and taking safe upstream changes**

Preserve male URL/file-prefix/category behavior and `fetch_category_chapters.py`; take the upstream Action version upgrades, retry helper, concurrency settings, short-story page assets, and tests where they can be adapted cleanly.

- [ ] **Step 4: Run syntax and YAML checks before committing the merge**

Run: `python3 -m py_compile scrape_fanqie_ranks.py scripts/build_latest.py fetch_category_chapters.py` and a YAML parse check for `.github/workflows/*.yml`.

Expected: exit 0 for Python and YAML parsing.

- [ ] **Step 5: Commit the merge**

```bash
git add .
git commit -m "merge: integrate upstream workflow and short recommendations"
```

### Task 2: Add shared dataset configuration and scraper selection

**Files:**
- Create: `fanqie_datasets.py`
- Modify: `scrape_fanqie_ranks.py`
- Modify: `fetch_category_chapters.py` only where dataset paths need explicit male compatibility
- Create: `tests/test_dataset_config.py`
- Modify: `tests/test_scrape_fanqie_ranks.py`

**Interfaces:**
- `get_dataset_config(name: str) -> dict` returns label, rank URL, category prefix, snapshot prefix, and relative data root.
- `scrape_fanqie_ranks.py --dataset male|female` selects the configuration and output directory.
- Existing `run_scraper()` defaults to `male` so local callers remain compatible.

- [ ] **Step 1: Write failing tests for both dataset configurations and invalid names**

Assert male uses `/rank/1_1_1141` and `fanqie_male_new_ranks_`, female uses `/rank/0_1_1139` and `fanqie_female_new_ranks_`, and an unknown dataset raises `ValueError`.

- [ ] **Step 2: Run the focused tests and verify they fail for the missing configuration API**

Run: `pytest -q tests/test_dataset_config.py`

Expected: FAIL because `fanqie_datasets.py` does not yet expose the required API.

- [ ] **Step 3: Implement the minimal configuration module and CLI plumbing**

Keep the existing male defaults and move only URL, prefix, label, and output-root decisions behind the configuration.

- [ ] **Step 4: Run focused tests and the scraper unit tests**

Run: `pytest -q tests/test_dataset_config.py tests/test_scrape_fanqie_ranks.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fanqie_datasets.py scrape_fanqie_ranks.py fetch_category_chapters.py tests/
git commit -m "feat: parameterize male and female rank scrapers"
```

### Task 3: Build independent male and female aggregates and APIs

**Files:**
- Modify: `scripts/build_latest.py`
- Modify: `fanqie_datasets.py`
- Create: `tests/test_build_latest_datasets.py`
- Create/modify: `data/datasets.json` if the builder emits a static manifest

**Interfaces:**
- `scripts/build_latest.py --dataset male|female` selects input snapshots, output root, file prefix, API root, genre groups, keywords, and prompt language.
- Default invocation remains equivalent to the current male build.
- Female output is written under `data/female/` and `api/female/lastest/`.

- [ ] **Step 1: Write failing tests for snapshot discovery and output roots**

Use temporary directories with one male and one female snapshot; assert each dataset discovers only its own prefix and writes its own latest/trend/API files.

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `pytest -q tests/test_build_latest_datasets.py`

Expected: FAIL because the builder is currently hard-coded to the male root and prefix.

- [ ] **Step 3: Implement dataset-aware builder configuration**

Keep male genre groups and prompts; add the upstream female groups and prompts as a separate configuration. Parameterize all paths used by trend, market summary, latest output, dates, and API generation.

- [ ] **Step 4: Run focused tests and an offline build for both datasets**

Run: `pytest -q tests/test_build_latest_datasets.py` and the repository’s offline builder fixture command.

Expected: PASS with no API key required; rule summaries are acceptable.

- [ ] **Step 5: Commit**

```bash
git add fanqie_datasets.py scripts/build_latest.py tests/test_build_latest_datasets.py data/datasets.json api/
git commit -m "feat: build isolated male and female rank datasets"
```

### Task 4: Add the unified dataset switcher and short-story navigation

**Files:**
- Modify: `index.html`
- Modify: `trend.html`
- Modify: `book.html`
- Modify: `js/app.js`
- Modify: `js/trend.js`
- Modify: `js/book.js`
- Modify: `css/style.css`
- Add/keep: `shorts.html`, `js/shorts.js`
- Create: `tests/test_frontend_dataset_links.py`

**Interfaces:**
- Dataset query parameter: `?dataset=male` or `?dataset=female`; invalid/missing values default to male.
- Shared client configuration maps each dataset to its latest file, dates file, trend directory, market summary, and API base.
- Navigation links preserve the active dataset; short-story navigation is dataset-independent.

- [ ] **Step 1: Write failing checks for dataset URL resolution**

Assert that both dataset values produce distinct latest/date/trend/API URLs and that invalid values fall back to male.

- [ ] **Step 2: Run the frontend checks and verify failure**

Run: `pytest -q tests/test_frontend_dataset_links.py`

Expected: FAIL because the current JavaScript hard-codes the male paths.

- [ ] **Step 3: Implement the dataset switcher and path resolution**

Add a visible male/female selector, update title/subtitle text, preserve query parameters across trend/book links, and keep legacy male URLs working.

- [ ] **Step 4: Integrate the upstream short-story page and safe navigation**

Keep upstream escaping, abort handling, empty-state rendering, and URL validation; add the page link to the dashboard and trend navigation.

- [ ] **Step 5: Run frontend checks and static HTML/script checks**

Run: `pytest -q tests/test_frontend_dataset_links.py` plus a check that all referenced local scripts/files exist.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add index.html trend.html book.html js/ css/ shorts.html tests/test_frontend_dataset_links.py
git commit -m "feat: switch between male female rankings and add shorts"
```

### Task 5: Run both datasets in GitHub Actions

**Files:**
- Modify: `.github/workflows/scrape.yml`
- Modify: `.github/workflows/force_update.yml`
- Modify: `.github/workflows/pages.yml`
- Modify: `README.md`
- Modify: `README_EN.md`

**Interfaces:**
- Daily workflow runs male and female scraping/building sequentially and commits `data` plus `api` once.
- Force-update workflow accepts the existing date input and rebuilds both datasets.
- Male chapter fetching remains conditional on a fresh male scrape.

- [ ] **Step 1: Add workflow validation checks**

Validate YAML parsing and assert both `--dataset male` and `--dataset female` commands, the male chapter-fetch command, non-canceling concurrency, and upgraded Action versions are present.

- [ ] **Step 2: Run the checks and verify failure against the single-dataset workflow**

Run: `pytest -q tests/test_workflows.py`.

Expected: FAIL because the current workflow runs only the male dataset.

- [ ] **Step 3: Implement sequential two-dataset workflow execution**

Use the upstream checkout/sync/concurrency/action versions while preserving the male chapter fetch and one auto-commit/deployment sequence.

- [ ] **Step 4: Update documentation with both dataset URLs and the short-story page**

- [ ] **Step 5: Run workflow validation**

Run: `pytest -q tests/test_workflows.py` and the full test suite.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows README.md README_EN.md tests/test_workflows.py
git commit -m "ci: publish male and female datasets together"
```

### Task 6: Full verification and push

**Files:**
- Verify all modified files and generated output.

- [ ] **Step 1: Run the complete test suite and Python syntax checks**

Run: `pytest -q` and `python3 -m compileall -q .` with ignored virtual-environment paths excluded.

Expected: all tests pass and syntax compilation exits 0.

- [ ] **Step 2: Verify the generated dataset manifests and representative JSON files**

Check one male and one female latest file, date index, trend file, and API index; verify JSON parsing and distinct dataset labels.

- [ ] **Step 3: Inspect the final diff and working tree**

Run: `git diff --check`, `git status --short --branch`, and `git log --oneline -8`.

Expected: no whitespace errors; only intended files changed; ignored environments remain ignored.

- [ ] **Step 4: Push the integrated branch**

```bash
git push origin main
```

- [ ] **Step 5: Verify the remote commit and Actions workflow file**

Run: `git fetch origin main && git rev-parse --short origin/main` and inspect the GitHub Actions workflow page.

Expected: remote `main` matches local `HEAD`; manual workflow dispatch is available for the two-dataset run.
