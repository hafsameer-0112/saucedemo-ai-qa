"""Generate SauceDemo-AI-QA-Submission.docx with embedded evidence."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = ROOT / "SauceDemo-AI-QA-Submission.docx"

doc = Document()
for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)


def font(run, size=11, bold=False, color=None):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        font(r, size={1: 16, 2: 13, 3: 12}.get(level, 12), bold=True)
    return p


def p(text, bold=False, italic=False, size=11, after=6):
    para = doc.add_paragraph()
    run = para.add_run(text)
    font(run, size=size, bold=bold)
    run.italic = italic
    para.paragraph_format.space_after = Pt(after)
    return para


def bullet(text):
    para = doc.add_paragraph(style="List Bullet")
    run = para.add_run(text)
    font(run, size=10)
    para.paragraph_format.space_after = Pt(3)


def shade_header(row):
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "1F4E79")
        shd.set(qn("w:val"), "clear")
        tcPr.append(shd)
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.bold = True
                run.font.size = Pt(9)
                run.font.name = "Calibri"


def table(headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for i, header in enumerate(headers):
        t.rows[0].cells[i].text = header
        for para in t.rows[0].cells[i].paragraphs:
            for run in para.runs:
                font(run, size=9, bold=True)
    shade_header(t.rows[0])
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            t.rows[r_i + 1].cells[c_i].text = val
            for para in t.rows[r_i + 1].cells[c_i].paragraphs:
                for run in para.runs:
                    font(run, size=9)
    doc.add_paragraph()


def img(path: Path, width=5.8, caption=None):
    if not path.exists():
        p(f"[Missing evidence: {path.name}]", italic=True, size=9)
        return
    doc.add_picture(str(path), width=Inches(width))
    if caption:
        cap = doc.add_paragraph()
        run = cap.add_run(caption)
        font(run, size=9, bold=False)
        run.italic = True
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(10)


# Title
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("SauceDemo — AI-Assisted QA Submission")
font(r, size=20, bold=True, color=(31, 78, 121))

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Tasks A–D · Defect Report · Automation · AI QA Strategy")
font(r, size=12, bold=True)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = meta.add_run(
    "App: https://www.saucedemo.com/  |  Account: standard_user / secret_sauce\n"
    "Date: 6 October 2026  |  Automation: Playwright (TypeScript)"
)
font(r, size=10)
meta.paragraph_format.space_after = Pt(12)

h("1. Executive summary")
p(
    "AI accelerated risk discovery and automation drafting for SauceDemo. Ideas were challenged "
    "against the live app on standard_user. Five high-impact defects were confirmed; unsupported "
    "AI suggestions (real payments, stock, i18n, etc.) were discarded. One maintainable Playwright "
    "E2E covers the critical purchase path."
)

h("2. Task B — Defect report (top 5)")

# DEF-01
h("DEF-01 — Empty cart can complete checkout ($0 order)", 2)
table(
    ["Field", "Detail"],
    [
        ["Severity / Priority", "Critical / P0"],
        [
            "Steps to reproduce",
            "1) Login as standard_user. 2) Open empty cart. 3) Click Checkout. "
            "4) Enter any First/Last/Zip. 5) Continue → Finish.",
        ],
        ["Expected", "Checkout blocked when cart is empty; order cannot complete."],
        [
            "Actual",
            "Checkout proceeds. Overview: Item total $0 / Tax $0.00 / Total $0.00. "
            "Finish shows “Thank you for your order!”",
        ],
        [
            "Business / user impact",
            "Meaningless successful orders; broken purchase invariant; pollutes metrics.",
        ],
        [
            "Classification reasoning",
            "Reproduced on standard_user. Not a persona quirk. Empty-cart Checkout is a rule failure.",
        ],
    ],
)
img(EVIDENCE / "DEF01-empty-cart-checkout-enabled.png", caption="Fig. DEF-01a — Empty cart with Checkout enabled")
img(EVIDENCE / "DEF01-empty-order-overview-zero-total.png", caption="Fig. DEF-01b — Overview totals $0.00")
img(EVIDENCE / "DEF01-empty-order-thank-you.png", caption="Fig. DEF-01c — Thank-you after empty order")

# DEF-02
h("DEF-02 — Whitespace-only checkout identity accepted", 2)
table(
    ["Field", "Detail"],
    [
        ["Severity / Priority", "Critical / P0"],
        [
            "Steps to reproduce",
            "1) Login, add item, Checkout. 2) Enter spaces only in First/Last/Zip. 3) Continue.",
        ],
        ["Expected", "Validation error after trim; spaces-only rejected."],
        ["Actual", "Advances to Overview with no error."],
        [
            "Business / user impact",
            "Orders with unusable customer identity; fulfillment would fail in a real system.",
        ],
        [
            "Classification reasoning",
            "Truly empty fields are validated (“is required”), so accepting spaces is incomplete validation — not “no validation by design.”",
        ],
    ],
)
img(EVIDENCE / "DEF02-whitespace-only-checkout-fields.png", caption="Fig. DEF-02a — Fields contain only spaces")
img(EVIDENCE / "DEF02-whitespace-accepted-overview.png", caption="Fig. DEF-02b — Overview reached after whitespace submit")

# DEF-03
h("DEF-03 — Postal code accepts invalid format (!!!)", 2)
table(
    ["Field", "Detail"],
    [
        ["Severity / Priority", "High / P1"],
        [
            "Steps to reproduce",
            "1) Login, add item, Checkout. 2) Valid names + Zip “!!!”. 3) Continue.",
        ],
        ["Expected", "Format validation rejects non-postal values."],
        ["Actual", "Accepted; Overview reached."],
        ["Business / user impact", "Invalid shipping addresses; support/return cost."],
        [
            "Classification reasoning",
            "Field is labeled Zip/Postal Code and other fields are validated — format check is reasonable.",
        ],
    ],
)
img(EVIDENCE / "DEF03-invalid-postal-code.png", caption="Fig. DEF-03 — Zip value “!!!” accepted on the form")

# DEF-04
h("DEF-04 — Browser Back after completion allows re-Finish", 2)
table(
    ["Field", "Detail"],
    [
        ["Severity / Priority", "High / P1"],
        [
            "Steps to reproduce",
            "1) Complete checkout to Thank You. 2) Browser Back. 3) Finish still available; click again.",
        ],
        ["Expected", "Overview invalidated; Finish cannot re-submit."],
        ["Actual", "Overview + Finish remain usable (duplicate completion path)."],
        ["Business / user impact", "Duplicate submissions; confused order state."],
        [
            "Classification reasoning",
            "Classic history/state bug on standard_user — not an exotic persona issue.",
        ],
    ],
)
img(EVIDENCE / "DEF04-back-allows-refinish.png", caption="Fig. DEF-04 — Back returns to Overview with Finish active")

# DEF-05
h("DEF-05 — Lazy Load catalog duplicate SKUs", 2)
table(
    ["Field", "Detail"],
    [
        ["Severity / Priority", "High / P1"],
        [
            "Steps to reproduce",
            "1) Login. 2) Menu → Dynamic Catalog → Lazy Load. 3) Scroll to load items. "
            "4) Observe Test.allTheThings() T-Shirt (Red) (L).",
        ],
        ["Expected", "Each size/SKU appears once."],
        ["Actual", "Duplicate cards for the same name/size (worsens with further lazy loads)."],
        [
            "Business / user impact",
            "Catalog data integrity; user confusion; analytics/automation uniqueness breaks.",
        ],
        [
            "Classification reasoning",
            "Main inventory has unique items; bug is specific to Dynamic Catalog Lazy Load. "
            "Browse-only (no Add to cart) is a limitation, not this defect.",
        ],
    ],
)
img(EVIDENCE / "DEF05-lazy-load-duplicate-sku.png", caption="Fig. DEF-05 — Duplicate Red T-Shirt (L) highlighted")

h("Not reported as defects (reasoning)", 2)
bullet("Dynamic Catalog has no Add to cart → feature limitation / separate surface.")
bullet("Cart qty cannot exceed 1 → demo localStorage ID-array model.")
bullet("SauceCard #31337 mock payment → intentional demo behavior.")
bullet("problem_user / visual_user quirks → persona-specific, not primary-account defects.")

h("3. Task A — AI prompt / usage log")
prompts = [
    (
        "Prompt 1 — Risk prioritization",
        "Identify highest-risk SauceDemo journeys for standard_user; challenge real-commerce assumptions.",
        "Focus session on impact.",
        "Checkout/cart top; payment likely mocked.",
        "Validated checkout/cart risk. Rejected deep payment/fraud focus.",
    ),
    (
        "Prompt 2 — Checkout edge cases",
        "Generate checkout risks: empty cart, whitespace, postal format, Back after complete, tax math.",
        "Convert ideation to experiments.",
        "Empty cart, whitespace, !!! zip, Back+Finish, tax.",
        "Validated DEF-01–04 as bugs; tax 8% confirmed pass.",
    ),
    (
        "Prompt 3 — Dynamic Catalog",
        "Explore Lazy/Spinner/Slider for data integrity, loading UX, a11y; discard if browse-only.",
        "Scout newer surface.",
        "Duplicates, a11y, missing Add to cart.",
        "Validated DEF-05. Treated missing Add to cart as limitation.",
    ),
    (
        "Prompt 4 — Auth scoped",
        "Login/session risks; ignore SQL injection unless UI justifies it.",
        "Cover auth without folklore.",
        "Required fields, locked_out_user, route guards.",
        "Validated guards + locked_out. Rejected SQL deep dive.",
    ),
    (
        "Prompt 5 — Discard pass",
        "Discard multi-currency, stock, email confirmation, multi-user cart, real cards — based on app reality.",
        "Kill unsupported AI ideas.",
        "Discard list with rationale.",
        "All five discarded after live observation.",
    ),
]
for title_t, prompt, purpose, useful, action in prompts:
    h(title_t, 3)
    p("Prompt: " + prompt, italic=True)
    p("Purpose: " + purpose)
    p("Useful AI output: " + useful)
    p("Tested / changed / rejected / validated: " + action)

h("4. Task C — Automated test")
p(
    "Framework: Playwright (TypeScript). Flow: Login → add Sauce Labs Backpack → cart → "
    "checkout info → overview (assert totals) → finish → assert thank-you + cleared cart badge."
)
h("Setup & run", 3)
p("Repository folder: saucedemo-ai-qa (public GitHub — see README after publish).", italic=True)
bullet("npm install")
bullet("npx playwright install chromium")
bullet("npm test   # or: npm run test:headed")
p("Credentials: standard_user / secret_sauce (public demo credentials).")

h("AI assistance vs manual changes", 3)
table(
    ["Topic", "Detail"],
    [
        [
            "AI assisted",
            "Playwright+TS choice; happy-path structure; data-test/role locators; price assertions; storage isolation idea.",
        ],
        [
            "AI incorrect / brittle",
            "Assumed data-testid (SauceDemo uses data-test) → 60s timeout; early draft used hard waits; nth button locators.",
        ],
        [
            "Manual fixes",
            "testIdAttribute: 'data-test'; removed hard waits; product-specific data-test IDs; exact tax/total asserts; clear cookies+storage in beforeEach.",
        ],
        [
            "Limitations / risks",
            "Depends on live SauceDemo; single persona; does not encode known demo defects as expected failures; network flakiness possible.",
        ],
    ],
)
p("Test file: tests/checkout-happy-path.spec.ts — verified locally: 1 passed (~3s).", bold=True)

h("5. Task D — AI-driven QA approach (1 page)")
p(
    "When developers use AI to generate code, tests, and docs, QA shifts from writing every case "
    "by hand to risk ownership, oracle definition, and gatekeeping."
)
p("Where AI adds value:", bold=True, after=2)
bullet("Planning: risk heatmaps, journey candidates, ambiguity questions.")
bullet("Design: boundaries/negatives, state-transition gaps.")
bullet("Authoring: draft automation, locator suggestions, fixtures.")
bullet("Execution: flake clustering, failure summarization, log/trace triage.")
bullet("Reporting: defect drafts, release risk summaries.")

p("Where human review is mandatory:", bold=True, after=2)
bullet("Acceptance criteria / product oracles (“what is correct?”).")
bullet("Severity & release-risk decisions.")
bullet("Security, privacy, payments, compliance-sensitive flows.")
bullet("Any AI claim not reproduced on a real build.")
bullet("Final sign-off that a finding is a real defect (not persona/env quirk).")

p("Reviewing AI-generated tests before regression:", bold=True, after=2)
bullet("Map each test to a risk/requirement; reject orphans.")
bullet("Assert outcomes (URL, totals, persistence, errors), not only clicks.")
bullet("Prefer data-test / roles; ban brittle nth/XPath unless justified.")
bullet("Prove isolation; ban unnecessary hard waits.")
bullet("Run locally + CI; human marks “promotion approved.”")

p("Defect analysis, coverage, regression optimization:", bold=True, after=2)
bullet("AI clusters failures; humans confirm root cause.")
bullet("AI maps changed files → impacted journeys for regression subsets.")
bullet("AI finds coverage gaps vs critical journeys; humans prioritize.")
bullet("Optimize: quarantine flakes; keep critical path green.")

p("CI/CD quality gates:", bold=True, after=2)
bullet("PR: lint + unit + smoke E2E (purchase-class).")
bullet("Nightly: broader regression; AI summarizes failures with owners.")
bullet("Release: critical-path pass required; AI drafts risk note from open defects.")
bullet("AI never auto-closes a failing gate without human override policy.")

p("Key risks & mitigations:", bold=True, after=2)
table(
    ["Risk", "Mitigation"],
    [
        ["Wrong oracle in AI tests", "Human AC review; tie tests to requirements"],
        ["Brittle selectors / env", "data-test contract; target-env CI runs"],
        ["Hallucinated defects", "Require live repro + evidence"],
        ["Security blind spots", "Mandatory human/security review on auth/PII"],
        ["Automation theater", "Track escaped defects; keep exploratory charters"],
        ["Secret leakage in prompts", "Redact secrets; use public demo accounts in examples"],
    ],
)
p(
    "Bottom line: AI accelerates ideation and drafting; humans own correctness, risk, and "
    "promotion into the regression suite.",
    bold=True,
)

h("6. Tools used")
bullet("Cursor Agent / Composer — ideation, coding, packaging")
bullet("Cursor IDE Browser — live exploratory validation")
bullet("Playwright + Chromium — E2E automation")
bullet("Node.js / npm")
bullet("python-docx — Word submission export")
bullet("SauceDemo public web application")

h("7. Evidence & repo index")
table(
    ["Artifact", "Location"],
    [
        ["Automated test", "tests/checkout-happy-path.spec.ts"],
        ["Run instructions", "README.md"],
        ["AI usage detail", "docs/AI-USAGE.md"],
        ["Markdown narrative", "docs/SUBMISSION.md"],
        ["Screenshots", "evidence/DEF01–DEF05*.png"],
        ["This Word document", "SauceDemo-AI-QA-Submission.docx"],
    ],
)

doc.save(OUT)
print(OUT)
