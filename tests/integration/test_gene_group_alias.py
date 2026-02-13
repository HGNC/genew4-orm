"""Integration tests for GeneGroupAlias model with PostgreSQL.

This module tests GeneGroupAlias CRUD operations with real database connections,
including testing relationships with GeneGroup.
"""

import time

import pytest
from sqlalchemy import select

from genew4_orm.models.gene_group import GeneGroup
from genew4_orm.models.gene_group_alias import GeneGroupAlias


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupAliasCRUD:
    """Test GeneGroupAlias CRUD operations with PostgreSQL."""

    def test_create_gene_group_alias_minimal(self, postgres_session):
        """Test creating gene group alias with minimal required fields."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Test Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Test Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        assert alias.id is not None
        assert alias.alias == f"Test Alias {ts}"

    def test_create_gene_group_alias_with_gene_group(self, postgres_session):
        """Test creating gene group alias with a new gene group."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Test Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Group Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        assert alias.alias == f"Group Alias {ts}"
        assert alias.gene_group_id == gene_group.id

    def test_read_gene_group_alias_by_id(self, postgres_session):
        """Test reading gene group alias by ID."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Read Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Read Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        alias_id = alias.id

        # Read by ID
        retrieved_alias = postgres_session.get(GeneGroupAlias, alias_id)

        assert retrieved_alias is not None
        assert retrieved_alias.alias == f"Read Alias {ts}"

    def test_update_gene_group_alias(self, postgres_session):
        """Test updating gene group alias."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Update Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Original Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()

        # Update alias
        alias.alias = f"Updated Alias {ts}"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(alias)
        assert alias.alias == f"Updated Alias {ts}"

    def test_delete_gene_group_alias(self, postgres_session):
        """Test deleting gene group alias."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Delete Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Delete Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        alias_id = alias.id

        # Delete alias
        postgres_session.delete(alias)
        postgres_session.commit()

        # Verify deletion
        deleted_alias = postgres_session.get(GeneGroupAlias, alias_id)
        assert deleted_alias is None

    def test_query_gene_group_alias_by_pattern(self, postgres_session):
        """Test querying gene group alias by pattern."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Query Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Query Test Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()

        # Query by pattern
        stmt = select(GeneGroupAlias).where(GeneGroupAlias.alias.like(f"%Query Test%{ts}"))
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.alias == f"Query Test Alias {ts}"


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupAliasRelationship:
    """Test GeneGroupAlias relationship with GeneGroup."""

    def test_gene_group_cascade_delete(self, postgres_session):
        """Test that deleting gene group cascades to aliases."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Cascade Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Cascade Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        alias_id = alias.id

        # Delete gene group (should cascade to alias)
        postgres_session.delete(gene_group)
        postgres_session.commit()

        # Verify cascade delete
        deleted_alias = postgres_session.get(GeneGroupAlias, alias_id)
        assert deleted_alias is None

    def test_multiple_aliases_for_same_group(self, postgres_session):
        """Test creating multiple aliases for the same gene group."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Multi Alias Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        aliases = [
            GeneGroupAlias(
                alias=f"Alias {i} {ts}",
                gene_group_id=gene_group.id,
            )
            for i in range(3)
        ]
        postgres_session.add_all(aliases)
        postgres_session.commit()

        # Query all aliases for this group
        stmt = select(GeneGroupAlias).where(GeneGroupAlias.gene_group_id == gene_group.id)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include our 3 aliases
        assert len([r for r in results if f" {ts}" in r.alias]) == 3

    def test_query_aliases_by_gene_group(self, postgres_session):
        """Test querying all aliases for a specific gene group."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Find Aliases Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias1 = GeneGroupAlias(
            alias=f"Found Alias 1 {ts}",
            gene_group_id=gene_group.id,
        )
        alias2 = GeneGroupAlias(
            alias=f"Found Alias 2 {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add_all([alias1, alias2])
        postgres_session.commit()

        # Query aliases for the group
        stmt = (
            select(GeneGroupAlias).where(GeneGroupAlias.gene_group_id == gene_group.id).order_by(GeneGroupAlias.alias)
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should include our aliases
        ts_results = [r for r in results if f" {ts}" in r.alias]
        assert len(ts_results) == 2
        aliases = {r.alias for r in ts_results}
        assert aliases == {f"Found Alias 1 {ts}", f"Found Alias 2 {ts}"}


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupAliasRepr:
    """Test GeneGroupAlias __repr__ method."""

    def test_gene_group_alias_repr(self, postgres_session):
        """Test GeneGroupAlias string representation."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Repr Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias = GeneGroupAlias(
            alias=f"Repr Alias {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        result = repr(alias)

        assert "GeneGroupAlias" in result
        assert f"Repr Alias {ts}" in result
        assert str(alias.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestGeneGroupAliasEdgeCases:
    """Test GeneGroupAlias edge cases and special scenarios."""

    def test_gene_group_alias_with_special_characters(self, postgres_session):
        """Test alias with special characters."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Special Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        special_alias = f"Alias-with_special.chars@{ts}!"
        alias = GeneGroupAlias(
            alias=special_alias,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        assert alias.alias == special_alias

    def test_gene_group_alias_with_unicode(self, postgres_session):
        """Test alias with unicode characters."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Unicode Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        unicode_alias = f"Gene group α (alpha) {ts}"
        alias = GeneGroupAlias(
            alias=unicode_alias,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        assert alias.alias == unicode_alias

    def test_gene_group_alias_max_length(self, postgres_session):
        """Test alias with maximum length."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Max Length Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        max_alias = "A" * 255
        alias = GeneGroupAlias(
            alias=max_alias,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(alias)
        postgres_session.commit()
        postgres_session.refresh(alias)

        assert len(alias.alias) == 255
        assert alias.alias == max_alias

    def test_gene_group_alias_case_sensitivity(self, postgres_session):
        """Test that aliases are case sensitive."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Case Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        alias1 = GeneGroupAlias(
            alias=f"lowercase {ts}",
            gene_group_id=gene_group.id,
        )
        alias2 = GeneGroupAlias(
            alias=f"UPPERCASE {ts}",
            gene_group_id=gene_group.id,
        )
        alias3 = GeneGroupAlias(
            alias=f"MixedCase {ts}",
            gene_group_id=gene_group.id,
        )
        postgres_session.add_all([alias1, alias2, alias3])
        postgres_session.commit()

        # Verify all three are stored distinctly
        stmt = select(GeneGroupAlias).where(GeneGroupAlias.alias.like(f"%{ts}"))
        results = postgres_session.execute(stmt).scalars().all()

        ts_results = {r.alias for r in results if f" {ts}" in r.alias}
        assert ts_results == {
            f"lowercase {ts}",
            f"UPPERCASE {ts}",
            f"MixedCase {ts}",
        }

    def test_create_many_gene_group_aliases(self, postgres_session):
        """Test creating many gene group aliases."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Many Aliases Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        aliases = [
            GeneGroupAlias(
                alias=f"Many Alias {i} {ts}",
                gene_group_id=gene_group.id,
            )
            for i in range(20)
        ]
        postgres_session.add_all(aliases)
        postgres_session.commit()

        # Query all aliases for this group
        stmt = select(GeneGroupAlias).where(GeneGroupAlias.gene_group_id == gene_group.id)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include our 20 aliases
        assert len([r for r in results if f" {ts}" in r.alias]) == 20
