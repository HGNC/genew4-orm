"""Unit tests for Reminder model."""

from datetime import date

from genew4_orm.models import Reminder


class TestReminder:
    """Test cases for Reminder model."""

    def test_reminder_instantiation_minimal(self) -> None:
        """Test Reminder can be instantiated with minimal required fields."""
        reminder = Reminder(
            subject="Test Reminder",
            content="This is a test reminder",
            reminder_date=date(2025, 6, 15),
        )

        assert reminder.subject == "Test Reminder"
        assert reminder.content == "This is a test reminder"
        assert reminder.reminder_date == date(2025, 6, 15)
        assert reminder.sent is False  # Default value

    def test_reminder_instantiation_with_all_fields(self) -> None:
        """Test Reminder can be instantiated with all fields."""
        reminder = Reminder(
            subject="Test Reminder",
            content="This is a test reminder",
            reminder_date=date(2025, 6, 15),
            sent=True,
            user_id=1,
            hgnc_id=12345,
            group_id=678,
        )

        assert reminder.subject == "Test Reminder"
        assert reminder.content == "This is a test reminder"
        assert reminder.reminder_date == date(2025, 6, 15)
        assert reminder.sent is True
        assert reminder.user_id == 1
        assert reminder.hgnc_id == 12345
        assert reminder.group_id == 678

    def test_reminder_with_gene_reference(self) -> None:
        """Test Reminder with gene reference."""
        reminder = Reminder(
            subject="Gene Review",
            content="Review this gene",
            reminder_date=date(2025, 6, 15),
            hgnc_id=12345,
        )

        assert reminder.hgnc_id == 12345
        assert reminder.group_id is None
        assert reminder.user_id is None

    def test_reminder_with_gene_group_reference(self) -> None:
        """Test Reminder with gene group reference."""
        reminder = Reminder(
            subject="Group Review",
            content="Review this gene group",
            reminder_date=date(2025, 6, 15),
            group_id=678,
        )

        assert reminder.group_id == 678
        assert reminder.hgnc_id is None
        assert reminder.user_id is None

    def test_reminder_with_user_reference(self) -> None:
        """Test Reminder with user reference."""
        reminder = Reminder(
            subject="User Task",
            content="Complete this task",
            reminder_date=date(2025, 6, 15),
            user_id=1,
        )

        assert reminder.user_id == 1
        assert reminder.hgnc_id is None
        assert reminder.group_id is None

    def test_reminder_sent_default(self) -> None:
        """Test Reminder sent field defaults to False."""
        reminder = Reminder(
            subject="Test",
            content="Test content",
            reminder_date=date(2025, 6, 15),
        )

        assert reminder.sent is False

    def test_reminder_sent_true(self) -> None:
        """Test Reminder sent can be set to True."""
        reminder = Reminder(
            subject="Test",
            content="Test content",
            reminder_date=date(2025, 6, 15),
            sent=True,
        )

        assert reminder.sent is True

    def test_reminder_repr(self) -> None:
        """Test Reminder __repr__ method."""
        reminder = Reminder(
            id=123,
            subject="Test Reminder",
            content="Test content",
            reminder_date=date(2025, 6, 15),
        )

        repr_str = repr(reminder)

        assert "Reminder" in repr_str
        assert "id=123" in repr_str
        assert "subject='Test Reminder'" in repr_str

    def test_reminder_repr_with_none_id(self) -> None:
        """Test Reminder __repr__ with None id (before save)."""
        reminder = Reminder(
            subject="Test Reminder",
            content="Test content",
            reminder_date=date(2025, 6, 15),
        )

        repr_str = repr(reminder)

        assert "Reminder" in repr_str
        assert "id=None" in repr_str
        assert "subject='Test Reminder'" in repr_str

    def test_reminder_all_foreign_keys_null(self) -> None:
        """Test Reminder with all foreign keys null."""
        reminder = Reminder(
            subject="Standalone Reminder",
            content="Just a reminder",
            reminder_date=date(2025, 6, 15),
            user_id=None,
            hgnc_id=None,
            group_id=None,
        )

        assert reminder.user_id is None
        assert reminder.hgnc_id is None
        assert reminder.group_id is None

    def test_reminder_date_field(self) -> None:
        """Test Reminder with various date values."""
        reminder1 = Reminder(
            subject="Test",
            content="Test",
            reminder_date=date(2025, 1, 1),
        )
        reminder2 = Reminder(
            subject="Test",
            content="Test",
            reminder_date=date(2025, 12, 31),
        )

        assert reminder1.reminder_date == date(2025, 1, 1)
        assert reminder2.reminder_date == date(2025, 12, 31)
