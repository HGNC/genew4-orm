"""Integration tests for Grch38Mapping model with PostgreSQL.

This module tests Grch38Mapping CRUD operations with real database connections.
Note: This table uses a composite primary key with no auto-increment ID.
"""

import time

import pytest
from sqlalchemy import select, text

from genew4_orm.models.grch38_mapping import Grch38Mapping
from genew4_orm.enums import Grch38SourceType, Grch38MarkType


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingCRUD:
    """Test Grch38Mapping CRUD operations with PostgreSQL."""

    def test_create_grch38_mapping_minimal(self, postgres_session):
        """Test creating GRCh38 mapping with minimal required fields."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.NCBI
        assert mapping.chromosome == f"chr1_{ts}"
        assert mapping.start == 1000000
        assert mapping.end == 2000000

    def test_create_grch38_mapping_with_all_fields(self, postgres_session):
        """Test creating GRCh38 mapping with all fields."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.ENSEMBL,
            strand="-",
            chromosome=f"chrX_{ts}",
            start=5000000,
            end=15000000,
            map_by=f"complete_test_{ts}",
            source_id=f"ENSG00001{ts}",
            ncbi_gene_id=12345,
            hgnc_id=6789,
            notes=f"Test mapping notes {ts}",
            mark=Grch38MarkType.MAX,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.ENSEMBL
        assert mapping.strand == "-"
        assert mapping.chromosome == f"chrX_{ts}"
        assert mapping.source_id == f"ENSG00001{ts}"
        assert mapping.ncbi_gene_id == 12345
        assert mapping.hgnc_id == 6789
        assert mapping.notes == f"Test mapping notes {ts}"
        assert mapping.mark == Grch38MarkType.MAX

    def test_query_grch38_mapping_by_chromosome(self, postgres_session):
        """Test querying GRCh38 mapping by chromosome."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"query_chr2_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"query_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        # Query by chromosome
        stmt = select(Grch38Mapping).where(
            Grch38Mapping.chromosome == f"query_chr2_{ts}"
        )
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.strand == "+"

    def test_update_grch38_mapping(self, postgres_session):
        """Test updating GRCh38 mapping."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"update_chr3_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"update_test_{ts}",
            notes="Original notes",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        # Update fields
        mapping.notes = f"Updated notes {ts}"
        mapping.hgnc_id = 99999
        postgres_session.commit()

        # Verify update
        assert mapping.notes == f"Updated notes {ts}"
        assert mapping.hgnc_id == 99999

    def test_delete_grch38_mapping(self, postgres_session):
        """Test deleting GRCh38 mapping."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.HGNC,
            strand="-",
            chromosome=f"delete_chr4_{ts}",
            start=5000000,
            end=10000000,
            map_by=f"delete_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        chromosome = mapping.chromosome
        source = mapping.source
        strand = mapping.strand
        start = mapping.start
        end = mapping.end
        map_by = mapping.map_by

        # Delete mapping
        postgres_session.delete(mapping)
        postgres_session.commit()

        # Verify deletion using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM coord_match_grch38
                WHERE cm_source = :source AND cm_strand = :strand
                AND cm_chr = :chromosome AND cm_start = :start
                AND cm_end = :end AND cm_mapby = :map_by
            """),
            {
                "source": source,
                "strand": strand,
                "chromosome": chromosome,
                "start": start,
                "end": end,
                "map_by": map_by,
            },
        ).scalar()
        assert result == 0


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingStrand:
    """Test Grch38Mapping strand field."""

    def test_grch38_mapping_forward_strand(self, postgres_session):
        """Test creating mapping with forward strand (+)."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"fwd_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"fwd_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.strand == "+"

    def test_grch38_mapping_reverse_strand(self, postgres_session):
        """Test creating mapping with reverse strand (-)."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="-",
            chromosome=f"rev_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"rev_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.strand == "-"

    def test_query_by_strand(self, postgres_session):
        """Test querying mappings by strand."""
        ts = int(time.time() * 1000)
        mapping_plus = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"strand_query_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"strand_plus_{ts}",
        )
        mapping_minus = Grch38Mapping(
            source=Grch38SourceType.ENSEMBL,
            strand="-",
            chromosome=f"strand_query_chr2_{ts}",
            start=3000000,
            end=4000000,
            map_by=f"strand_minus_{ts}",
        )
        postgres_session.add_all([mapping_plus, mapping_minus])
        postgres_session.commit()

        # Query forward strand mappings
        stmt = select(Grch38Mapping).where(Grch38Mapping.strand == "+")
        results = postgres_session.execute(stmt).scalars().all()

        # Should include at least our forward strand mapping
        assert any(r.chromosome == f"strand_query_chr1_{ts}" for r in results)


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingSource:
    """Test Grch38Mapping source field."""

    def test_grch38_mapping_ncbi_source(self, postgres_session):
        """Test creating mapping with NCBI source."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"ncbi_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"ncbi_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.NCBI

    def test_grch38_mapping_ensembl_source(self, postgres_session):
        """Test creating mapping with Ensembl source."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.ENSEMBL,
            strand="+",
            chromosome=f"ensembl_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"ensembl_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.ENSEMBL

    def test_grch38_mapping_chrom_source(self, postgres_session):
        """Test creating mapping with Chrom source."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.CHROM,
            strand="+",
            chromosome=f"chrom_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"chrom_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.CHROM

    def test_grch38_mapping_hgnc_source(self, postgres_session):
        """Test creating mapping with HGNC source."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.HGNC,
            strand="+",
            chromosome=f"hgnc_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"hgnc_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source == Grch38SourceType.HGNC


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingOptionalFields:
    """Test Grch38Mapping optional fields."""

    def test_grch38_mapping_with_source_id(self, postgres_session):
        """Test creating mapping with source_id."""
        ts = int(time.time() * 1000)
        source_id = f"ENSG00001234{ts}"
        mapping = Grch38Mapping(
            source=Grch38SourceType.ENSEMBL,
            strand="+",
            chromosome=f"sid_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"sid_test_{ts}",
            source_id=source_id,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.source_id == source_id

    def test_grch38_mapping_with_ncbi_gene_id(self, postgres_session):
        """Test creating mapping with NCBI gene ID."""
        ts = int(time.time() * 1000)
        ncbi_id = 12345678
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"ncbiid_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"ncbiid_test_{ts}",
            ncbi_gene_id=ncbi_id,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.ncbi_gene_id == ncbi_id

    def test_grch38_mapping_with_hgnc_id(self, postgres_session):
        """Test creating mapping with HGNC ID."""
        ts = int(time.time() * 1000)
        hgnc_id = 98765
        mapping = Grch38Mapping(
            source=Grch38SourceType.HGNC,
            strand="+",
            chromosome=f"hgncid_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"hgncid_test_{ts}",
            hgnc_id=hgnc_id,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.hgnc_id == hgnc_id

    def test_grch38_mapping_with_notes(self, postgres_session):
        """Test creating mapping with notes."""
        ts = int(time.time() * 1000)
        notes = f"Detailed mapping notes for testing {ts}"
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"notes_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"notes_test_{ts}",
            notes=notes,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.notes == notes

    def test_grch38_mapping_with_mark(self, postgres_session):
        """Test creating mapping with mark type."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"mark_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"mark_test_{ts}",
            mark=Grch38MarkType.HIDDEN,
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        assert mapping.mark == Grch38MarkType.HIDDEN


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingRepr:
    """Test Grch38Mapping __repr__ method."""

    def test_grch38_mapping_repr(self, postgres_session):
        """Test Grch38Mapping string representation."""
        ts = int(time.time() * 1000)
        mapping = Grch38Mapping(
            source=Grch38SourceType.NCBI,
            strand="+",
            chromosome=f"repr_chr1_{ts}",
            start=1000000,
            end=2000000,
            map_by=f"repr_test_{ts}",
        )
        postgres_session.add(mapping)
        postgres_session.commit()

        result = repr(mapping)

        assert "Grch38Mapping" in result
        assert "NCBI" in result
        assert f"repr_chr1_{ts}" in result


@pytest.mark.usefixtures("postgres_session")
class TestGrch38MappingEdgeCases:
    """Test Grch38Mapping edge cases and special scenarios."""

    def test_grch38_mapping_different_chromosomes(self, postgres_session):
        """Test creating mappings for different chromosomes."""
        ts = int(time.time() * 1000)
        chromosomes = [
            f"chr1_{ts}",
            f"chr2_{ts}",
            f"chrX_{ts}",
            f"chrY_{ts}",
            f"chrMT_{ts}",
        ]
        for chromosome in chromosomes:
            mapping = Grch38Mapping(
                source=Grch38SourceType.NCBI,
                strand="+",
                chromosome=chromosome,
                start=1000000,
                end=2000000,
                map_by=f"multi_chr_{ts}",
            )
            postgres_session.add(mapping)
        postgres_session.commit()

        # Verify all created
        stmt = select(Grch38Mapping).where(Grch38Mapping.map_by == f"multi_chr_{ts}")
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) >= 5

    def test_grch38_mapping_position_ranges(self, postgres_session):
        """Test mappings with various position ranges."""
        ts = int(time.time() * 1000)
        ranges = [
            (1, 1000, "tiny"),
            (1000000, 20000000, "small"),
            (50000000, 150000000, "medium"),
            (1, 250000000, "large"),
        ]
        for start, end, label in ranges:
            mapping = Grch38Mapping(
                source=Grch38SourceType.NCBI,
                strand="+",
                chromosome=f"range_chr_{label}_{ts}",
                start=start,
                end=end,
                map_by=f"range_test_{label}_{ts}",
            )
            postgres_session.add(mapping)
        postgres_session.commit()

        # Verify records were created
        stmt = select(Grch38Mapping).where(Grch38Mapping.map_by.like(f"range_test%_{ts}"))
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) >= 4
