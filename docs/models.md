# Models

genew4-orm provides SQLAlchemy 2.0 declarative models for the database tables in
the genew4 database. All models subclass `db_common.DeclarativeBase` (a plain
`sqlalchemy.orm.DeclarativeBase`), so they share a single `MetaData`/registry.

## Core Models

### Gene

Represents a gene in the `hgnc` table.

```python
from genew4_orm.models import Gene

gene = Gene(
    hgnc_id=12345,
    approved_symbol="BRCA1",
    approved_name="Breast Cancer 1",
    status="Approved",
    locus_type="gene with protein product",
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `hgnc_id` | `int` | Primary key (HGNC ID) |
| `approved_symbol` | `str \| None` | HGNC approved gene symbol |
| `approved_name` | `str \| None` | HGNC approved gene name |
| `status` | `str \| None` | Gene status — a `GeneStatus` value (default `"Pending"`) |
| `locus_type` | `str \| None` | Locus type — a `GeneLocusType` value (default `"undef"`) |
| `previous_symbols` | `str \| None` | Previous gene symbols |
| `alias_symbols` | `str \| None` | Alias gene symbols |
| `chromosomal_location` | `str \| None` | Chromosomal location |
| `editor` | `str \| None` | Last editor |
| `date_modified` | `date \| None` | Last modification date |
| `date_approved` / `date_symbol_changed` / `date_name_changed` | `date \| None` | Lifecycle dates |

> `status` and `locus_type` are stored as plain string columns but hold values
> from the [`GeneStatus`](#genestatus) and [`GeneLocusType`](#genelocustype)
> enums respectively.

**Relationships:**
- `gene_has_gene_groups` - Many-to-many with GeneGroup
- `gene_has_comments` - One-to-many with GeneHasComment

The model also exposes Phase 2 cross-reference/sequence columns (`ccds_ids`,
`hseq_ids`, `public_hseq_id`, `pseudogene_id`, `vega_ids`, etc.).

### GeneGroup

Represents a gene family/group in the `family_new` table.

```python
from genew4_orm.models import GeneGroup

