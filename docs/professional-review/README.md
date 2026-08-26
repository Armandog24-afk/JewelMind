# JewelMind Professional Review — Real, Fillable Forms

This directory holds real forms meant to be handed to a real jewelry professional and actually filled in — a CAD designer, a goldsmith/bench jeweler, a stone setter, or a casting/resin-printing specialist. None of them contain a fake completed review, a fake reviewer name, or fake evidence. Every field below is blank, waiting for a real person.

**Nothing in this directory has been filled in yet.** Filling one in and returning it to JewelMind is what would start turning a preliminary software assumption into evidence-backed professional validation — and that has not happened yet, as of this Sprint. The framework these forms feed into is documented in [`docs/bible/15-professional-validation/README.md`](../bible/15-professional-validation/README.md); read it for the full picture of how a filled-in form becomes a structured, versioned `ValidationRecord`.

## Files in this directory

| File | Use it when... |
|---|---|
| [`reviewer-onboarding.md`](reviewer-onboarding.md) | A professional is about to review JewelMind for the first time. |
| [`confidentiality-and-scope-template.md`](confidentiality-and-scope-template.md) | Setting expectations with a reviewer before a session — what they're being shown, what feedback is being requested. |
| [`solitaire-general-review-form.md`](solitaire-general-review-form.md) | A general, whole-product review of the current solitaire. |
| [`forge-rule-review-form.md`](forge-rule-review-form.md) | Reviewing one specific automated design rule. |
| [`geometry-review-form.md`](geometry-review-form.md) | Reviewing a component or the complete model's geometry, especially by a CAD designer. |
| [`stone-setting-review-form.md`](stone-setting-review-form.md) | A stone setter's review of prong/basket/setting geometry. |
| [`manufacturing-review-form.md`](manufacturing-review-form.md) | A casting or resin-printing specialist's review. |
| [`cad-interoperability-review-form.md`](cad-interoperability-review-form.md) | Testing STEP import into a real external CAD application. |
| [`review-session-notes-template.md`](review-session-notes-template.md) | Free-form running notes for one review sitting. |
| [`validation-decision-template.md`](validation-decision-template.md) | Recording one specific decision in plain language. |

## Relationship to the review package's own auto-generated form

`backend/jewelmind/professional_validation/review_package.py` already bundles a compact, single-page `review-form.md` inside every generated Professional Review Package ZIP — that one is auto-generated per model and always present. The forms in this directory are the fuller, standalone versions meant for a structured pilot review program (see [`docs/bible/15-professional-validation/444-current-solitaire-review-plan.md`](../bible/15-professional-validation/444-current-solitaire-review-plan.md) — the practical review agenda) — a different purpose from the one-page form bundled automatically with every package, not a replacement for it.

## No scoring system

None of these forms produce a numeric score. A rejection, a "needs substantial rework," or a "this is a good starting point" answer are all equally complete, valuable responses. Honest negative feedback is exactly as valuable as a positive one.
