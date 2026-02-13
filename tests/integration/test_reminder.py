"""Integration tests for Reminder model with PostgreSQL.

This module tests Reminder CRUD operations with real database connections,
including testing relationships with User, Gene, and GeneGroup.
"""

from datetime import date, timedelta

import pytest
from sqlalchemy import select, text

from genew4_orm.models.gene import Gene
from genew4_orm.models.gene_group import GeneGroup
from genew4_orm.models.reminder import Reminder
from genew4_orm.models.user import User


@pytest.mark.usefixtures("postgres_session")
class TestReminderCRUD:
    """Test Reminder CRUD operations with PostgreSQL."""

    def test_create_reminder_minimal(self, postgres_session):
        """Test creating reminder with minimal required fields."""
        user = User(display_name="testuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Test Reminder",
            content="Test content",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        postgres_session.refresh(reminder)

        assert reminder.id is not None
        assert reminder.subject == "Test Reminder"
        assert reminder.content == "Test content"
        assert reminder.reminder_date == date.today()
        assert reminder.sent is False
        assert reminder.user_id == user.id

    def test_create_reminder_with_all_fields(self, postgres_session):
        """Test creating reminder with all fields."""
        user = User(display_name="testuser2")
        gene = Gene(approved_symbol="TEST1", approved_name="Test Gene 1")
        gene_group = GeneGroup(name="Test Group")

        postgres_session.add_all([user, gene, gene_group])
        postgres_session.commit()
        postgres_session.refresh(user)
        postgres_session.refresh(gene)
        postgres_session.refresh(gene_group)

        reminder = Reminder(
            subject="Complete Review",
            content="Review the gene entry",
            reminder_date=date.today() + timedelta(days=7),
            sent=True,
            user_id=user.id,
            hgnc_id=gene.hgnc_id,
            group_id=gene_group.id,
        )

        postgres_session.add(reminder)
        postgres_session.commit()
        postgres_session.refresh(reminder)

        assert reminder.subject == "Complete Review"
        assert reminder.content == "Review the gene entry"
        assert reminder.sent is True
        assert reminder.user_id == user.id
        assert reminder.hgnc_id == gene.hgnc_id
        assert reminder.group_id == gene_group.id

    def test_read_reminder_by_id(self, postgres_session):
        """Test reading reminder by ID."""
        user = User(display_name="readuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Read Test",
            content="Test reading reminder",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        reminder_id = reminder.id

        # Read by ID
        retrieved_reminder = postgres_session.get(Reminder, reminder_id)

        assert retrieved_reminder is not None
        assert retrieved_reminder.subject == "Read Test"
        assert retrieved_reminder.content == "Test reading reminder"

    def test_update_reminder_fields(self, postgres_session):
        """Test updating reminder fields."""
        user = User(display_name="updateuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Original Subject",
            content="Original content",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()

        # Update fields
        reminder.subject = "Updated Subject"
        reminder.content = "Updated content"
        reminder.reminder_date = date.today() + timedelta(days=30)
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(reminder)
        assert reminder.subject == "Updated Subject"
        assert reminder.content == "Updated content"
        assert reminder.reminder_date == date.today() + timedelta(days=30)

    def test_update_reminder_sent_status(self, postgres_session):
        """Test updating reminder sent status."""
        user = User(display_name="sentuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Send Test",
            content="Test sending reminder",
            reminder_date=date.today(),
            sent=False,
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()

        # Mark as sent
        reminder.sent = True
        postgres_session.commit()

        postgres_session.refresh(reminder)
        assert reminder.sent is True

    def test_delete_reminder(self, postgres_session):
        """Test deleting reminder."""
        user = User(display_name="deleteuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Delete Test",
            content="Test deleting reminder",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        reminder_id = reminder.id

        # Delete reminder
        postgres_session.delete(reminder)
        postgres_session.commit()

        # Verify deletion
        deleted_reminder = postgres_session.get(Reminder, reminder_id)
        assert deleted_reminder is None

    def test_query_reminders_by_subject_pattern(self, postgres_session):
        """Test querying reminders by subject pattern."""
        user = User(display_name="patternuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        # Create multiple reminders
        for i in range(3):
            reminder = Reminder(
                subject=f"Task {i}",
                content=f"Content {i}",
                reminder_date=date.today(),
                user_id=user.id,
            )
            postgres_session.add(reminder)
        postgres_session.commit()

        # Query with wildcard
        stmt = select(Reminder).where(Reminder.subject.like("Task %")).order_by(Reminder.subject)
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) >= 3

    def test_query_reminders_by_sent_status(self, postgres_session):
        """Test querying reminders by sent status."""
        user = User(display_name="sentstatususer")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        # Create reminders with different sent statuses
        reminder1 = Reminder(
            subject="Sent Reminder",
            content="Already sent",
            reminder_date=date.today(),
            sent=True,
            user_id=user.id,
        )
        reminder2 = Reminder(
            subject="Unsent Reminder",
            content="Not yet sent",
            reminder_date=date.today(),
            sent=False,
            user_id=user.id,
        )
        postgres_session.add_all([reminder1, reminder2])
        postgres_session.commit()

        # Query unsent reminders
        stmt = select(Reminder).where(not Reminder.sent)  # Use == instead of is
        unsent_reminders = postgres_session.execute(stmt).scalars().all()

        unsent_subjects = [r.subject for r in unsent_reminders]
        assert "Unsent Reminder" in unsent_subjects

    def test_query_reminders_by_date_range(self, postgres_session):
        """Test querying reminders by date range."""
        user = User(display_name="dateuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        reminder1 = Reminder(
            subject="Today",
            content="Due today",
            reminder_date=today,
            user_id=user.id,
        )
        reminder2 = Reminder(
            subject="Tomorrow",
            content="Due tomorrow",
            reminder_date=tomorrow,
            user_id=user.id,
        )
        reminder3 = Reminder(
            subject="Next Week",
            content="Due next week",
            reminder_date=next_week,
            user_id=user.id,
        )
        postgres_session.add_all([reminder1, reminder2, reminder3])
        postgres_session.commit()

        # Query reminders due within next 2 days
        stmt = select(Reminder).where(Reminder.reminder_date <= tomorrow).order_by(Reminder.reminder_date)
        results = postgres_session.execute(stmt).scalars().all()

        subjects = [r.subject for r in results]
        assert "Today" in subjects
        assert "Tomorrow" in subjects


@pytest.mark.usefixtures("postgres_session")
class TestReminderUserRelationship:
    """Test Reminder relationship with User."""

    def test_reminder_with_user(self, postgres_session):
        """Test creating reminder associated with a user."""
        user = User(display_name="reminderuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="User Reminder",
            content="Reminder for user",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        postgres_session.refresh(reminder)

        assert reminder.user_id == user.id

    def test_query_reminders_by_user(self, postgres_session):
        """Test querying reminders for a specific user."""
        user1 = User(display_name="user1")
        user2 = User(display_name="user2")
        postgres_session.add_all([user1, user2])
        postgres_session.commit()
        postgres_session.refresh(user1)
        postgres_session.refresh(user2)

        reminder1 = Reminder(
            subject="User1 Task 1",
            content="For user 1",
            reminder_date=date.today(),
            user_id=user1.id,
        )
        reminder2 = Reminder(
            subject="User2 Task 1",
            content="For user 2",
            reminder_date=date.today(),
            user_id=user2.id,
        )
        reminder3 = Reminder(
            subject="User1 Task 2",
            content="Another for user 1",
            reminder_date=date.today(),
            user_id=user1.id,
        )
        postgres_session.add_all([reminder1, reminder2, reminder3])
        postgres_session.commit()

        # Query reminders for user1
        stmt = select(Reminder).where(Reminder.user_id == user1.id)
        user1_reminders = postgres_session.execute(stmt).scalars().all()

        assert len(user1_reminders) == 2
        subjects = {r.subject for r in user1_reminders}
        assert subjects == {"User1 Task 1", "User1 Task 2"}

    def test_cascade_delete_user_deletes_reminders(self, postgres_session):
        """Test that deleting a user cascades to their reminders."""
        user = User(display_name="cascadeuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="To Be Deleted",
            content="This reminder should be deleted with user",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        reminder_id = reminder.id

        # Delete user (should cascade to reminders)
        postgres_session.delete(user)
        postgres_session.commit()

        # Verify reminder is deleted
        deleted_reminder = postgres_session.get(Reminder, reminder_id)
        assert deleted_reminder is None


@pytest.mark.usefixtures("postgres_session")
class TestReminderGeneRelationship:
    """Test Reminder relationship with Gene."""

    def test_reminder_with_gene(self, postgres_session):
        """Test creating reminder associated with a gene."""
        user = User(display_name="geneuser")
        gene = Gene(
            approved_symbol="REMINDER1",
            approved_name="Reminder Test Gene",
            status="Approved",
        )
        postgres_session.add_all([user, gene])
        postgres_session.commit()
        postgres_session.refresh(user)
        postgres_session.refresh(gene)

        reminder = Reminder(
            subject="Gene Reminder",
            content="Review this gene",
            reminder_date=date.today(),
            user_id=user.id,
            hgnc_id=gene.hgnc_id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        postgres_session.refresh(reminder)

        assert reminder.hgnc_id == gene.hgnc_id

    def test_query_reminders_by_gene(self, postgres_session):
        """Test querying reminders for a specific gene."""
        user = User(display_name="genequeryuser")
        gene1 = Gene(approved_symbol="GENE1", approved_name="Gene 1", status="Approved")
        gene2 = Gene(approved_symbol="GENE2", approved_name="Gene 2", status="Approved")
        postgres_session.add_all([user, gene1, gene2])
        postgres_session.commit()
        postgres_session.refresh(user)
        postgres_session.refresh(gene1)
        postgres_session.refresh(gene2)

        reminder1 = Reminder(
            subject="Review Gene1",
            content="Review first gene",
            reminder_date=date.today(),
            user_id=user.id,
            hgnc_id=gene1.hgnc_id,
        )
        reminder2 = Reminder(
            subject="Review Gene2",
            content="Review second gene",
            reminder_date=date.today(),
            user_id=user.id,
            hgnc_id=gene2.hgnc_id,
        )
        postgres_session.add_all([reminder1, reminder2])
        postgres_session.commit()

        # Query reminders for gene1
        stmt = select(Reminder).where(Reminder.hgnc_id == gene1.hgnc_id)
        gene1_reminders = postgres_session.execute(stmt).scalars().all()

        assert len(gene1_reminders) == 1
        assert gene1_reminders[0].subject == "Review Gene1"


@pytest.mark.usefixtures("postgres_session")
class TestReminderGeneGroupRelationship:
    """Test Reminder relationship with GeneGroup."""

    def test_reminder_with_gene_group(self, postgres_session):
        """Test creating reminder associated with a gene group."""
        user = User(display_name="groupuser")
        gene_group = GeneGroup(name="Reminder Test Group")
        postgres_session.add_all([user, gene_group])
        postgres_session.commit()
        postgres_session.refresh(user)
        postgres_session.refresh(gene_group)

        reminder = Reminder(
            subject="Group Reminder",
            content="Review this gene group",
            reminder_date=date.today(),
            user_id=user.id,
            group_id=gene_group.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()
        postgres_session.refresh(reminder)

        assert reminder.group_id == gene_group.id

    def test_query_reminders_by_gene_group(self, postgres_session):
        """Test querying reminders for a specific gene group."""
        user = User(display_name="groupqueryuser")
        group1 = GeneGroup(name="Group 1")
        group2 = GeneGroup(name="Group 2")
        postgres_session.add_all([user, group1, group2])
        postgres_session.commit()
        postgres_session.refresh(user)
        postgres_session.refresh(group1)
        postgres_session.refresh(group2)

        reminder1 = Reminder(
            subject="Review Group 1",
            content="Review first group",
            reminder_date=date.today(),
            user_id=user.id,
            group_id=group1.id,
        )
        reminder2 = Reminder(
            subject="Review Group 2",
            content="Review second group",
            reminder_date=date.today(),
            user_id=user.id,
            group_id=group2.id,
        )
        postgres_session.add_all([reminder1, reminder2])
        postgres_session.commit()

        # Query reminders for group1
        stmt = select(Reminder).where(Reminder.group_id == group1.id)
        group1_reminders = postgres_session.execute(stmt).scalars().all()

        assert len(group1_reminders) == 1
        assert group1_reminders[0].subject == "Review Group 1"


@pytest.mark.usefixtures("postgres_session")
class TestReminderRepr:
    """Test Reminder __repr__ method."""

    def test_reminder_repr_with_id(self, postgres_session):
        """Test Reminder string representation includes ID and subject."""
        user = User(display_name="repruser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Repr Test",
            content="Test representation",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()

        result = repr(reminder)

        assert "Reminder" in result
        assert "Repr Test" in result


@pytest.mark.usefixtures("postgres_session")
class TestReminderDefaultValues:
    """Test Reminder default field values."""

    def test_reminder_sent_default(self, postgres_session):
        """Test sent field defaults to False."""
        user = User(display_name="defaultuser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Default Test",
            content="Test default values",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()

        assert reminder.sent is False

    def test_reminder_optional_relationships_default(self, postgres_session):
        """Test optional relationship fields default to None."""
        user = User(display_name="optionaluser")
        postgres_session.add(user)
        postgres_session.commit()
        postgres_session.refresh(user)

        reminder = Reminder(
            subject="Optional Test",
            content="Test optional fields",
            reminder_date=date.today(),
            user_id=user.id,
        )
        postgres_session.add(reminder)
        postgres_session.commit()

        # Query raw columns - gene_id and group_id should be NULL
        result = postgres_session.execute(
            text("SELECT hgnc_id, group_id FROM reminder WHERE id = :id"), {"id": reminder.id}
        ).one()

        assert result[0] is None  # hgnc_id
        assert result[1] is None  # group_id
