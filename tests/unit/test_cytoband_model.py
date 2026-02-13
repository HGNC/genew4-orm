"""Unit tests for Cytoband model."""

from genew4_orm.enums import CytobandSourceType
from genew4_orm.models.cytoband import Cytoband


class TestCytoband:
    """Test cases for Cytoband dataclass."""

    def test_cytoband_instantiation_with_all_fields(self) -> None:
        """Test Cytoband can be instantiated with all fields."""
        cytoband = Cytoband(
            source=CytobandSourceType.UCSC,
            chromosome="chr1",
            start=1000,
            end=5000,
            band="p36.33",
            stain="gneg",
        )

        assert cytoband.source == CytobandSourceType.UCSC
        assert cytoband.chromosome == "chr1"
        assert cytoband.start == 1000
        assert cytoband.end == 5000
        assert cytoband.band == "p36.33"
        assert cytoband.stain == "gneg"

    def test_cytoband_instantiation_with_none_values(self) -> None:
        """Test Cytoband can be instantiated with None values."""
        cytoband = Cytoband(
            source=None,
            chromosome=None,
            start=None,
            end=None,
            band=None,
            stain=None,
        )

        assert cytoband.source is None
        assert cytoband.chromosome is None
        assert cytoband.start is None
        assert cytoband.end is None
        assert cytoband.band is None
        assert cytoband.stain is None

    def test_cytoband_repr_with_all_fields(self) -> None:
        """Test __repr__ includes relevant information."""
        cytoband = Cytoband(
            source=CytobandSourceType.UCSC,
            chromosome="chr1",
            start=1000,
            end=5000,
            band="p36.33",
            stain="gneg",
        )

        repr_str = repr(cytoband)

        assert "Cytoband" in repr_str
        assert "UCSC" in repr_str
        assert "chr1" in repr_str
        assert "p36.33" in repr_str

    def test_cytoband_repr_with_none_values(self) -> None:
        """Test __repr__ handles None values gracefully."""
        cytoband = Cytoband(
            source=None,
            chromosome=None,
            start=None,
            end=None,
            band=None,
            stain=None,
        )

        repr_str = repr(cytoband)

        assert "Cytoband" in repr_str
        # Should show 'None' for chromosome and band when None
        assert "None" in repr_str

    def test_cytoband_with_ensembl_source(self) -> None:
        """Test Cytoband with Ensembl source."""
        cytoband = Cytoband(
            source=CytobandSourceType.ENSEMBL,
            chromosome="chrX",
            start=100000,
            end=200000,
            band="q27",
            stain="gpos100",
        )

        assert cytoband.source == CytobandSourceType.ENSEMBL
        assert cytoband.chromosome == "chrX"
        assert cytoband.stain == "gpos100"

    def test_cytoband_partial_fields(self) -> None:
        """Test Cytoband can have partial field values."""
        cytoband = Cytoband(
            source=CytobandSourceType.UCSC,
            chromosome="chr7",
            band=None,
            stain=None,
            start=None,
            end=None,
        )

        assert cytoband.source == CytobandSourceType.UCSC
        assert cytoband.chromosome == "chr7"
        assert cytoband.band is None
        assert cytoband.stain is None
        assert cytoband.start is None
        assert cytoband.end is None
