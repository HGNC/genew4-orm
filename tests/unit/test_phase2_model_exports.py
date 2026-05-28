"""Tests verifying Phase 2 model exports from genew4_orm.models."""

import pytest
from sqlmodel import SQLModel

EXPECTED_PHASE2_EXPORTS = [
    ("TableModDate", "table_mod_dates"),
    ("Ccds", "ccds"),
    ("CcdsSequence", "ccds_seq"),
    ("Gene2Refseq", "gene2refseq"),
    ("GeneInfo", "gene_info"),
    ("PseudogeneOrg", "pseudogene_org"),
    ("OtterSequence", "otter_seq"),
    ("EnsemblSequence", "ensembl_seq"),
    ("Hseq", "hseq"),
    ("HgncId2CcdsId", "hgnc_id2ccds_id"),
]


@pytest.mark.parametrize(("class_name", "tablename"), EXPECTED_PHASE2_EXPORTS)
def test_phase2_model_importable_from_package(class_name: str, tablename: str) -> None:
    import genew4_orm.models

    model_class = getattr(genew4_orm.models, class_name)
    assert issubclass(model_class, SQLModel)
    assert model_class.__tablename__ == tablename


def test_phase2_models_in_all() -> None:
    import genew4_orm.models

    for class_name, _ in EXPECTED_PHASE2_EXPORTS:
        assert class_name in genew4_orm.models.__all__, f"{class_name} missing from __all__"


def test_updated_gene_in_all() -> None:
    import genew4_orm.models

    assert "Gene" in genew4_orm.models.__all__
