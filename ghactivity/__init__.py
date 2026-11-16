"""GitHub activity for the portfolio: fetch, cache, redact, derive.

Public surface:
    activity_view(year)  -> view-model for /activity/
    card_view()          -> view-model for the homepage card, or None

Nothing in here may hand a template a private repo's name, owner, message,
oid or URL. Redaction happens in `redact.py` at fetch time, and `service.py`
applies the hide list again when it builds the view-model.
"""
from .service import activity_view, card_view

__all__ = ["activity_view", "card_view"]
