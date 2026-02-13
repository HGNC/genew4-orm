"""Integration tests for HierarchyClosure model with PostgreSQL.

This module tests HierarchyClosure CRUD operations with real database connections,
including testing relationships with GeneGroup for hierarchical queries.
"""

import time

import pytest
from sqlalchemy import select, text

from genew4_orm.models.hierarchy_closure import HierarchyClosure
from genew4_orm.models.gene_group import GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestHierarchyClosureCRUD:
    """Test HierarchyClosure CRUD operations with PostgreSQL."""

    def test_create_hierarchy_closure_minimal(self, postgres_session):
        """Test creating hierarchy closure with minimal required fields."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Ancestor {ts}")
        descendant = GeneGroup(name=f"Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=1,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        assert closure.ancestor_id == ancestor.id
        assert closure.descendant_id == descendant.id
        assert closure.distance == 1

    def test_create_hierarchy_closure_with_distance(self, postgres_session):
        """Test creating hierarchy closure with distance."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Distance Ancestor {ts}")
        descendant = GeneGroup(name=f"Distance Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=3,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        assert closure.distance == 3

    def test_query_hierarchy_closure_by_ancestor(self, postgres_session):
        """Test querying hierarchy closure by ancestor."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Query Ancestor {ts}")
        descendant = GeneGroup(name=f"Query Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=1,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        # Query by ancestor
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.ancestor_id == ancestor.id
        )
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.descendant_id == descendant.id

    def test_query_hierarchy_closure_by_descendant(self, postgres_session):
        """Test querying hierarchy closure by descendant."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Desc Query Ancestor {ts}")
        descendant = GeneGroup(name=f"Desc Query Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=2,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        # Query by descendant
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.descendant_id == descendant.id
        )
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.ancestor_id == ancestor.id

    def test_update_hierarchy_closure_distance(self, postgres_session):
        """Test updating hierarchy closure distance."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Update Ancestor {ts}")
        descendant = GeneGroup(name=f"Update Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=1,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        # Update distance
        closure.distance = 5
        postgres_session.commit()

        # Verify update
        assert closure.distance == 5

    def test_delete_hierarchy_closure(self, postgres_session):
        """Test deleting hierarchy closure."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Delete Ancestor {ts}")
        descendant = GeneGroup(name=f"Delete Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=1,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        ancestor_id = closure.ancestor_id
        descendant_id = closure.descendant_id
        distance = closure.distance

        # Delete closure
        postgres_session.delete(closure)
        postgres_session.commit()

        # Verify deletion using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT COUNT(*) FROM hierarchy_closure
                WHERE parent_fam_id = :ancestor_id AND child_fam_id = :descendant_id
                AND distance = :distance
            """),
            {
                "ancestor_id": ancestor_id,
                "descendant_id": descendant_id,
                "distance": distance,
            },
        ).scalar()
        assert result == 0


@pytest.mark.usefixtures("postgres_session")
class TestHierarchyClosureDistance:
    """Test HierarchyClosure distance field."""

    def test_hierarchy_closure_zero_distance(self, postgres_session):
        """Test creating closure with zero distance (self-reference)."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Self Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        closure = HierarchyClosure(
            ancestor_id=gene_group.id,
            descendant_id=gene_group.id,
            distance=0,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        assert closure.distance == 0

    def test_hierarchy_closure_large_distance(self, postgres_session):
        """Test creating closure with large distance."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Far Ancestor {ts}")
        descendant = GeneGroup(name=f"Far Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        large_distance = 100
        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=large_distance,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        assert closure.distance == large_distance

    def test_query_by_distance(self, postgres_session):
        """Test querying closures by distance."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Dist Ancestor {ts}")
        descendant1 = GeneGroup(name=f"Dist Descendant 1 {ts}")
        descendant2 = GeneGroup(name=f"Dist Descendant 2 {ts}")
        postgres_session.add_all([ancestor, descendant1, descendant2])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant1)
        postgres_session.refresh(descendant2)

        closure1 = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant1.id,
            distance=1,
        )
        closure2 = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant2.id,
            distance=5,
        )
        postgres_session.add_all([closure1, closure2])
        postgres_session.commit()

        # Query closures with distance >= 3
        stmt = select(HierarchyClosure).where(HierarchyClosure.distance >= 3)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include closure2 but not closure1
        assert any(r.descendant_id == descendant2.id for r in results)


