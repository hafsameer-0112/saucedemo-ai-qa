# AI prompt / usage log (Tasks A–C)

## Tools used

| Tool | Role |
|------|------|
| Cursor Agent (Composer) | Exploratory risk ideation, defect drafting, Playwright coding, submission packaging |
| Cursor Browser (IDE browser) | Live validation on https://www.saucedemo.com/ |
| Playwright + Chromium | Automated E2E execution |
| python-docx | Word submission document generation |

## Representative AI prompts

See `docs/SUBMISSION.md` § AI Prompt Log for the five Task A prompts with purpose, useful output, and validation outcomes.

## Task C — What AI assisted with

- Suggested Playwright + TypeScript as the framework
- Drafted initial happy-path structure (login → cart → checkout → assert)
- Proposed `data-test` / role-based locators and meaningful price assertions
- Suggested clearing storage for isolation

## What was incorrect / brittle in AI output (and manual fixes)

| AI output issue | Manual change | Why |
|-----------------|---------------|-----|
| Assumed Playwright `getByTestId` maps to `data-testid` | Set `testIdAttribute: "data-test"` in `playwright.config.ts` | SauceDemo uses `data-test`; first run timed out waiting for backpack add button |
| Suggested `waitForTimeout` / fixed sleeps in early draft | Removed; used auto-waiting + `expect` | Hard-coded waits are brittle and slow |
| Over-broad locator ideas (`button.btn_inventory` nth) | Switched to product-specific `data-test` IDs | nth-index selectors break when sort order changes |
| Incomplete isolation (login only) | Clear cookies + localStorage/sessionStorage in `beforeEach` | Cart persists in `localStorage` across runs |
| Tax assertion as “about 8%” only | Exact labels: subtotal 29.99, tax 2.40, total 32.39 | Stronger regression signal |

## Resulting automation risks

- Live third-party demo dependency
- Does not encode known demo defects as expected failures (those belong in separate negative tests)
- Visual / Dynamic Catalog flows are not covered by this single E2E
