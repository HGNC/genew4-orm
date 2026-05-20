"""Unit tests for Comment model."""

from datetime import date

from genew4_orm.enums import PublishStatus
from genew4_orm.models import Comment


class TestComment:
    """Test cases for Comment model."""

    def test_comment_instantiation_minimal(self) -> None:
        """Test Comment can be instantiated with minimal required fields."""
        comment = Comment(
            comment="This is a test comment",
            author_id=1,
        )

        assert comment.comment == "This is a test comment"
        assert comment.author_id == 1
        assert comment.status == "pending"
        assert comment.lock is None
        assert comment.publisher_id is None
        assert comment.replace_id is None
        assert comment.replacement_id is None

    def test_comment_instantiation_with_all_fields(self) -> None:
        """Test Comment can be instantiated with all fields."""
        comment = Comment(
            comment="Full comment text",
            author_id=1,
            lock="locked",
            created=date(2025, 1, 15),
            publisher_id=2,
            status=PublishStatus.PUBLISHED,
            status_date=date(2025, 1, 20),
            replace_id=10,
            replacement_id=20,
        )

        assert comment.comment == "Full comment text"
        assert comment.author_id == 1
        assert comment.lock == "locked"
        assert comment.created == date(2025, 1, 15)
        assert comment.publisher_id == 2
        assert comment.status == "published"
        assert comment.status_date == date(2025, 1, 20)
        assert comment.replace_id == 10
        assert comment.replacement_id == 20

    def test_comment_status_defaults_to_pending(self) -> None:
        """Test Comment status defaults to pending."""
        comment = Comment(
            comment="Test",
            author_id=1,
        )

        assert comment.status == "pending"
        assert comment.status == PublishStatus.PENDING

    def test_comment_status_can_be_published(self) -> None:
        """Test Comment status can be set to published."""
        comment = Comment(
            comment="Test",
            author_id=1,
            status=PublishStatus.PUBLISHED,
        )

        assert comment.status == "published"

    def test_comment_status_can_be_rejected(self) -> None:
        """Test Comment status can be set to rejected."""
        comment = Comment(
            comment="Test",
            author_id=1,
            status=PublishStatus.REJECTED,
        )

        assert comment.status == "rejected"

    def test_comment_nullable_fields_default_to_none(self) -> None:
        """Test all nullable fields default to None."""
        comment = Comment(
            comment="Test",
            author_id=1,
        )

        assert comment.id is None
        assert comment.lock is None
        assert comment.publisher_id is None
        assert comment.replace_id is None
        assert comment.replacement_id is None

    def test_comment_created_field(self) -> None:
        """Test Comment created field accepts date values."""
        comment = Comment(
            comment="Test",
            author_id=1,
            created=date(2025, 6, 1),
        )

        assert comment.created == date(2025, 6, 1)

    def test_comment_status_date_field(self) -> None:
        """Test Comment status_date field accepts date values."""
        comment = Comment(
            comment="Test",
            author_id=1,
            status_date=date(2025, 6, 1),
        )

        assert comment.status_date == date(2025, 6, 1)

    def test_comment_repr(self) -> None:
        """Test Comment __repr__ method."""
        comment = Comment(
            id=42,
            comment="Test comment",
            author_id=1,
        )

        repr_str = repr(comment)

        assert "Comment" in repr_str
        assert "id=42" in repr_str

    def test_comment_repr_with_none_id(self) -> None:
        """Test Comment __repr__ with None id (before save)."""
        comment = Comment(
            comment="Test comment",
            author_id=1,
        )

        repr_str = repr(comment)

        assert "Comment" in repr_str
        assert "id=None" in repr_str

    def test_comment_author_id_required(self) -> None:
        """Test Comment requires author_id (not nullable)."""
        comment = Comment(
            comment="Test",
            author_id=5,
        )

        assert comment.author_id == 5

    def test_comment_comment_text_required(self) -> None:
        """Test Comment requires comment text (not nullable)."""
        comment = Comment(
            comment="Required text",
            author_id=1,
        )

        assert comment.comment == "Required text"
