# SauceDemo AI-Assisted QA — Submission Document

**Application:** https://www.saucedemo.com/  
**Primary account:** `standard_user` / `secret_sauce`  
**Date:** 6 October 2026  

---

## Task A — AI-Assisted Exploratory Testing

**Goal:** Use AI to accelerate exploration of SauceDemo — not to dump a traditional test-case list. AI proposed risks and edge cases; each idea was converted into a live check, then kept, changed, or discarded based on what the app actually does for `standard_user`.

### Approach

- Explore live app at https://www.saucedemo.com/ with `standard_user` / `secret_sauce`
- Ask AI for high-risk journeys, functional risks, edge cases, UX/a11y, performance, and follow-up questions
- Execute useful suggestions as real tests in the browser
- Challenge or discard ideas that are irrelevant, wrong, redundant, or unsupported by the app

### Highest-risk user journeys identified

| Journey | Why it mattered | Session outcome |
|---------|-----------------|-----------------|
| Purchase / checkout integrity | Money, order completion, and validation sit here | Highest risk — multiple critical defects (see Task B) |
| Cart state (add/remove/empty/badge) | Empty-cart checkout and no qty control change purchase semantics | High risk — empty checkout confirmed |
| Dynamic Catalog (Lazy / Spinner / Slider) | Newer surface with loading, duplicates, a11y, browse-only UX | High risk — duplicate SKUs confirmed |
| Auth + session guards | Protects all post-login pages | Medium — mostly passed |
| Catalog browse + sort | Core discovery path | Lower risk — sort/tax healthy |

### What was actually tested (live)

- Login: empty submit, username-only, password-only, `locked_out_user`
- Inventory: price sort lohi/hilo; add/remove; cart badge
- Cart: quantity editability, localStorage cart model, empty-cart checkout
- Checkout: whitespace-only names/zip, invalid zip (`!!!`), tax math, Finish, Back then re-Finish
- Order complete: thank-you page; Generate PDF order button state
- Auth guards: logout then direct URL to `/inventory.html` and `/checkout-step-one.html`
- Dynamic Catalog: Lazy Load scroll/duplicates, Spinner page, Slider dots/a11y

### Exploration outcomes (summary)

**Confirmed bugs** (full write-ups in Task B): empty cart $0 order; whitespace-only checkout info; zip `!!!` accepted; Back allows re-Finish; Lazy Load duplicate Red T-Shirt (L).

**Confirmed passes:** tax math 8%; price sort; cart badge; route guards; `locked_out_user` blocked.

**Limitations (not defects):** Dynamic Catalog browse-only; cart qty cannot exceed 1.

### Representative AI prompts (Task A deliverable)

#### Prompt 1 — Risk prioritization
**Prompt:** “For SauceDemo (saucedemo.com), identify the highest-risk user journeys for standard_user. Prioritize by business/impact risk, not by page count. Challenge assumptions that only apply to real e-commerce backends.”  
**Purpose:** Focus the session on risk instead of generating a generic test-case list.  
**Useful AI output:** Ranked checkout/cart as top risk; auth/session next; warned payment may be mocked.  
**What I tested / changed / rejected / validated:** Validated checkout + cart as highest risk. Kept auth as medium. Rejected deep payment/fraud testing after confirming SauceCard is fake.

#### Prompt 2 — Checkout edge cases
**Prompt:** “Generate functional risks and edge cases for SauceDemo checkout (info form → overview → finish). Include empty cart, whitespace, postal formats, back-button after complete, and tax math. Mark which need live proof.”  
**Purpose:** Convert AI edge-case ideation into concrete checkout experiments.  
**Useful AI output:** Empty-cart checkout, whitespace names, invalid zip, tax rounding, re-submit via Back.  
**What I tested / changed / rejected / validated:** Validated as bugs: empty cart $0 order, whitespace accepted, zip `!!!` accepted, Back+Finish replay. Validated as pass: 8% tax.

