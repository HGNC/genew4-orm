"""Integration tests for Editor model with PostgreSQL.

This module tests Editor CRUD operations with real database connections.
"""

import time

import pytest
from sqlalchemy import select

from genew4_orm.models.editor import Editor


@pytest.mark.usefixtures("postgres_session")
class TestEditorCRUD:
    """Test Editor CRUD operations with PostgreSQL."""

    def test_create_editor_minimal(self, postgres_session):
        """Test creating editor record with minimal required fields."""
        ts = int(time.time() * 1000)
        editor = Editor(
            editor=f"editor_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.id is not None
        assert editor.editor == f"editor_{ts}"
        assert editor.current is True  # Default value

    def test_create_editor_with_all_fields(self, postgres_session):
        """Test creating editor record with all fields."""
        ts = int(time.time() * 1000)
        editor = Editor(
            full_name=f"Test Editor {ts}",
            editor=f"complete_editor_{ts}",
            password=f"hashed_password_{ts}",
            preferences="theme=dark;language=en",
            current=True,
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.full_name == f"Test Editor {ts}"
        assert editor.editor == f"complete_editor_{ts}"
        assert editor.password == f"hashed_password_{ts}"
        assert editor.preferences == "theme=dark;language=en"
        assert editor.current is True

    def test_read_editor_by_id(self, postgres_session):
        """Test reading editor by ID."""
        ts = int(time.time() * 1000)
        editor = Editor(
            full_name=f"Read Test {ts}",
            editor=f"read_editor_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()
        editor_id = editor.id

        # Read by ID
        retrieved_editor = postgres_session.get(Editor, editor_id)

        assert retrieved_editor is not None
        assert retrieved_editor.full_name == f"Read Test {ts}"
        assert retrieved_editor.editor == f"read_editor_{ts}"

    def test_update_editor_fields(self, postgres_session):
        """Test updating editor fields."""
        ts = int(time.time() * 1000)
        editor = Editor(
            full_name=f"Original Name {ts}",
            editor=f"update_editor_{ts}",
            current=True,
        )
        postgres_session.add(editor)
        postgres_session.commit()

        # Update fields
        editor.full_name = f"Updated Name {ts}"
        editor.preferences = "theme=light"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(editor)
        assert editor.full_name == f"Updated Name {ts}"
        assert editor.preferences == "theme=light"

    def test_delete_editor(self, postgres_session):
        """Test deleting editor."""
        ts = int(time.time() * 1000)
        editor = Editor(
            editor=f"delete_editor_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()
        editor_id = editor.id

        # Delete editor
        postgres_session.delete(editor)
        postgres_session.commit()

        # Verify deletion
        deleted_editor = postgres_session.get(Editor, editor_id)
        assert deleted_editor is None

    def test_query_editor_by_login(self, postgres_session):
        """Test querying editor by login name."""
        ts = int(time.time() * 1000)
        editor = Editor(
            full_name=f"Query Test {ts}",
            editor=f"query_editor_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()

        # Query by editor login
        stmt = select(Editor).where(Editor.editor == f"query_editor_{ts}")
        result = postgres_session.execute(stmt).scalar_one_or_none()

        assert result is not None
        assert result.full_name == f"Query Test {ts}"


@pytest.mark.usefixtures("postgres_session")
class TestEditorActiveStatus:
    """Test Editor active/current status field."""

    def test_editor_default_active(self, postgres_session):
        """Test that editor defaults to active=True."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"default_active_{ts}")
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.current is True

    def test_editor_set_inactive(self, postgres_session):
        """Test setting editor to inactive."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"inactive_{ts}", current=False)
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.current is False

    def test_query_active_editors(self, postgres_session):
        """Test querying only active editors."""
        ts = int(time.time() * 1000)
        active_editor = Editor(editor=f"active_{ts}", current=True)
        inactive_editor = Editor(editor=f"inactive_{ts}", current=False)
        postgres_session.add_all([active_editor, inactive_editor])
        postgres_session.commit()

        # Query only active editors
        stmt = select(Editor).where(Editor.current)
        results = postgres_session.execute(stmt).scalars().all()

        # Should include active_editor
        assert any(r.editor == f"active_{ts}" for r in results)

    def test_deactivate_editor(self, postgres_session):
        """Test deactivating an editor."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"deactivate_{ts}", current=True)
        postgres_session.add(editor)
        postgres_session.commit()

        # Deactivate
        editor.current = False
        postgres_session.commit()

        # Verify
        postgres_session.refresh(editor)
        assert editor.current is False


@pytest.mark.usefixtures("postgres_session")
class TestEditorPreferences:
    """Test Editor preferences field."""

    def test_editor_with_preferences(self, postgres_session):
        """Test creating editor with preferences."""
        ts = int(time.time() * 1000)
        prefs = "theme=dark;language=en;timezone=UTC"
        editor = Editor(
            editor=f"prefs_{ts}",
            preferences=prefs,
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.preferences == prefs

    def test_editor_without_preferences(self, postgres_session):
        """Test creating editor without preferences (null)."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"no_prefs_{ts}")
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.preferences is None

    def test_update_editor_preferences(self, postgres_session):
        """Test updating editor preferences."""
        ts = int(time.time() * 1000)
        editor = Editor(
            editor=f"update_prefs_{ts}",
            preferences="theme=light",
        )
        postgres_session.add(editor)
        postgres_session.commit()

        # Update preferences
        editor.preferences = "theme=dark;sidebar=collapsed"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(editor)
        assert editor.preferences == "theme=dark;sidebar=collapsed"


@pytest.mark.usefixtures("postgres_session")
class TestEditorPassword:
    """Test Editor password field."""

    def test_editor_with_password(self, postgres_session):
        """Test creating editor with password (hashed)."""
        ts = int(time.time() * 1000)
        hashed_pw = f"bcrypt_hash_{ts}"
        editor = Editor(
            editor=f"with_pw_{ts}",
            password=hashed_pw,
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.password == hashed_pw

    def test_editor_without_password(self, postgres_session):
        """Test creating editor without password (null)."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"no_pw_{ts}")
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.password is None

    def test_update_editor_password(self, postgres_session):
        """Test updating editor password."""
        ts = int(time.time() * 1000)
        editor = Editor(
            editor=f"update_pw_{ts}",
            password=f"old_hash_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()

        # Update password
        editor.password = f"new_hash_{ts}"
        postgres_session.commit()

        # Verify update
        postgres_session.refresh(editor)
        assert editor.password == f"new_hash_{ts}"


@pytest.mark.usefixtures("postgres_session")
class TestEditorFullName:
    """Test Editor full_name field."""

    def test_editor_with_full_name(self, postgres_session):
        """Test creating editor with full name."""
        ts = int(time.time() * 1000)
        full_name = f"Dr. Jane Editor Smith {ts}"
        editor = Editor(
            editor=f"dr_smith_{ts}",
            full_name=full_name,
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.full_name == full_name

    def test_editor_without_full_name(self, postgres_session):
        """Test creating editor without full name (null)."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"no_name_{ts}")
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.full_name is None

    def test_query_editor_by_full_name_pattern(self, postgres_session):
        """Test querying editors by full name pattern."""
        ts = int(time.time() * 1000)
        editor1 = Editor(
            editor=f"name1_{ts}",
            full_name=f"John Doe {ts}",
        )
        editor2 = Editor(
            editor=f"name2_{ts}",
            full_name=f"Jane Smith {ts}",
        )
        postgres_session.add_all([editor1, editor2])
        postgres_session.commit()

        # Query by full name pattern
        stmt = select(Editor).where(Editor.full_name.like(f"%{ts}"))
        results = postgres_session.execute(stmt).scalars().all()

        assert len(results) >= 2


@pytest.mark.usefixtures("postgres_session")
class TestEditorRepr:
    """Test Editor __repr__ method."""

    def test_editor_repr(self, postgres_session):
        """Test Editor string representation."""
        ts = int(time.time() * 1000)
        editor = Editor(
            editor=f"repr_{ts}",
        )
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        result = repr(editor)

        assert "Editor" in result
        assert f"repr_{ts}" in result
        assert str(editor.id) in result


@pytest.mark.usefixtures("postgres_session")
class TestEditorEdgeCases:
    """Test Editor edge cases and special scenarios."""

    def test_create_multiple_editors(self, postgres_session):
        """Test creating multiple editors."""
        ts = int(time.time() * 1000)
        editors = [Editor(editor=f"editor_{i}_{ts}", current=True) for i in range(5)]
        postgres_session.add_all(editors)
        postgres_session.commit()

        # Verify all created
        stmt = select(Editor).where(Editor.editor.like(f"%_{ts}"))
        results = postgres_session.execute(stmt).scalars().all()
        assert len(results) >= 5

    def test_editor_with_special_characters_in_login(self, postgres_session):
        """Test editor with special characters in login name."""
        ts = int(time.time() * 1000)
        editor = Editor(editor=f"test.editor-{ts}@example")
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.editor == f"test.editor-{ts}@example"

    def test_editor_long_preferences_string(self, postgres_session):
        """Test editor with very long preferences string."""
        ts = int(time.time() * 1000)
        long_prefs = ";".join([f"key{i}=value{i}" for i in range(100)])
        editor = Editor(editor=f"long_prefs_{ts}", preferences=long_prefs)
        postgres_session.add(editor)
        postgres_session.commit()
        postgres_session.refresh(editor)

        assert editor.preferences == long_prefs
