"""Integration tests for Cytoband table with PostgreSQL.

This module tests Cytoband CRUD operations using raw SQL queries
since the cytoband table has no primary key and cannot be ORM-mapped.
"""

import time

import pytest
from sqlalchemy import text

from genew4_orm.enums import CytobandSourceType

# Cytoband is a dataclass for type hints, not an ORM model
# We use raw SQL for all operations on this table


@pytest.mark.usefixtures("postgres_session")
class TestCytobandCRUD:
    """Test Cytoband CRUD operations with PostgreSQL using raw SQL."""

    def test_create_cytoband_minimal(self, postgres_session):
        """Test creating cytoband record with minimal required fields."""
        ts = int(time.time() * 1000)
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                VALUES (:source, :chromosome, :start, :end, :band)
            """),
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": f"chr1_{ts}",
                "start": 1000000,
                "end": 20000000,
                "band": f"q11_{ts}",
            },
        )
        postgres_session.commit()

        # Verify the record was created
        result = postgres_session.execute(
            text("""
                SELECT cb_source, cb_chr, cb_band, cb_start, cb_end
                FROM cytoband
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {"chromosome": f"chr1_{ts}", "band": f"q11_{ts}"},
        ).fetchone()

        assert result is not None
        assert result[0] == str(CytobandSourceType.UCSC)
        assert result[1] == f"chr1_{ts}"
        assert result[2] == f"q11_{ts}"

    def test_create_cytoband_with_all_fields(self, postgres_session):
        """Test creating cytoband record with all fields."""
        ts = int(time.time() * 1000)
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band, cb_stain)
                VALUES (:source, :chromosome, :start, :end, :band, :stain)
            """),
            {
                "source": str(CytobandSourceType.ENSEMBL),
                "chromosome": f"chrX_{ts}",
                "start": 1,
                "end": 50000000,
                "band": f"p11_{ts}",
                "stain": "negative",
            },
        )
        postgres_session.commit()

        # Verify the record was created
        result = postgres_session.execute(
            text("""
                SELECT cb_source, cb_chr, cb_band, cb_stain
                FROM cytoband
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {"chromosome": f"chrX_{ts}", "band": f"p11_{ts}"},
        ).fetchone()

        assert result is not None
        assert result[0] == str(CytobandSourceType.ENSEMBL)
        assert result[3] == "negative"


@pytest.mark.usefixtures("postgres_session")
class TestCytobandQuery:
    """Test Cytoband query operations with PostgreSQL using raw SQL."""

    def test_query_cytoband_by_chromosome(self, postgres_session):
        """Test querying cytoband by chromosome pattern."""
        ts = int(time.time() * 1000)
        # Create test cytobands
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                VALUES (:source, :chromosome1, :start1, :end1, :band1),
                       (:source, :chromosome2, :start2, :end2, :band2)
            """),
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome1": f"query_chr1_{ts}",
                "start1": 1000000,
                "end1": 20000000,
                "band1": f"q11_{ts}",
                "chromosome2": f"query_chr2_{ts}",
                "start2": 20000001,
                "end2": 40000000,
                "band2": f"q21_{ts}",
            },
        )
        postgres_session.commit()

        # Query by chromosome pattern
        results = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM cytoband WHERE cb_chr LIKE :pattern
            """),
            {"pattern": f"query_chr%_{ts}"},
        ).scalar()

        assert results == 2

    def test_query_cytoband_by_source(self, postgres_session):
        """Test querying cytoband by data source."""
        ts = int(time.time() * 1000)
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                VALUES (:source, :chromosome, :start, :end, :band)
            """),
            {
                "source": str(CytobandSourceType.ENSEMBL),
                "chromosome": f"ensembl_chr1_{ts}",
                "start": 1,
                "end": 10000000,
                "band": f"p11_{ts}",
            },
        )
        postgres_session.commit()

        # Query by source
        results = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM cytoband WHERE cb_source = :source
            """),
            {"source": str(CytobandSourceType.ENSEMBL)},
        ).scalar()

        # Should include at least our Ensembl record
        assert results >= 1


