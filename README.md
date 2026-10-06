# SauceDemo — AI-Assisted QA Assignment

End-to-end Playwright automation plus defect evidence for [SauceDemo](https://www.saucedemo.com/).

## What’s in this repo

| Path | Contents |
|------|----------|
| `tests/checkout-happy-path.spec.ts` | Automated E2E: Login → add Backpack → checkout → verify completion |
| `playwright.config.ts` | Base URL, `data-test` test IDs, isolation defaults |
| `evidence/` | Screenshots for top defects (DEF-01 … DEF-05) |
| `docs/SUBMISSION.md` | Full submission narrative (defects, AI prompts, strategy) |
| `docs/AI-USAGE.md` | What AI generated vs what was changed manually |

The single Word submission document is also generated at the repo root:
`SauceDemo-AI-QA-Submission.docx`

## Prerequisites

- Node.js 18+ (Node 22 recommended)
- npm

## Setup

```bash
npm install
npx playwright install chromium
```

## Run the automated test

```bash
# headless (CI-friendly)
npm test

# headed
npm run test:headed

# Playwright UI mode
npm run test:ui
```

### Credentials used by the test

- Username: `standard_user`
- Password: `secret_sauce`

(Public demo credentials shown on the SauceDemo login page.)

## Test design notes

- **Flow:** Login → add Sauce Labs Backpack → cart → checkout info → overview → finish
- **Assertions:** URL transitions, cart badge, line item name/price, tax/total (`$29.99` + `$2.40` = `$32.39`), thank-you header, cart badge cleared
- **Selectors:** `data-test` attributes via Playwright `getByTestId` (`testIdAttribute: "data-test"`)
- **Isolation:** cookies + `localStorage` / `sessionStorage` cleared in `beforeEach`
- **No hard-coded sleeps:** relies on Playwright auto-waiting + `expect` timeouts

## Limitations / risks

- Depends on the public SauceDemo site remaining available and unchanged
- Demo app quirks (e.g. empty-cart checkout) are **not** asserted as “correct business rules” in the happy-path test
- Network flakiness can affect runs against the live host
- Other SauceDemo personas (`problem_user`, `error_user`, etc.) are out of scope for this single test
