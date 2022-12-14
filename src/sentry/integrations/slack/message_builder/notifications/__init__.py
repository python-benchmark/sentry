from __future__ import annotations

from .base import SlackNotificationsMessageBuilder
from .digest import DigestNotificationMessageBuilder
from .issues import ActiveReleaseIssueNotificationMessageBuilder, IssueNotificationMessageBuilder


def get_message_builder(klass: str) -> type[SlackNotificationsMessageBuilder]:
    """TODO(mgaeta): HACK to get around circular imports."""
    return {
        "DigestNotificationMessageBuilder": DigestNotificationMessageBuilder,
        "IssueNotificationMessageBuilder": IssueNotificationMessageBuilder,
        "ActiveReleaseIssueNotificationMessageBuilder": ActiveReleaseIssueNotificationMessageBuilder,
        "SlackNotificationsMessageBuilder": SlackNotificationsMessageBuilder,
    }[klass]


__all__ = (
    "get_message_builder",
    "DigestNotificationMessageBuilder",
    "IssueNotificationMessageBuilder",
    "ActiveReleaseIssueNotificationMessageBuilder",
    "SlackNotificationsMessageBuilder",
)