#### Prompt 3 — Dynamic Catalog scout
**Prompt:** “After login, the menu has Dynamic Catalog → Lazy Load / Spinner / Slider. What should I explore for data integrity, loading UX, a11y, and purchase flow gaps? Discard ideas if those pages are browse-only.”  
**Purpose:** Investigate a less obvious surface with AI as a scout.  
**Useful AI output:** Infinite-scroll duplicates, spinner leftovers, slider keyboard/a11y, missing Add to cart.  
**What I tested / changed / rejected / validated:** Validated duplicate Red T-Shirt (L); slider a11y-current on all dots; browse-only. Treated missing Add to cart as limitation, not defect.

#### Prompt 4 — Login / session risks (scoped)
**Prompt:** “Propose login/UX and session risks for SauceDemo: empty fields, partial credentials, locked_out_user, and direct URL access after logout. Ignore SQL injection unless the UI gives a real reason to prioritize it.”  
**Purpose:** Cover auth without wasting time on generic security folklore.  
**Useful AI output:** Required-field messaging, locked-out persona, route guards, misleading error chrome.  
**What I tested / changed / rejected / validated:** Validated required-field errors, locked_out blocked, route guards. Confirmed UX issue: both fields show red X when only one is wrong. Rejected SQL-injection deep dive.

#### Prompt 5 — Explicit discard pass
**Prompt:** “Which of these AI ideas should I discard for SauceDemo and why: multi-currency, stock limits, email confirmation, multi-user cart sync, real card processing? Base the answer on what the app actually exposes.”  
**Purpose:** Force explicit rejection of AI noise before writing findings.  
**Useful AI output:** Discard list with rationale tied to missing UI/capabilities.  
**What I tested / changed / rejected / validated:** All five discarded after live observation. Prevented false findings in the report.

### AI suggestions discarded

