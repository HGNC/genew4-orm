"""Gene-GeneGroup relationship integration tests with PostgreSQL.

This module tests the many-to-many relationship between Gene and
GeneGroup through raw SQL since SQLAlchemy model relationships have issues.
"""

import pytest
from sqlalchemy import text

from genew4_orm.models import Gene, GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestGeneGeneGroupRelationships:
    """Test Gene-GeneGroup many-to-many relationships using raw SQL."""

    def test_associate_gene_with_single_group_raw_sql(self, postgres_session):
        """Test associating one gene with one group using raw SQL."""
        # First create gene and group
        gene = Gene(
            approved_symbol="RELSQL1",
            approved_name="Relationship SQL Test Gene 1",
            status="Approved",
        )
        gene_group = GeneGroup(name="Relationship SQL Test Group 1")

        postgres_session.add_all([gene, gene_group])
        postgres_session.commit()

        # Create association using raw SQL (avoiding ORM relationship issues)
        gene_id = gene.hgnc_id
        group_id = gene_group.id

        postgres_session.execute(
            text("INSERT INTO gene_has_family (hgnc_id, family_id) VALUES (:gene_id, :group_id)"),
            {"gene_id": gene_id, "group_id": group_id},
        )
        postgres_session.commit()

        # Verify association was created
        result = postgres_session.execute(
            text("SELECT * FROM gene_has_family WHERE hgnc_id = :gene_id AND family_id = :group_id"),
            {"gene_id": gene_id, "group_id": group_id},
        ).fetchone()

        assert result is not None
        assert result[0] == gene_id  # hgnc_id
        assert result[1] == group_id  # family_id

    def test_remove_gene_from_group_raw_sql(self, postgres_session):
        """Test removing a gene from a group using raw SQL."""
        # First create gene and group
        gene = Gene(
            approved_symbol="REMOVESQL1",
            approved_name="Remove SQL Test Gene",
            status="Approved",
        )
        gene_group = GeneGroup(name="Remove SQL Test Group")

        postgres_session.add_all([gene, gene_group])
        postgres_session.commit()

        # Create association
        gene_id = gene.hgnc_id
        group_id = gene_group.id

        postgres_session.execute(
            text("INSERT INTO gene_has_family (hgnc_id, family_id) VALUES (:gene_id, :group_id)"),
            {"gene_id": gene_id, "group_id": group_id},
        )
        postgres_session.commit()

        # Verify association exists
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM gene_has_family WHERE hgnc_id = :gene_id AND family_id = :group_id"),
            {"gene_id": gene_id, "group_id": group_id},
        ).scalar()
        assert result == 1  # Should exist

        # Delete association using composite primary key
        postgres_session.execute(
            text("DELETE FROM gene_has_family WHERE hgnc_id = :gene_id AND family_id = :group_id"),
            {"gene_id": gene_id, "group_id": group_id},
        )
        postgres_session.commit()

        # Verify removal
        result = postgres_session.execute(
            text("SELECT COUNT(*) FROM gene_has_family WHERE hgnc_id = :gene_id AND family_id = :group_id"),
            {"gene_id": gene_id, "group_id": group_id},
        ).scalar()

        assert result == 0  # Should be deleted

    def test_query_genes_by_group_raw_sql(self, postgres_session):
        """Test finding all genes in a group using raw SQL."""
        # Create test data
        gene1 = Gene(
            approved_symbol="GROUPSQL1",
            approved_name="Group SQL Test Gene 1",
            status="Approved",
        )
        gene2 = Gene(
            approved_symbol="GROUPSQL2",
            approved_name="Group SQL Test Gene 2",
            status="Approved",
        )
        gene_group = GeneGroup(name="Group SQL Test Group")

        postgres_session.add_all([gene1, gene2, gene_group])
        postgres_session.commit()

        # Get group ID
        group_id = gene_group.id

        # Associate both genes with the group
        for gene in [gene1, gene2]:
            postgres_session.execute(
                text("INSERT INTO gene_has_family (hgnc_id, family_id) VALUES (:gene_id, :group_id)"),
                {"gene_id": gene.hgnc_id, "group_id": group_id},
            )
        postgres_session.commit()

        # Query genes in group using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT hgnc.hgnc_id, hgnc.hgnc_app_sym
                FROM hgnc
                JOIN gene_has_family ON hgnc.hgnc_id = gene_has_family.hgnc_id
                WHERE gene_has_family.family_id = :group_id
                ORDER BY hgnc.hgnc_app_sym
            """),
            {"group_id": group_id},
        ).fetchall()

        # Should return both genes
        test_symbols = {r[1] for r in result if r[1].startswith("GROUPSQL")}
        assert test_symbols == {"GROUPSQL1", "GROUPSQL2"}

    def test_query_groups_for_gene_raw_sql(self, postgres_session):
        """Test finding all groups for a gene using raw SQL."""
        # Create test data
        gene = Gene(
            approved_symbol="GENEGROUPSQL1",
            approved_name="Gene Groups SQL Test",
            status="Approved",
        )
        group1 = GeneGroup(name="Gene Groups SQL Group 1")
        group2 = GeneGroup(name="Gene Groups SQL Group 2")

        postgres_session.add_all([gene, group1, group2])
        postgres_session.commit()

        # Get gene ID
        gene_id = gene.hgnc_id

        # Associate gene with both groups
        for group in [group1, group2]:
            postgres_session.execute(
                text("INSERT INTO gene_has_family (hgnc_id, family_id) VALUES (:gene_id, :group_id)"),
                {"gene_id": gene_id, "group_id": group.id},
            )
        postgres_session.commit()

        # Query groups for gene using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT family_new.id, family_new.name
                FROM family_new
                JOIN gene_has_family ON family_new.id = gene_has_family.family_id
                WHERE gene_has_family.hgnc_id = :gene_id
                ORDER BY family_new.name
            """),
            {"gene_id": gene_id},
        ).fetchall()

        # Should return both groups
        group_names = {r[1] for r in result if r[0] is not None}
        assert group_names == {"Gene Groups SQL Group 1", "Gene Groups SQL Group 2"}
