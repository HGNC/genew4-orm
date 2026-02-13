"""Unit tests for GeneGroup model."""

import pytest

from genew4_orm.models import GeneGroup


class TestGeneGroup:
    """Test cases for GeneGroup model."""

    def test_gene_group_instantiation_minimal(self) -> None:
        """Test GeneGroup can be instantiated with minimal required fields."""
        gene_group = GeneGroup(
            name="Test Gene Group",
        )

        assert gene_group.name == "Test Gene Group"
        assert gene_group.abbreviation is None
        assert gene_group.editor is None

    def test_gene_group_instantiation_with_basic_fields(self) -> None:
        """Test GeneGroup can be instantiated with basic fields."""
        gene_group = GeneGroup(
            name="Test Gene Group",
            abbreviation="TGG",
            editor="testuser",
        )

        assert gene_group.name == "Test Gene Group"
        assert gene_group.abbreviation == "TGG"
        assert gene_group.editor == "testuser"

    def test_gene_group_with_pubmed_ids(self) -> None:
        """Test GeneGroup with PubMed IDs."""
        gene_group = GeneGroup(
            name="Test Group",
            pubmed_ids="12345678, 23456789, 34567890",
        )

        assert gene_group.pubmed_ids == "12345678, 23456789, 34567890"

    def test_gene_group_with_internal_comments(self) -> None:
        """Test GeneGroup with internal curator comments."""
        gene_group = GeneGroup(
            name="Test Group",
            internal_comments="Internal notes for curators",
        )

        assert gene_group.internal_comments == "Internal notes for curators"

    def test_gene_group_with_public_comments(self) -> None:
        """Test GeneGroup with public-facing comments."""
        gene_group = GeneGroup(
            name="Test Group",
            public_comments="Public information about this group",
        )

        assert gene_group.public_comments == "Public information about this group"

    def test_gene_group_with_description_fields(self) -> None:
        """Test GeneGroup with all description fields."""
        gene_group = GeneGroup(
            name="Test Group",
            label="Test Label",
            source="Test Source",
            typical_gene="GENE1",
            description="Full description of the gene group",
        )

        assert gene_group.label == "Test Label"
        assert gene_group.source == "Test Source"
        assert gene_group.typical_gene == "GENE1"
        assert gene_group.description == "Full description of the gene group"

    def test_gene_group_with_all_fields(self) -> None:
        """Test GeneGroup can be instantiated with all fields."""
        gene_group = GeneGroup(
            name="Complete Test Group",
            abbreviation="CTG",
            editor="curator",
            pubmed_ids="12345678",
            internal_comments="Internal note",
            public_comments="Public note",
            label="Complete Label",
            source="Complete Source",
            typical_gene="GENEX",
            description="Complete description",
        )

        assert gene_group.name == "Complete Test Group"
        assert gene_group.abbreviation == "CTG"
        assert gene_group.editor == "curator"
        assert gene_group.pubmed_ids == "12345678"
        assert gene_group.internal_comments == "Internal note"
        assert gene_group.public_comments == "Public note"
        assert gene_group.label == "Complete Label"
        assert gene_group.source == "Complete Source"
        assert gene_group.typical_gene == "GENEX"
        assert gene_group.description == "Complete description"

    def test_gene_group_all_text_fields_nullable_except_name(self) -> None:
        """Test that only name is required, all other text fields are nullable."""
        gene_group = GeneGroup(name="Required Name")

        assert gene_group.name == "Required Name"
        assert gene_group.abbreviation is None
        assert gene_group.editor is None
        assert gene_group.pubmed_ids is None
        assert gene_group.internal_comments is None
        assert gene_group.public_comments is None
        assert gene_group.label is None
        assert gene_group.source is None
        assert gene_group.typical_gene is None
        assert gene_group.description is None

    def test_gene_group_repr(self) -> None:
        """Test GeneGroup __repr__ method."""
        gene_group = GeneGroup(id=123, name="Test Group")

        repr_str = repr(gene_group)

        assert "GeneGroup" in repr_str
        assert "id=123" in repr_str
        assert "name='Test Group'" in repr_str

    def test_gene_group_repr_with_none_id(self) -> None:
        """Test GeneGroup __repr__ with None id (before save)."""
        gene_group = GeneGroup(name="Test Group")

        repr_str = repr(gene_group)

        assert "GeneGroup" in repr_str
        assert "id=None" in repr_str
        assert "name='Test Group'" in repr_str
