"""Database models for genew4-orm.

This module contains all SQLAlchemy model classes (subclassing
``db_common.DeclarativeBase``) representing database tables.
"""

from genew4_orm.models.audit_log import AuditLog
from genew4_orm.models.ccds import Ccds
from genew4_orm.models.ccds_sequence import CcdsSequence
from genew4_orm.models.comment import Comment
from genew4_orm.models.correspondence import Correspondence
from genew4_orm.models.editor import Editor
from genew4_orm.models.ensembl_sequence import EnsemblSequence
from genew4_orm.models.external_resource import ExternalResource
from genew4_orm.models.fam_has_corr import FamHasCorr
from genew4_orm.models.fam_has_ext_resource import FamHasExtResource
from genew4_orm.models.fam_has_specialist import FamHasSpecialist
from genew4_orm.models.gene import Gene
from genew4_orm.models.gene2refseq import Gene2Refseq
from genew4_orm.models.gene_group import GeneGroup
from genew4_orm.models.gene_group_alias import GeneGroupAlias
from genew4_orm.models.gene_has_comment import GeneHasComment
from genew4_orm.models.gene_has_gene_group import GeneHasGeneGroup
from genew4_orm.models.gene_info import GeneInfo
from genew4_orm.models.grch38_mapping import Grch38Mapping
from genew4_orm.models.hgnc_id2ccds_id import HgncId2CcdsId
from genew4_orm.models.hierarchy_closure import HierarchyClosure
from genew4_orm.models.hseq import Hseq
from genew4_orm.models.otter_sequence import OtterSequence
from genew4_orm.models.pseudogene_org import PseudogeneOrg
from genew4_orm.models.reminder import Reminder
from genew4_orm.models.specialist import Specialist
from genew4_orm.models.table_mod_date import TableModDate
from genew4_orm.models.user import User

# Cytoband excluded - use raw SQL for this table (no PK)
# from genew4_orm.models.cytoband import Cytoband

__all__ = [
    "AuditLog",
    "Ccds",
    "CcdsSequence",
    "Comment",
    "Correspondence",
    "Editor",
    "EnsemblSequence",
    "ExternalResource",
    "FamHasCorr",
    "FamHasExtResource",
    "FamHasSpecialist",
    "Gene",
    "Gene2Refseq",
    "GeneGroup",
    "GeneGroupAlias",
    "GeneHasComment",
    "GeneHasGeneGroup",
    "GeneInfo",
    "Grch38Mapping",
    "HgncId2CcdsId",
    "HierarchyClosure",
    "Hseq",
    "OtterSequence",
    "PseudogeneOrg",
    "Reminder",
    "Specialist",
    "TableModDate",
    "User",
]
