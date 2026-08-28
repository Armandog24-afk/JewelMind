"""Setting System v1 (Sprint 19) — category-neutral stone-setting geometry.

A Setting defines how metal geometry interacts with one or more stones. It
knows nothing about rings: SETTING-GOV-001/014 forbid importing
`jewelmind.ring`, and the category-specific attachment (a RingHead, a
future PendantBody, an EarringBody) consumes a `SettingAttachmentInterface`
rather than the Setting reaching outward.

Deliberately NON-EAGER (imports nothing) — the same discipline
`geometry/stone/__init__.py` adopted in Sprint 18 after a real circular
import. Import the submodule you need directly, e.g.
`from jewelmind.setting.dispatch import generate_setting`.

See docs/bible/21-setting/README.md.
"""

from __future__ import annotations
