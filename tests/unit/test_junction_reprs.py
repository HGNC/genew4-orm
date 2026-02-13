"""Unit tests for junction table models __repr__ methods.

These tests focus on improving coverage for the Fam* junction table models.
"""

import pytest

from genew4_orm.models import (
    FamHasCorr,
    FamHasExtResource,
    FamHasSpecialist,
)


class TestFamHasCorrRepr:
    """Test cases for FamHasCorr __repr__ method."""

    def test_fam_has_corr_repr_with_none_values(self) -> None:
        """Test FamHasCorr __repr__ handles None values."""
        # Create instance with None values to test repr
        fam_has_corr = FamHasCorr(
            correspondence_id=None,
            gene_group_id=None,
        )

        # The __repr__ should handle None values gracefully
        repr_str = repr(fam_has_corr)

        assert "FamHasCorr" in repr_str
        # Check it formats with None values
        assert "correspondence_id=None" in repr_str

    def test_fam_has_corr_repr_with_zero_values(self) -> None:
        """Test FamHasCorr __repr__ handles zero values."""
        fam_has_corr = FamHasCorr(
            correspondence_id=0,
            gene_group_id=0,
        )

        repr_str = repr(fam_has_corr)

        assert "correspondence_id=0" in repr_str
        assert "gene_group_id=0" in repr_str


class TestFamHasExtResourceRepr:
    """Test cases for FamHasExtResource __repr__ method."""

    def test_fam_has_ext_resource_repr_with_none_values(self) -> None:
        """Test FamHasExtResource __repr__ handles None values."""
        # Create instance with None values to test repr
        fam_has_ext = FamHasExtResource(
            external_resource_id=None,
            gene_group_id=None,
        )

        # The __repr__ should handle None values gracefully
        repr_str = repr(fam_has_ext)

        assert "FamHasExtResource" in repr_str
        # Check it formats with None values
        assert "external_resource_id=None" in repr_str

    def test_fam_has_ext_resource_repr_with_zero_values(self) -> None:
        """Test FamHasExtResource __repr__ handles zero values."""
        fam_has_ext = FamHasExtResource(
            external_resource_id=0,
            gene_group_id=0,
        )

        repr_str = repr(fam_has_ext)

        assert "external_resource_id=0" in repr_str
        assert "gene_group_id=0" in repr_str


class TestFamHasSpecialistRepr:
    """Test cases for FamHasSpecialist __repr__ method."""

    def test_fam_has_specialist_repr_with_none_values(self) -> None:
        """Test FamHasSpecialist __repr__ handles None values."""
        # Create instance with None values to test repr
        fam_has_spec = FamHasSpecialist(
            gene_group_id=None,
            specialist_id=None,
        )

        # The __repr__ should handle None values gracefully
        repr_str = repr(fam_has_spec)

        assert "FamHasSpecialist" in repr_str
        # Check it formats with None values
        assert "gene_group_id=None" in repr_str

    def test_fam_has_specialist_repr_with_zero_values(self) -> None:
        """Test FamHasSpecialist __repr__ handles zero values."""
        fam_has_spec = FamHasSpecialist(
            gene_group_id=0,
            specialist_id=0,
        )

        repr_str = repr(fam_has_spec)

        assert "gene_group_id=0" in repr_str
        assert "specialist_id=0" in repr_str