group = GeneGroup(
    id=1,
    name="BRCA1 Family",
    abbreviation="BRCA1",
    description="BRCA-related gene family",
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (`fam_id`) |
| `name` | `str` | Group name (required) |
| `abbreviation` | `str \| None` | Group abbreviation |
| `editor` | `str \| None` | Editor responsible |
| `pubmed_ids` | `str \| None` | PubMed IDs |
| `internal_comments` | `str \| None` | Internal curator comments (`curator_comment` column) |
| `public_comments` | `str \| None` | Public-facing comments (`external_note` column) |
| `label` | `str \| None` | Description label (`desc_label`) |
| `source` | `str \| None` | Description source (`desc_source`) |
| `typical_gene` | `str \| None` | Typical gene for this group |
| `description` | `str \| None` | Full description (`desc_comment`) |

> Note: the legacy `status` and `type` enum columns are **not** mapped on this
> model (they were removed because the database does not use enum types here).
> The `GeneGroupStatus` / `GeneGroupType` enums still exist but are not bound
> to columns.

**Relationships:**
- `gene_group_has_genes` - One-to-many with GeneHasGeneGroup
- `aliases` - One-to-many with GeneGroupAlias
- `parent_hierarchy_closures` / `child_hierarchy_closures` - One-to-many with HierarchyClosure

Specialists, external resources, and correspondences are associated via junction
tables (`FamHasSpecialist`, `FamHasExtResource`, `FamHasCorr`) rather than direct
relationships — query them with explicit joins.

## Junction Models

### GeneHasGeneGroup

Junction table for the Gene ↔ GeneGroup many-to-many relationship
(`gene_has_family` table). The two foreign keys form a composite primary key.

```python
from genew4_orm.models import GeneHasGeneGroup

association = GeneHasGeneGroup(
    gene_id=12345,
    gene_group_id=1,
    custom_sort="A",
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `gene_id` | `int` | Foreign key to `hgnc.hgnc_id` (composite PK, `hgnc_id` column) |
| `gene_group_id` | `int` | Foreign key to `family_new.id` (composite PK, `family_id` column) |
| `url` | `str \| None` | URL for this gene-group association |
| `custom_sort` | `str \| None` | Custom sort value for the gene within the group |

**Relationships:**
- `gene` - Belongs to Gene
- `gene_group` - Belongs to GeneGroup

### FamHasSpecialist

Junction table for the Specialist ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasSpecialist

association = FamHasSpecialist(
    specialist_id=1,
    gene_group_id=1,
)
```

### FamHasExtResource

Junction table for the ExternalResource ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasExtResource

association = FamHasExtResource(
    external_resource_id=1,
    gene_group_id=1,
)
```

### FamHasCorr

Junction table for the Correspondence ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasCorr

association = FamHasCorr(
    correspondence_id=1,
    gene_group_id=1,
)
```

### GeneHasComment

Junction table for the Gene ↔ Comment many-to-many relationship. The two
foreign keys form a composite primary key.

```python
from genew4_orm.models import GeneHasComment

association = GeneHasComment(
    comment_id=1,
    hgnc_id=12345,
    editor_id=1,
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `comment_id` | `int` | Foreign key to `comment.id` (composite PK) |
| `hgnc_id` | `int` | Foreign key to `hgnc.hgnc_id` (composite PK) |
| `date_added` | `date` | Date the comment was linked to the gene (defaults to today) |
| `editor_id` | `int` | Foreign key to `editor.ed_id` |

**Relationships:**
- `comment` - Belongs to Comment
- `gene` - Belongs to Gene
- `editor` - Belongs to Editor

## Related Models

### Specialist

External specialist organizations that collaborate with HGNC.

```python
from genew4_orm.models import Specialist

specialist = Specialist(
    name="Test Specialist",
    address="123 Test Street",
    url="https://example.com",
)
```

### ExternalResource

External databases and resources linked to gene groups.

```python
from genew4_orm.models import ExternalResource

resource = ExternalResource(
    name="UniProt",
    url="https://uniprot.org",
    description="Universal Protein Resource",
)
```

### Correspondence

Records of correspondence with researchers and organizations.

```python
from genew4_orm.models import Correspondence

corr = Correspondence(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
)
```

### User

User accounts for the application.

```python
from genew4_orm.models import User

user = User(
    display_name="jdoe",
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
)
```

### AuditLog

Automatic audit trail for all write operations.

```python
from genew4_orm.models import AuditLog

audit = AuditLog(
    user="username",
    operation="CREATE",
    entity_type="Gene",
    entity_id=12345,
    field_changes={
        "approved_name": {"old": None, "new": "New Name"}
    },
)
```

### Comment

Comments linked to genes with a publication workflow.

```python
from genew4_orm.enums import PublishStatus
from genew4_orm.models import Comment

comment = Comment(
    comment="This gene requires further review",
    author_id=1,
    status=PublishStatus.PENDING,
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (auto-increment via `comment_sequence`) |
| `comment` | `str` | Comment text content |
| `author_id` | `int` | Foreign key to editor (author) |
| `lock` | `str \| None` | Editing lock |
| `created` | `date \| None` | Date comment was created |
| `publisher_id` | `int \| None` | Foreign key to editor (publisher) |
| `status` | `PublishStatus` | pending, published, or rejected (defaults to `PENDING`) |
| `status_date` | `date \| None` | Date of last status change |
| `replace_id` | `int \| None` | Foreign key to comment (comment this replaces) |
| `replacement_id` | `int \| None` | Foreign key to comment (replacement comment) |

**Relationships:**
- `author` - Belongs to Editor (via `author_id`)
- `publisher` - Belongs to Editor (via `publisher_id`)
- `gene_has_comments` - One-to-many with GeneHasComment

## Enum Types

All enums are string-based (`StrEnum`) for PostgreSQL compatibility and are
defined in `genew4_orm.enums`.

### GeneStatus

Gene approval/status values: `APPROVED` (`"Approved"`), `PENDING` (`"Pending"`),
`RESERVED`, `RESERVED_NON_HUMAN`, `SUSPENDED`, `DELETE`, `ENTRY_WITHDRAWN`,
`SYMBOL_WITHDRAWN` (8 values).

### GeneLocusType

Locus type values (34 values), including `GWPP` (`"gene with protein product"`),
`PSEUDOGENE`, `RNA_LONG_NON_CODING`, `REGION`, `UNDEF` (`"undef"`), and others.

### GeneGroupStatus

Gene group visibility status: `DELETE` (`"delete"`), `EXPORTED` (`"exported"`),
`INTERNAL` (`"internal"`) (3 values).

### GeneGroupType

Gene group type: `SET` (`"set"`) (1 value).

### PublishStatus

Comment publication status: `PENDING` (`"pending"`), `PUBLISHED` (`"published"`),
`REJECTED` (`"rejected"`) (3 values).

### Other enums

- `Grch38SourceType` - GRCh38 mapping source: `NCBI`, `ENSEMBL`, `CHROM`, `HGNC`
- `Grch38MarkType` - GRCh38 marking type: `MAX`, `HIDDEN`
- `CytobandSourceType` - Cytoband source: `UCSC`, `ENSEMBL`

The `enum_field()` helper builds a plain-SQLAlchemy `mapped_column` backed by an
`Enum(...)` column type for use on `DeclarativeBase` subclasses (used by
`Comment.status`).

## Full Model List

- `Gene` - Gene information (`hgnc`)
- `GeneGroup` - Gene family/group (`family_new`)
- `GeneHasGeneGroup` - Gene-Group junction (`gene_has_family`)
- `GeneHasComment` - Gene-Comment junction (`gene_has_comment`)
- `FamHasSpecialist` - Specialist-Group junction
- `FamHasExtResource` - Resource-Group junction
- `FamHasCorr` - Correspondence-Group junction
- `Specialist` - Specialist organizations
- `ExternalResource` - External resources
- `Correspondence` - Correspondence records
- `Comment` - Gene comments with publication workflow
- `User` - Application users
- `Editor` - Curator accounts
- `Reminder` - Reminder records
- `GeneGroupAlias` - Group aliases
- `HierarchyClosure` - Hierarchical relationship closure
- `Grch38Mapping` - GRCh38 mapping data
- `AuditLog` - Audit trail

Phase 2 cross-reference and sequence models: `Ccds`, `CcdsSequence`,
`Gene2Refseq`, `GeneInfo`, `PseudogeneOrg`, `OtterSequence`, `EnsemblSequence`,
`Hseq`, `HgncId2CcdsId`, `TableModDate`.

> Note: the `cytoband` table has no primary key and is intentionally **not**
> mapped as a model — query it with raw SQL via `session.execute(text(...))`.
