"""Integration tests for ExternalResource model with PostgreSQL.

This module tests ExternalResource CRUD operations with real database connections,
including testing relationships with GeneGroup.
"""

import time

import pytest
from sqlalchemy import select, text

from genew4_orm.models.external_resource import ExternalResource
from genew4_orm.models.fam_has_ext_resource import FamHasExtResource
from genew4_orm.models.gene_group import GeneGroup


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceCRUD:
    """Test ExternalResource CRUD operations with PostgreSQL."""

    def test_create_external_resource_minimal(self, postgres_session):
        """Test creating external resource with minimal required fields."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Test Resource {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/resource/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.id is not None
        assert resource.name == f"Test Resource {ts}"
        assert resource.url == f"https://test-{ts}.test-{ts}.example.com/resource/{ts}"
        assert resource.approved is False  # Default value

    def test_create_external_resource_with_all_fields(self, postgres_session):
        """Test creating external resource with all fields."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Complete Resource {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/complete/{ts}",
            description=f"A complete test resource {ts}",
            approved=True,
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.name == f"Complete Resource {ts}"
        assert resource.url == f"https://test-{ts}.test-{ts}.example.com/complete/{ts}"
        assert resource.description == f"A complete test resource {ts}"
        assert resource.approved is True

    def test_read_external_resource_by_id(self, postgres_session):
        """Test reading external resource by ID."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Read Test {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/read/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        resource_id = resource.id

        # Read by ID
        retrieved_resource = postgres_session.get(ExternalResource, resource_id)

        assert retrieved_resource is not None
        assert retrieved_resource.name == f"Read Test {ts}"
        assert retrieved_resource.url == f"https://test-{ts}.test-{ts}.example.com/read/{ts}"

    def test_update_external_resource_fields(self, postgres_session):
        """Test updating external resource fields."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Original Resource {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/original/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()

        # Update fields
        resource.name = f"Updated Resource {ts}"
        resource.url = f"https://test-{ts}.test-{ts}.example.com/updated/{ts}"
        resource.approved = True
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(resource)
        assert resource.name == f"Updated Resource {ts}"
        assert resource.url == f"https://test-{ts}.test-{ts}.example.com/updated/{ts}"
        assert resource.approved is True

    def test_delete_external_resource(self, postgres_session):
        """Test deleting external resource."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Delete Test {ts}",
            url=f"https://test-{ts}.example.com/delete/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        resource_id = resource.id

        # Delete resource
        postgres_session.delete(resource)
        postgres_session.commit()

        # Verify deletion
        deleted_resource = postgres_session.get(ExternalResource, resource_id)
        assert deleted_resource is None

    def test_query_external_resource_by_name(self, postgres_session):
        """Test querying external resource by name pattern."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Query Test Resource {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/query/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()

        # Query by name pattern
        stmt = select(ExternalResource).where(ExternalResource.name.like(f"%Query Test%{ts}"))
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.url == f"https://test-{ts}.test-{ts}.example.com/query/{ts}"


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceApproved:
    """Test ExternalResource approved field."""

    def test_external_resource_default_not_approved(self, postgres_session):
        """Test that external resource defaults to approved=False."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Not Approved {ts}",
            url=f"https://test-{ts}.example.com/not_approved/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.approved is False

    def test_external_resource_set_approved(self, postgres_session):
        """Test setting external resource to approved."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Approved Resource {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/approved/{ts}",
            approved=True,
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.approved is True

    def test_query_approved_resources(self, postgres_session):
        """Test querying only approved resources."""
        ts = int(time.time() * 1000)
        approved_resource = ExternalResource(
            name=f"Approved {ts}",
            url=f"https://test-{ts}.example.com/approved_{ts}",
            approved=True,
        )
        unapproved_resource = ExternalResource(
            name=f"Unapproved {ts}",
            url=f"https://test-{ts}.example.com/unapproved_{ts}",
            approved=False,
        )
        postgres_session.add_all([approved_resource, unapproved_resource])
        postgres_session.commit()

        # Query only approved resources
        stmt = select(ExternalResource).where(ExternalResource.approved)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include approved_resource
        assert any(r.name == f"Approved {ts}" for r in results)

    def test_query_unapproved_resources(self, postgres_session):
        """Test querying only unapproved resources."""
        ts = int(time.time() * 1000)
        unapproved_resource = ExternalResource(
            name=f"Unapproved Query {ts}",
            url=f"https://test-{ts}.example.com/unapproved_query_{ts}",
            approved=False,
        )
        approved_resource = ExternalResource(
            name=f"Approved Query {ts}",
            url=f"https://test-{ts}.example.com/approved_query_{ts}",
            approved=True,
        )
        postgres_session.add_all([unapproved_resource, approved_resource])
        postgres_session.commit()

        # Query only unapproved resources
        stmt = select(ExternalResource).where(ExternalResource.approved == False)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include unapproved_resource
        assert any(r.name == f"Unapproved Query {ts}" for r in results)

    def test_approve_existing_resource(self, postgres_session):
        """Test approving an existing resource."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"To Approve {ts}",
            url=f"https://test-{ts}.example.com/to_approve/{ts}",
            approved=False,
        )
        postgres_session.add(resource)
        postgres_session.commit()

        # Approve resource
        resource.approved = True
        postgres_session.commit()

        # Verify
        postgres_session.refresh(resource)
        assert resource.approved is True


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceDescription:
    """Test ExternalResource description field."""

    def test_external_resource_with_description(self, postgres_session):
        """Test creating external resource with description."""
        ts = int(time.time() * 1000)
        description = f"A comprehensive database of genetic information {ts}"
        resource = ExternalResource(
            name=f"With Description {ts}",
            url=f"https://test-{ts}.example.com/with_desc/{ts}",
            description=description,
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.description == description

    def test_external_resource_without_description(self, postgres_session):
        """Test creating external resource without description (null)."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"No Description {ts}",
            url=f"https://test-{ts}.example.com/no_desc/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.description is None

    def test_query_external_resource_by_description(self, postgres_session):
        """Test querying resources by description pattern."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Desc Query {ts}",
            url=f"https://test-{ts}.example.com/desc_query/{ts}",
            description=f"Genetic database with focus on cancer {ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()

        # Query by description pattern
        stmt = select(ExternalResource).where(ExternalResource.description.like(f"%cancer%{ts}"))
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.name == f"Desc Query {ts}"


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceURL:
    """Test ExternalResource URL field."""

    def test_external_resource_with_various_url_formats(self, postgres_session):
        """Test external resource with various URL formats."""
        ts = int(time.time() * 1000)
        urls = [
            f"https://test-{ts}.example.com/{ts}",
            f"http://example.org/{ts}",
            f"https://api.example.net/v1/resource/{ts}",
            f"ftp://files.test-{ts}.example.com/data/{ts}",
        ]
        for i, url in enumerate(urls):
            resource = ExternalResource(
                name=f"URL Test {i} {ts}",
                url=url,
            )
            postgres_session.add(resource)
        postgres_session.commit()

        # Verify all created
        stmt = select(ExternalResource).where(ExternalResource.url.like(f"%{ts}"))
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) >= 4

    def test_query_external_resource_by_url(self, postgres_session):
        """Test querying resource by URL pattern."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"URL Query {ts}",
            url=f"https://api.test-{ts}.example.com/v1/genes/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()

        # Query by URL pattern
        stmt = select(ExternalResource).where(ExternalResource.url.like(f"%/genes/%{ts}"))
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.name == f"URL Query {ts}"


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceGeneGroupRelationship:
    """Test ExternalResource relationship with GeneGroup via FamHasExtResource."""

    def test_external_resource_with_gene_group(self, postgres_session):
        """Test associating external resource with a gene group."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Test Resource {ts}",
            url=f"https://test-{ts}.example.com/resource/{ts}",
        )
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([resource, gene_group])
        postgres_session.commit()
        postgres_session.refresh(resource)
        postgres_session.refresh(gene_group)

        # Create association via junction table
        association = FamHasExtResource(
            external_resource_id=resource.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        # Verify the association was created
        assert association.external_resource_id == resource.id
        assert association.gene_group_id == gene_group.id

    def test_query_resources_for_gene_group(self, postgres_session):
        """Test finding external resources for a gene group."""
        ts = int(time.time() * 1000)
        resource1 = ExternalResource(
            name=f"Resource 1 {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/r1/{ts}",
        )
        resource2 = ExternalResource(
            name=f"Resource 2 {ts}",
            url=f"https://test-{ts}.test-{ts}.example.com/r2/{ts}",
        )
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([resource1, resource2, gene_group])
        postgres_session.commit()
        postgres_session.refresh(resource1)
        postgres_session.refresh(resource2)
        postgres_session.refresh(gene_group)

        # Associate both resources with the group
        association1 = FamHasExtResource(
            external_resource_id=resource1.id,
            gene_group_id=gene_group.id,
        )
        association2 = FamHasExtResource(
            external_resource_id=resource2.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add_all([association1, association2])
        postgres_session.commit()

        # Query resources for the group using raw SQL
        result = postgres_session.execute(
            text("""
                SELECT er.id, er.name, er.url
                FROM external_resource er
                JOIN family_has_external_resource ON er.id = family_has_external_resource.ext_id
                WHERE family_has_external_resource.family_id = :group_id
                ORDER BY er.name
            """),
            {"group_id": gene_group.id},
        ).fetchall()

        assert len(result) == 2
        names = {r[1] for r in result}
        assert names == {f"Resource 1 {ts}", f"Resource 2 {ts}"}


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceRepr:
    """Test ExternalResource __repr__ method."""

    def test_external_resource_repr(self, postgres_session):
        """Test ExternalResource string representation."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Repr Test {ts}",
            url=f"https://test-{ts}.example.com/repr/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        result = repr(resource)

        assert "ExternalResource" in result
        assert f"Repr Test {ts}" in result
        assert str(resource.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestFamHasExtResourceRepr:
    """Test FamHasExtResource __repr__ method."""

    def test_fam_has_ext_resource_repr(self, postgres_session):
        """Test FamHasExtResource string representation."""
        ts = int(time.time() * 1000)
        resource = ExternalResource(
            name=f"Test Resource {ts}",
            url=f"https://test-{ts}.example.com/test/{ts}",
        )
        gene_group = GeneGroup(name=f"Test Group {ts}")

        postgres_session.add_all([resource, gene_group])
        postgres_session.commit()
        postgres_session.refresh(resource)
        postgres_session.refresh(gene_group)

        association = FamHasExtResource(
            external_resource_id=resource.id,
            gene_group_id=gene_group.id,
        )
        postgres_session.add(association)
        postgres_session.commit()

        result = repr(association)

        assert "FamHasExtResource" in result
        assert str(resource.id) in result
        assert str(gene_group.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestExternalResourceEdgeCases:
    """Test ExternalResource edge cases and special scenarios."""

    def test_create_multiple_resources(self, postgres_session):
        """Test creating multiple external resources."""
        ts = int(time.time() * 1000)
        resources = [
            ExternalResource(
                name=f"Resource {i} {ts}",
                url=f"https://test-{ts}.example.com/resource{i}/{ts}",
            )
            for i in range(5)
        ]
        postgres_session.add_all(resources)
        postgres_session.commit()

        # Verify all created
        stmt = select(ExternalResource).where(ExternalResource.name.like(f"%{ts}"))
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) >= 5

    def test_external_resource_with_special_characters_in_name(self, postgres_session):
        """Test resource with special characters in name."""
        ts = int(time.time() * 1000)
        name = f"CRC-Database (v2.0) [TEST-{ts}]"
        resource = ExternalResource(
            name=name,
            url=f"https://test-{ts}.example.com/special/{ts}",
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        assert resource.name == name

    def test_external_resource_long_description(self, postgres_session):
        """Test resource with maximum length description."""
        ts = int(time.time() * 1000)
        description = "A" * 255
        resource = ExternalResource(
            name=f"Long Desc {ts}",
            url=f"https://test-{ts}.example.com/long/{ts}",
            description=description,
        )
        postgres_session.add(resource)
        postgres_session.commit()
        postgres_session.refresh(resource)

        # Verify the created resource has the long description
        assert resource.description is not None
        assert len(resource.description) == 255
        assert resource.description == description