| Suggestion | Why discarded |
|------------|---------------|
| Deep payment / fraud / card-processor tests | Payment is mocked (“SauceCard #31337”) |
| SQL injection / auth bypass as primary focus | Demo cookie session; not worth session budget |
| i18n / multi-currency checkout | No locale or currency switcher |
| Inventory stock / oversell limits | No stock counters in UI/cart model |
| Multi-user cart sync / concurrency | Cart is localStorage product-ID list only |
| Email / order confirmation delivery | No email field at checkout |

---

## Task B — Defect Discovery & Reporting

Quality over quantity. Findings below were reproduced on `standard_user` and classified only when impact + unexpectedness were clear for a purchase demo. Unusual demo personas (`problem_user`, etc.) were **not** treated as defects of the primary path unless they also affect `standard_user`.

### DEF-01 — Empty cart can complete checkout ($0 order)

| Field | Detail |
|-------|--------|
| **Title** | Checkout allowed with empty cart produces a successful $0 order |
| **Severity / Priority** | **Critical / P0** |
| **Steps** | 1. Login as `standard_user`. 2. Open cart with no items (or Reset App State / clear cart). 3. Click **Checkout**. 4. Enter any First/Last/Zip. 5. Continue → Finish. |
| **Expected** | Checkout disabled or blocked when cart is empty; order cannot complete. |
| **Actual** | Checkout proceeds. Overview shows Item total $0 / Tax $0.00 / Total $0.00. Finish shows “Thank you for your order!” |
| **Impact** | Inflated order metrics, meaningless “successful” orders, broken business rule that a purchase requires items. |
| **Classification note** | Not a persona quirk — reproducible on `standard_user`. Enabling Checkout on an empty cart is a product rule failure, not intentional demo flavor. |
| **Evidence** | `evidence/DEF01-empty-cart-checkout-enabled.png`, `DEF01-empty-order-overview-zero-total.png`, `DEF01-empty-order-thank-you.png` |

### DEF-02 — Whitespace-only checkout identity accepted

| Field | Detail |
|-------|--------|
| **Title** | Checkout “Your Information” accepts whitespace-only First/Last/Zip |
| **Severity / Priority** | **Critical / P0** |
| **Steps** | 1. Login, add any item, Checkout. 2. Enter spaces only in First Name, Last Name, Zip. 3. Continue. |
| **Expected** | Validation error; trim + reject empty-after-trim values. |
| **Actual** | Continues to Overview with no error. |
| **Impact** | Orders with unusable customer identity; shipping/fulfillment would fail in a real system. |
| **Classification note** | App *does* validate truly empty fields (“First Name is required”), so accepting spaces is an incomplete validation bug, not “no validation by design.” |
| **Evidence** | `evidence/DEF02-whitespace-only-checkout-fields.png`, `DEF02-whitespace-accepted-overview.png` |

### DEF-03 — Postal code accepts invalid format (`!!!`)

| Field | Detail |
|-------|--------|
| **Title** | Zip/Postal Code accepts non-postal values such as `!!!` |
| **Severity / Priority** | **High / P1** |
| **Steps** | 1. Login, add item, Checkout. 2. Enter valid names and Zip `!!!`. 3. Continue. |
| **Expected** | Format validation (e.g. alphanumeric postal pattern) rejects `!!!`. |
| **Actual** | Accepted; Overview reached. |
| **Impact** | Invalid shipping addresses; higher support/return cost in production analogues. |
| **Classification note** | Demo may intentionally be loose, but field is labeled Zip/Postal Code and other fields are validated — format check is a reasonable expectation. |
| **Evidence** | `evidence/DEF03-invalid-postal-code.png` |

### DEF-04 — Browser Back after completion allows re-Finish

| Field | Detail |
|-------|--------|
| **Title** | After order complete, Back returns to Overview with Finish still active |
| **Severity / Priority** | **High / P1** |
| **Steps** | 1. Complete a checkout to Thank You page. 2. Press browser **Back**. 3. Observe Finish still available; click Finish again. |
| **Expected** | Overview should be invalidated / redirected; Finish must not re-submit. |
| **Actual** | Overview + Finish remain usable (duplicate completion path). |
| **Impact** | Duplicate order submissions, confused order state, audit noise. |
| **Classification note** | Classic post-redirect-get / history issue; confirmed on `standard_user`, not an exotic persona bug. |
| **Evidence** | `evidence/DEF04-back-allows-refinish.png` |

### DEF-05 — Dynamic Catalog Lazy Load shows duplicate SKUs

| Field | Detail |
|-------|--------|
| **Title** | Lazy Load catalog duplicates `Test.allTheThings() T-Shirt (Red) (L)` |
| **Severity / Priority** | **High / P1** |
| **Steps** | 1. Login. 2. Menu → Dynamic Catalog → Lazy Load. 3. Scroll until catalog finishes loading. 4. Search for Red T-Shirt size L. |
| **Expected** | Each size/SKU appears once. |
| **Actual** | Duplicate cards for the same name/size (count increases with further lazy loads). |
| **Impact** | Catalog trust/data integrity; users may believe multiple identical SKUs exist; breaks uniqueness assumptions for automation/analytics. |
| **Classification note** | Distinct from main `/inventory.html` catalog (6 unique items). Bug is in Dynamic Catalog Lazy Load surface. Browse-only (no Add to cart) is treated as **limitation**, not this defect. |
| **Evidence** | `evidence/DEF05-lazy-load-duplicate-sku.png` |

### Intentionally not reported as defects

- Missing Add to cart on Dynamic Catalog pages → product limitation / separate feature surface  
- Cart quantity cannot exceed 1 → demo cart model (`localStorage` ID array), document as limitation  
- Mock payment “SauceCard #31337” → intentional demo behavior  
- Broken UX on `problem_user` / `visual_user` → persona-specific, not primary-account defects  

---

## Task C — AI-Assisted Test Automation

**Framework:** Playwright (TypeScript)  
**Flow:** Login → add Sauce Labs Backpack → cart → checkout → verify thank-you + cleared cart  

**Setup / run:** see root `README.md`  
```bash
npm install
npx playwright install chromium
npm test
```

**AI vs manual:** see `docs/AI-USAGE.md`  
Critical manual fix: configure `testIdAttribute: "data-test"` after AI-assumed `data-testid` caused a 60s timeout.

**Automation limitations:** live site dependency; single persona; does not assert known demo defects as expected failures.

---

## Task D — AI-Driven QA Approach (≤ 1 page)

### Proposal: QA in an AI-driven development workflow

When developers use AI to generate code, tests, and docs, QA’s job shifts from “write every case by hand” to **risk ownership, oracle definition, and gatekeeping**.

**Where AI adds value across the QA lifecycle**
- **Planning:** risk heatmaps, persona/journey candidates, ambiguity questions for stories  
- **Design:** boundary/negative ideas, state-transition coverage gaps  
- **Authoring:** draft automation, locator suggestions, fixture scaffolding  
- **Execution support:** flaky-test clustering, failure summarization, log/trace triage  
- **Reporting:** defect drafting, release risk summaries  

**Where human review is mandatory**
- Acceptance criteria / product oracles (“what is correct?”)  
- Severity & release-risk decisions  
- Security, privacy, payments, and compliance-sensitive flows  
- Any AI claim not reproduced on a real build/environment  
- Final sign-off that a defect is real (not a demo persona quirk or env issue)

**Reviewing AI-generated tests before regression**
1. Map each test to a risk/requirement (orphan tests rejected).  
2. Assert **outcomes**, not only clicks (URL, totals, persistence, errors).  
3. Prefer stable selectors (`data-test` / roles); ban brittle nth/XPath unless justified.  
4. Prove isolation (no shared cart/session pollution).  
5. Ban unnecessary hard waits; use framework auto-wait.  
6. Run once locally + once in CI against the target env before merge.  
7. Owner: a human reviewer marks “promotion approved.”

**Defect analysis, coverage, regression optimization**
- AI clusters failures by symptom/stack to speed triage; humans confirm root cause.  
- AI diffs changed files → impacted journeys to suggest regression subsets.  
- Coverage gaps: AI compares critical journeys vs existing tests; humans prioritize.  
- Optimize suite: quarantine flakes, demote low-signal UI checks, keep critical path green.

**CI/CD quality gates**
- PR gate: lint + unit + **smoke E2E** (this purchase flow class).  
- Merge/nightly: broader regression; AI summarizes new failures with owners.  
- Release gate: critical-path pass required; AI drafts release risk note from open defects + failed jobs.  
- AI never auto-closes a failing gate without human override policy.

**Key risks & mitigations**

| Risk | Mitigation |
|------|------------|
| Plausible but wrong tests (assert wrong oracle) | Human oracle review; tie tests to AC |
| Selector / env brittleness | `data-test` contract; contract tests for attributes |
| Hallucinated defects | Require live repro + evidence |
| Security blind spots | Mandatory human/security review on auth/PII |
| Over-trust / automation theater | Measure escaped defects; keep exploratory charters |
| Secret leakage into prompts | Redact credentials; use public demo accounts only in examples |

**Bottom line:** AI accelerates ideation and drafting; **humans own correctness, risk, and promotion into regression.**

---

## Tools used (list)

- Cursor Agent / Composer  
- Cursor IDE Browser  
- Playwright + Chromium  
- Node.js / npm  
- python-docx (submission Word export)  
- SauceDemo public web app  

---

## Evidence index

| ID | File |
|----|------|
| DEF-01 | `evidence/DEF01-*.png` |
| DEF-02 | `evidence/DEF02-*.png` |
| DEF-03 | `evidence/DEF03-invalid-postal-code.png` |
| DEF-04 | `evidence/DEF04-back-allows-refinish.png` |
| DEF-05 | `evidence/DEF05-lazy-load-duplicate-sku.png` |
