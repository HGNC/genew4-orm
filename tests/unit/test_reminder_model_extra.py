"""Additional unit tests for Reminder model to improve coverage."""

import pytest

from genew4_orm.models import Reminder


class TestReminderReprEdgeCases:
    """Additional test cases for Reminder __repr__ method."""

    def test_reminder_repr_with_id_zero(self) -> None:
        """Test Reminder __repr__ handles id of 0."""
        reminder = Reminder(
            id=0,
            subject="Test Reminder",
            content="Test content",
            reminder_date="2025-01-01",
        )

        repr_str = repr(reminder)

        assert "Reminder" in repr_str
        assert "id=0" in repr_str

    def test_reminder_repr_with_negative_id(self) -> None:
        """Test Reminder __repr__ handles negative ID."""
        reminder = Reminder(
            id=-999,
            subject="Test",
            content="Content",
            reminder_date="2025-01-01",
        )

        repr_str = repr(reminder)

        assert "Reminder" in repr_str
        assert "id=-999" in repr_str


class TestReminderEdgeCases:
    """Additional test cases for Reminder edge cases."""

    def test_reminder_with_only_user_reference(self) -> None:
        """Test Reminder with only user reference (no gene/group)."""
        reminder = Reminder(
            subject="User Task",
            content="Complete task",
            reminder_date="2025-06-15",
            user_id=1,
        )

        assert reminder.user_id == 1
        assert reminder.hgnc_id is None
        assert reminder.group_id is None

    def test_reminder_reminder_date_validation(self) -> None:
        """Test Reminder with various date formats."""
        from datetime import date

        reminder = Reminder(
            subject="Date Test",
            content="Test",
            reminder_date=date(2025, 12, 31),
        )

        assert reminder.reminder_date == date(2025, 12, 31)
