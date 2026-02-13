"""Unit tests for GeneGroup model relationships to improve coverage.

These tests focus on covering the relationship definitions and __repr__ method.
"""

import pytest

from genew4_orm.models import GeneGroup


class TestGeneGroupRepr:
    """Test cases for GeneGroup __repr__ method."""

    def test_gene_group_repr_with_id(self) -> None:
        """Test GeneGroup __repr__ with id."""
        gene_group = GeneGroup(id=123, name="Test Group")

        repr_str = repr(gene_group)

        assert "GeneGroup" in repr_str
        assert "id=123" in repr_str
        assert "name='Test Group'" in repr_str

    def test_gene_group_repr_with_none_id(self) -> None:
        """Test GeneGroup __repr__ with None id."""
        gene_group = GeneGroup(name="Test Group")

        repr_str = repr(gene_group)

        assert "GeneGroup" in repr_str
        assert "id=None" in repr_str
        assert "name='Test Group'" in repr_str


class TestGeneGroupRelationships:
    """Test cases for GeneGroup relationship attributes.

    These tests focus on accessing relationship attributes to ensure
    SQLAlchemy relationships are properly defined.
    """

    def test_gene_group_relationships_exist(self) -> None:
        """Test that GeneGroup has relationship attributes defined."""
        gene_group = GeneGroup(name="Test Group")

        # These should exist as defined in the model
        assert hasattr(gene_group, "gene_group_has_genes")
        assert hasattr(gene_group, "aliases")
        assert hasattr(gene_group, "parent_hierarchy_closures")
        assert hasattr(gene_group, "child_hierarchy_closures")

    def test_gene_group_relationships_can_be_none(self) -> None:
        """Test that accessing relationships on new instance doesn't error."""
        gene_group = GeneGroup(name="Test Group")

        # Accessing relationships should return empty lists/None
        # since we're not in a session
        assert gene_group.gene_group_has_genes == [] or gene_group.gene_group_has_genes is None
        assert gene_group.aliases == [] or gene_group.aliases is None
        assert gene_group.parent_hierarchy_closures == [] or gene_group.parent_hierarchy_closures is None
        assert gene_group.child_hierarchy_closures == [] or gene_group.child_hierarchy_closures is None
