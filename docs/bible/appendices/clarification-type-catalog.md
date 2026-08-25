---
id: JM-BIBLE-A76
title: "Appendix: Clarification Type Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Clarification Type Catalog

The 4 `ExpectedAnswerType` values (`backend/jewelmind/conversation/schemas.py`), and exactly how `try_resolve_answer()` (`backend/jewelmind/conversation/clarifications.py`) validates each. Example question/answer pairs are pulled from the real, generated `specs/conversation/v1/test-vectors/clarification-resolution-vectors.json` (produced by actually running `try_resolve_answer()`, per `specs/conversation/v1/README.md`) — none invented for this appendix.

| Type | Validation logic (`try_resolve_answer()`) | Accepted example | Rejected example |
|---|---|---|---|
| `NUMERIC` | Strips whitespace, lowercases, removes `"mm"`, then attempts `float(candidate)`. Accepts anything that parses as a float after that stripping; rejects (returns `(None, False)`) on a `ValueError`. | `"2.7 mm"` -> resolved value `2.7`, accepted | `"not a number"` -> resolved value `None`, rejected |
| `ENUM_CHOICE` | Case-insensitively matches `raw_answer` against `thread.allowedChoices`; returns the matching choice's original (not the caller's) casing if found. | `"rose_gold_18k"` -> resolved value `"rose_gold_18k"`, accepted (choice offered verbatim) | `"platinum"` -> resolved value `None`, rejected (not among `allowedChoices`) |
| `CONFIRMATION` | Lowercases and checks membership in `clarifications._CONFIRMATION_YES` (`"yes", "y", "si", "sì", "ok", "va bene", "d'accordo"`) or `_CONFIRMATION_NO` (`"no", "not really", "niente"`); anything else is rejected. | `"yes"` -> resolved value `"yes"`, accepted; `"no"` -> resolved value `"no"`, accepted (both normalize to the literal strings `"yes"`/`"no"`, not the raw input) | `"maybe"` -> resolved value `None`, rejected |
| `FREE_TEXT` | Accepts any non-empty stripped string as-is; rejects only an empty string. | `"make it sparkle"` -> resolved value `"make it sparkle"`, accepted | `""` (empty) -> resolved value `None`, rejected |

## Notes grounded in the real code

- `try_resolve_answer()` never mutates the `ClarificationThread` it validates against — the caller (`ConversationEngine._handle_answer_clarification()`, `service.py`) decides whether/how to close the thread based on the `(resolved_value, accepted)` tuple it returns. This is asserted directly by `backend/tests/test_conversation.py::TestClarifications::test_close_answered_sets_status` (`assert thread.status == "OPEN"  # original never mutated`).
- The `NUMERIC` branch only strips the literal substring `"mm"` — it does not handle other unit tokens (e.g. `"cm"`) or a comma decimal separator; any of those would fail the `float()` conversion and be rejected.
- `CONFIRMATION`'s resolved value is always exactly the string `"yes"` or `"no"`, never the caller's original casing/spelling of a synonym like `"d'accordo"` — this is real behavior, not a normalization the appendix is inferring: `try_resolve_answer(thread, "yes") == ("yes", True)` and `try_resolve_answer(thread, "no") == ("no", True)` are asserted verbatim in `backend/tests/test_conversation.py::TestClarifications::test_confirmation_yes_no`.
