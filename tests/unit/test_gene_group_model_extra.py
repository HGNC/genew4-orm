"""Additional unit tests for GeneGroup model to improve coverage."""

from genew4_orm.models import GeneGroup


class TestGeneGroupDescriptionFields:
    """Test cases for GeneGroup description fields."""

    def test_gene_group_label_field(self) -> None:
        """Test GeneGroup label field."""
        gene_group = GeneGroup(
            name="Test Group",
            label="Test Label",
        )

        assert gene_group.label == "Test Label"

    def test_gene_group_source_field(self) -> None:
        """Test GeneGroup source field."""
        gene_group = GeneGroup(
            name="Test Group",
            source="UCSC",
        )

        assert gene_group.source == "UCSC"

    def test_gene_group_typical_gene_field(self) -> None:
        """Test GeneGroup typical_gene field."""
        gene_group = GeneGroup(
            name="Test Group",
            typical_gene="BRCA1",
        )

        assert gene_group.typical_gene == "BRCA1"

    def test_gene_group_description_field(self) -> None:
        """Test GeneGroup description field."""
        gene_group = GeneGroup(
            name="Test Group",
            description="This is a test gene group description",
        )

        assert gene_group.description == "This is a test gene group description"


class TestGeneGroupAllDescriptionFieldsTogether:
    """Test GeneGroup with all description fields at once."""

    def test_gene_group_with_all_description_fields(self) -> None:
        """Test GeneGroup can have all description fields."""
        gene_group = GeneGroup(
            name="Full Test Group",
            label="Full Label",
            source="Full Source",
            typical_gene="GENE1",
            description="Full description",
        )

        assert gene_group.label == "Full Label"
        assert gene_group.source == "Full Source"
        assert gene_group.typical_gene == "GENE1"
        assert gene_group.description == "Full description"


class TestGeneGroupEdgeCases:
    """Test edge cases for GeneGroup."""

    def test_gene_group_name_field_max_length(self) -> None:
        """Test GeneGroup name field at max length."""
        # Max length is 150 per the model
        max_name = "x" * 150

        gene_group = GeneGroup(name=max_name)

        assert gene_group.name == max_name

    def test_gene_group_abbreviation_field(self) -> None:
        """Test GeneGroup abbreviation field."""
        gene_group = GeneGroup(
            name="Test Group",
            abbreviation="TGG",
        )

        assert gene_group.abbreviation == "TGG"

    def test_gene_group_repr_with_description_fields(self) -> None:
        """Test GeneGroup __repr__ with description fields."""
        gene_group = GeneGroup(id=123, name="Test Group")

        repr_str = repr(gene_group)

        assert "GeneGroup" in repr_str
        assert "name='Test Group'" in repr_str
