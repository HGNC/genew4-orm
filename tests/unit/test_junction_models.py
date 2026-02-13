"""Unit tests for junction table models."""

from datetime import date

import pytest

from genew4_orm.models import (
    FamHasCorr,
    FamHasExtResource,
    FamHasSpecialist,
    GeneHasGeneGroup,
    GeneGroupAlias,
)


class TestFamHasCorr:
    """Test cases for FamHasCorr junction model."""

    def test_fam_has_corr_instantiation(self) -> None:
        """Test FamHasCorr can be instantiated."""
        fam_has_corr = FamHasCorr(
            correspondence_id=123,
            gene_group_id=456,
        )

        assert fam_has_corr.correspondence_id == 123
        assert fam_has_corr.gene_group_id == 456

    def test_fam_has_corr_repr(self) -> None:
        """Test FamHasCorr __repr__ method."""
        fam_has_corr = FamHasCorr(
            correspondence_id=123,
            gene_group_id=456,
        )

        repr_str = repr(fam_has_corr)

        assert "FamHasCorr" in repr_str
        assert "correspondence_id=123" in repr_str
        assert "gene_group_id=456" in repr_str


class TestFamHasExtResource:
    """Test cases for FamHasExtResource junction model."""

    def test_fam_has_ext_resource_instantiation(self) -> None:
        """Test FamHasExtResource can be instantiated."""
        fam_has_ext_resource = FamHasExtResource(
            gene_group_id=789,
            external_resource_id=101,
        )

        assert fam_has_ext_resource.gene_group_id == 789
        assert fam_has_ext_resource.external_resource_id == 101

    def test_fam_has_ext_resource_repr(self) -> None:
        """Test FamHasExtResource __repr__ method."""
        fam_has_ext_resource = FamHasExtResource(
            gene_group_id=789,
            external_resource_id=101,
        )

        repr_str = repr(fam_has_ext_resource)

        assert "FamHasExtResource" in repr_str
        assert "gene_group_id=789" in repr_str
        assert "external_resource_id=101" in repr_str


class TestFamHasSpecialist:
    """Test cases for FamHasSpecialist junction model."""

    def test_fam_has_specialist_instantiation(self) -> None:
        """Test FamHasSpecialist can be instantiated."""
        fam_has_specialist = FamHasSpecialist(
            gene_group_id=999,
            specialist_id=888,
        )

        assert fam_has_specialist.gene_group_id == 999
        assert fam_has_specialist.specialist_id == 888

    def test_fam_has_specialist_repr(self) -> None:
        """Test FamHasSpecialist __repr__ method."""
        fam_has_specialist = FamHasSpecialist(
            gene_group_id=999,
            specialist_id=888,
        )

        repr_str = repr(fam_has_specialist)

        assert "FamHasSpecialist" in repr_str
        assert "gene_group_id=999" in repr_str
        assert "specialist_id=888" in repr_str


class TestGeneHasGeneGroup:
    """Test cases for GeneHasGeneGroup junction model."""

    def test_gene_has_gene_group_instantiation_minimal(self) -> None:
        """Test GeneHasGeneGroup can be instantiated with minimal fields."""
        gene_has_gene_group = GeneHasGeneGroup(
            gene_id=12345,
            gene_group_id=678,
        )

        assert gene_has_gene_group.gene_id == 12345
        assert gene_has_gene_group.gene_group_id == 678

    def test_gene_has_gene_group_instantiation_with_all_fields(self) -> None:
        """Test GeneHasGeneGroup can be instantiated with all fields."""
        gene_has_gene_group = GeneHasGeneGroup(
            gene_id=12345,
            gene_group_id=678,
            url="https://example.com/gene/12345",
            custom_sort="important",
        )

        assert gene_has_gene_group.gene_id == 12345
        assert gene_has_gene_group.gene_group_id == 678
        assert gene_has_gene_group.url == "https://example.com/gene/12345"
        assert gene_has_gene_group.custom_sort == "important"

    def test_gene_has_gene_group_with_null_optional_fields(self) -> None:
        """Test GeneHasGeneGroup with null optional fields."""
        gene_has_gene_group = GeneHasGeneGroup(
            gene_id=12345,
            gene_group_id=678,
            url=None,
            custom_sort=None,
        )

        assert gene_has_gene_group.url is None
        assert gene_has_gene_group.custom_sort is None

    def test_gene_has_gene_group_repr(self) -> None:
        """Test GeneHasGeneGroup __repr__ method."""
        gene_has_gene_group = GeneHasGeneGroup(
            gene_id=12345,
            gene_group_id=678,
        )

        repr_str = repr(gene_has_gene_group)

        assert "GeneHasGeneGroup" in repr_str
        assert "gene_id=12345" in repr_str
        assert "gene_group_id=678" in repr_str


class TestGeneGroupAlias:
    """Test cases for GeneGroupAlias model."""

    def test_gene_group_alias_instantiation_minimal(self) -> None:
        """Test GeneGroupAlias can be instantiated with minimal fields."""
        alias = GeneGroupAlias(
            alias="Test Alias",
            gene_group_id=123,
        )

        assert alias.alias == "Test Alias"
        assert alias.gene_group_id == 123

    def test_gene_group_alias_instantiation_with_all_fields(self) -> None:
        """Test GeneGroupAlias can be instantiated with all fields."""
        alias_obj = GeneGroupAlias(
            alias="Test Alias",
            gene_group_id=123,
        )

        assert alias_obj.alias == "Test Alias"
        assert alias_obj.gene_group_id == 123

    def test_gene_group_alias_repr(self) -> None:
        """Test GeneGroupAlias __repr__ method."""
        alias_obj = GeneGroupAlias(
            alias="Test Alias",
            gene_group_id=123,
        )

        repr_str = repr(alias_obj)

        assert "GeneGroupAlias" in repr_str
        assert "alias='Test Alias'" in repr_str