@pytest.mark.usefixtures("postgres_session")
class TestCytobandUpdate:
    """Test Cytoband update operations with raw SQL."""

    def test_update_cytoband_fields(self, postgres_session):
        """Test updating cytoband fields."""
        ts = int(time.time() * 1000)
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band, cb_stain)
                VALUES (:source, :chromosome, :start, :end, :band, :stain)
            """),
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": f"update_chr1_{ts}",
                "start": 1000000,
                "end": 20000000,
                "band": f"q11_{ts}",
                "stain": "original",
            },
        )
        postgres_session.commit()

        # Update fields
        postgres_session.execute(
            text("""
                UPDATE cytoband
                SET cb_stain = :stain, cb_end = :end
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {
                "chromosome": f"update_chr1_{ts}",
                "band": f"q11_{ts}",
                "stain": "updated",
                "end": 25000000,
            },
        )
        postgres_session.commit()

        # Verify update
        result = postgres_session.execute(
            text("""
                SELECT cb_stain, cb_end FROM cytoband
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {"chromosome": f"update_chr1_{ts}", "band": f"q11_{ts}"},
        ).fetchone()

        assert result is not None
        assert result[0] == "updated"
        assert result[1] == 25000000


@pytest.mark.usefixtures("postgres_session")
class TestCytobandDelete:
    """Test Cytoband delete operations with raw SQL."""

    def test_delete_cytoband(self, postgres_session):
        """Test deleting cytoband record."""
        ts = int(time.time() * 1000)
        postgres_session.execute(
            text("""
                INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                VALUES (:source, :chromosome, :start, :end, :band)
            """),
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": f"delete_chr1_{ts}",
                "start": 1000000,
                "end": 20000000,
                "band": f"q11_{ts}",
            },
        )
        postgres_session.commit()

        # Delete cytoband
        postgres_session.execute(
            text("""
                DELETE FROM cytoband
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {"chromosome": f"delete_chr1_{ts}", "band": f"q11_{ts}"},
        )
        postgres_session.commit()

        # Verify deletion
        result = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM cytoband
                WHERE cb_chr = :chromosome AND cb_band = :band
            """),
            {"chromosome": f"delete_chr1_{ts}", "band": f"q11_{ts}"},
        ).scalar()

        assert result == 0


@pytest.mark.usefixtures("postgres_session")
class TestCytobandEdgeCases:
    """Test Cytoband edge cases and special scenarios."""

    def test_create_multiple_cytobands_same_chromosome(self, postgres_session):
        """Test creating multiple cytobands for the same chromosome."""
        ts = int(time.time() * 1000)
        base_chromosome = f"multi_chr1_{ts}"
        cytobands = [
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": base_chromosome,
                "band": f"p11_{ts}",
                "start": 1,
                "end": 10000000,
            },
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": base_chromosome,
                "band": f"q11_{ts}",
                "start": 10000001,
                "end": 30000000,
            },
            {
                "source": str(CytobandSourceType.UCSC),
                "chromosome": base_chromosome,
                "band": f"q21_{ts}",
                "start": 30000001,
                "end": 50000000,
            },
        ]

        for cytoband in cytobands:
            postgres_session.execute(
                text("""
                    INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                    VALUES (:source, :chromosome, :start, :end, :band)
                """),
                cytoband,
            )
        postgres_session.commit()

        # Query all bands for this chromosome
        result = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM cytoband WHERE cb_chr = :chromosome
            """),
            {"chromosome": base_chromosome},
        ).scalar()

        assert result >= 3

    def test_cytoband_position_ranges(self, postgres_session):
        """Test cytoband with various position ranges."""
        ts = int(time.time() * 1000)
        test_ranges = [
            (1, 1000, "tiny"),
            (1000000, 20000000, "small"),
            (50000000, 150000000, "medium"),
            (1, 250000000, "large"),
        ]
        for start, end, label in test_ranges:
            postgres_session.execute(
                text("""
                    INSERT INTO cytoband (cb_source, cb_chr, cb_start, cb_end, cb_band)
                    VALUES (:source, :chromosome, :start, :end, :band)
                """),
                {
                    "source": str(CytobandSourceType.UCSC),
                    "chromosome": f"range_chr_{label}_{ts}",
                    "start": start,
                    "end": end,
                    "band": f"band_{label}_{ts}",
                },
            )
        postgres_session.commit()

        # Verify records were created
        result = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM cytoband WHERE cb_chr LIKE :pattern
            """),
            {"pattern": f"range_chr%_{ts}"},
        ).scalar()

        assert result >= 4
