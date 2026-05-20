"""Unit tests for GeneHasComment junction model."""

from datetime import date

from genew4_orm.models import GeneHasComment


class TestGeneHasComment:
    """Test cases for GeneHasComment junction model."""

    def test_gene_has_comment_instantiation(self) -> None:
        """Test GeneHasComment can be instantiated with required fields."""
        gene_has_comment = GeneHasComment(
            comment_id=1,
            hgnc_id=12345,
            editor_id=5,
        )

        assert gene_has_comment.comment_id == 1
        assert gene_has_comment.hgnc_id == 12345
        assert gene_has_comment.editor_id == 5

    def test_gene_has_comment_with_date_added(self) -> None:
        """Test GeneHasComment with explicit date_added."""
        gene_has_comment = GeneHasComment(
            comment_id=1,
            hgnc_id=12345,
            editor_id=5,
            date_added=date(2025, 3, 10),
        )

        assert gene_has_comment.date_added == date(2025, 3, 10)

    def test_gene_has_comment_date_added_defaults(self) -> None:
        """Test GeneHasComment date_added defaults to today."""
        gene_has_comment = GeneHasComment(
            comment_id=1,
            hgnc_id=12345,
            editor_id=5,
        )

        assert gene_has_comment.date_added == date.today()

    def test_gene_has_comment_repr(self) -> None:
        """Test GeneHasComment __repr__ method."""
        gene_has_comment = GeneHasComment(
            comment_id=1,
            hgnc_id=12345,
            editor_id=5,
        )

        repr_str = repr(gene_has_comment)

        assert "GeneHasComment" in repr_str
        assert "comment_id=1" in repr_str
        assert "hgnc_id=12345" in repr_str

    def test_gene_has_comment_with_large_ids(self) -> None:
        """Test GeneHasComment with large ID values."""
        gene_has_comment = GeneHasComment(
            comment_id=999999,
            hgnc_id=888888,
            editor_id=777777,
        )

        assert gene_has_comment.comment_id == 999999
        assert gene_has_comment.hgnc_id == 888888
        assert gene_has_comment.editor_id == 777777