@pytest.mark.usefixtures("postgres_session")
class TestHierarchyClosureRelationships:
    """Test HierarchyClosure relationships with GeneGroup."""

    def test_ancestor_descendant_relationship(self, postgres_session):
        """Test creating closure with proper ancestor/descendant relationship."""
        ts = int(time.time() * 1000)
        parent = GeneGroup(name=f"Parent Group {ts}")
        child = GeneGroup(name=f"Child Group {ts}")
        postgres_session.add_all([parent, child])
        postgres_session.commit()
        postgres_session.refresh(parent)
        postgres_session.refresh(child)

        closure = HierarchyClosure(
            ancestor_id=parent.id,
            descendant_id=child.id,
            distance=1,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        assert closure.ancestor_id == parent.id
        assert closure.descendant_id == child.id

    def test_multiple_descendants_same_ancestor(self, postgres_session):
        """Test creating multiple closures with same ancestor."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Multi Ancestor {ts}")
        descendant1 = GeneGroup(name=f"Multi Child 1 {ts}")
        descendant2 = GeneGroup(name=f"Multi Child 2 {ts}")
        descendant3 = GeneGroup(name=f"Multi Child 3 {ts}")
        postgres_session.add_all([ancestor, descendant1, descendant2, descendant3])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant1)
        postgres_session.refresh(descendant2)
        postgres_session.refresh(descendant3)

        descendant_ids = {descendant1.id, descendant2.id, descendant3.id}
        closures = [
            HierarchyClosure(
                ancestor_id=ancestor.id,
                descendant_id=descendant_id,
                distance=1,
            )
            for descendant_id in descendant_ids
        ]
        postgres_session.add_all(closures)
        postgres_session.commit()

        # Query all descendants for this ancestor
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.ancestor_id == ancestor.id
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should include our 3 closures
        found_ids = {r.descendant_id for r in results if r.descendant_id in descendant_ids}
        assert len(found_ids) == 3

    def test_multiple_ancestors_same_descendant(self, postgres_session):
        """Test creating multiple closures with same descendant."""
        ts = int(time.time() * 1000)
        parent1 = GeneGroup(name=f"Parent 1 {ts}")
        parent2 = GeneGroup(name=f"Parent 2 {ts}")
        child = GeneGroup(name=f"Multi Parent Child {ts}")
        postgres_session.add_all([parent1, parent2, child])
        postgres_session.commit()
        postgres_session.refresh(parent1)
        postgres_session.refresh(parent2)
        postgres_session.refresh(child)

        closures = [
            HierarchyClosure(
                ancestor_id=parent1.id,
                descendant_id=child.id,
                distance=1,
            ),
            HierarchyClosure(
                ancestor_id=parent2.id,
                descendant_id=child.id,
                distance=1,
            ),
        ]
        postgres_session.add_all(closures)
        postgres_session.commit()

        # Query all ancestors for this descendant
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.descendant_id == child.id
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should include our 2 closures
        assert len(results) >= 2


@pytest.mark.usefixtures("postgres_session")
class TestHierarchyClosureRepr:
    """Test HierarchyClosure __repr__ method."""

    def test_hierarchy_closure_repr(self, postgres_session):
        """Test HierarchyClosure string representation."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Repr Ancestor {ts}")
        descendant = GeneGroup(name=f"Repr Descendant {ts}")
        postgres_session.add_all([ancestor, descendant])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        postgres_session.refresh(descendant)

        closure = HierarchyClosure(
            ancestor_id=ancestor.id,
            descendant_id=descendant.id,
            distance=2,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        result = repr(closure)

        assert "HierarchyClosure" in result
        assert str(ancestor.id) in result
        assert str(descendant.id) in result
        assert "distance=2" in result


@pytest.mark.usefixtures("postgres_session")
class TestHierarchyClosureEdgeCases:
    """Test HierarchyClosure edge cases and special scenarios."""

    def test_create_many_hierarchy_closures(self, postgres_session):
        """Test creating many hierarchy closures."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Many Ancestor {ts}")
        descendants = [
            GeneGroup(name=f"Many Descendant {i} {ts}")
            for i in range(10)
        ]
        postgres_session.add_all([ancestor] + descendants)
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        for d in descendants:
            postgres_session.refresh(d)

        descendant_ids = {d.id for d in descendants}
        closures = []
        for descendant in descendants:
            closure = HierarchyClosure(
                ancestor_id=ancestor.id,
                descendant_id=descendant.id,
                distance=1,
            )
            closures.append(closure)
        postgres_session.add_all(closures)
        postgres_session.commit()

        # Verify all were created
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.ancestor_id == ancestor.id
        )
        results = postgres_session.execute(stmt).scalars().all()
        found_ids = {r.descendant_id for r in results if r.descendant_id in descendant_ids}
        assert len(found_ids) == 10

    def test_query_closures_in_distance_range(self, postgres_session):
        """Test querying closures within distance range."""
        ts = int(time.time() * 1000)
        ancestor = GeneGroup(name=f"Range Ancestor {ts}")
        descendant1 = GeneGroup(name=f"Range Child 1 {ts}")
        descendant2 = GeneGroup(name=f"Range Child 2 {ts}")
        descendant3 = GeneGroup(name=f"Range Child 3 {ts}")
        postgres_session.add_all([ancestor, descendant1, descendant2, descendant3])
        postgres_session.commit()
        postgres_session.refresh(ancestor)
        for d in [descendant1, descendant2, descendant3]:
            postgres_session.refresh(d)

        descendant_ids = {descendant1.id, descendant2.id, descendant3.id}
        closures = [
            HierarchyClosure(
                ancestor_id=ancestor.id,
                descendant_id=descendant1.id,
                distance=1,
            ),
            HierarchyClosure(
                ancestor_id=ancestor.id,
                descendant_id=descendant2.id,
                distance=5,
            ),
            HierarchyClosure(
                ancestor_id=ancestor.id,
                descendant_id=descendant3.id,
                distance=10,
            ),
        ]
        postgres_session.add_all(closures)
        postgres_session.commit()

        # Query closures with distance between 2 and 7
        stmt = select(HierarchyClosure).where(
            HierarchyClosure.distance.between(2, 7)
        )
        results = postgres_session.execute(stmt).scalars().all()

        # Should include distance=5 but not distance=1 or distance=10
        found = [r for r in results if r.descendant_id in descendant_ids and r.distance == 5]
        assert len(found) == 1

    def test_hierarchy_closure_with_self_reference(self, postgres_session):
        """Test closure where ancestor and descendant are the same."""
        ts = int(time.time() * 1000)
        gene_group = GeneGroup(name=f"Self Ref Group {ts}")
        postgres_session.add(gene_group)
        postgres_session.commit()
        postgres_session.refresh(gene_group)

        closure = HierarchyClosure(
            ancestor_id=gene_group.id,
            descendant_id=gene_group.id,
            distance=0,
        )
        postgres_session.add(closure)
        postgres_session.commit()

        # Verify self-reference
        assert closure.ancestor_id == closure.descendant_id
        assert closure.distance == 0
