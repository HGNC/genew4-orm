# Models

genew4-orm provides SQLModel classes for all database tables in the genew4 database.

## Core Models

### Gene

Represents a gene in the `hgnc` table.

```python
from genew4_orm.models import Gene

gene = Gene(
    approved_symbol="BRCA1",
    approved_name="Breast Cancer 1",
    status="Approved",
    locus_type="gene with protein product",
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (hgnc_id) |
| `approved_symbol` | `str` | HGNC approved gene symbol |
| `approved_name` | `str` | HGNC approved gene name |
| `status` | `GeneStatus` | Gene status (Approved, Pending, etc.) |
| `locus_type` | `GeneLocusType` | Locus type (37 options) |
| `chromosomal_location` | `str` | Chromosomal location |
| `date_modified` | `date` | Last modification date |
| `date_approved` | `date` | Approval date |
| `editor` | `str` | Last editor |

**Relationships:**
- `gene_has_gene_groups` - Many-to-many with GeneGroup

### GeneGroup

Represents a gene family/group in the `family_new` table.

```python
from genew4_orm.models import GeneGroup

group = GeneGroup(
    name="BRCA1 Family",
    abbreviation="BRCA1",
    status="exported",
    type="set",
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (fam_id) |
| `name` | `str` | Group name (unique) |
| `abbreviation` | `str` | Group abbreviation |
| `status` | `GeneGroupStatus` | Export status |
| `type` | `GeneGroupType` | Group type |
| `description` | `str` | Full description |

**Relationships:**
- `gene_group_has_genes` - One-to-many with GeneHasGeneGroup
- `aliases` - One-to-many with GeneGroupAlias

## Junction Models

### GeneHasGeneGroup

Junction table for Gene ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import GeneHasGeneGroup

association = GeneHasGeneGroup(
    gene_id=12345,
    gene_group_id=1,
    sort_order=1,
)
```

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `gene_id` | `int` | Foreign key to hgnc.hgnc_id |
| `gene_group_id` | `int` | Foreign key to family_new.id |
| `sort_order` | `int` | Display order |
| `comments` | `str` | Association comments |

### FamHasSpecialist

Junction table for Specialist ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasSpecialist

association = FamHasSpecialist(
    specialist_id=1,
    gene_group_id=1,
)
```

### FamHasExtResource

Junction table for ExternalResource ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasExtResource

association = FamHasExtResource(
    external_resource_id=1,
    gene_group_id=1,
)
```

### FamHasCorr

Junction table for Correspondence ↔ GeneGroup many-to-many relationship.

```python
from genew4_orm.models import FamHasCorr

association = FamHasCorr(
    correspondence_id=1,
    gene_group_id=1,
)
```

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

## Enum Types

### GeneStatus

Gene status values: `APPROVED`, `PENDING`, `RESERVED`, `RESERVED_NON_HUMAN`, `SUSPENDED`, `DELETE`, `ENTRY_WITHDRAWN`, `SYMBOL_WITHDRAWN`

### GeneLocusType

Locus type values: `GWPP` (gene with protein product), `PSEUDOGENE`, `UNDEF`, and 34 more options

### GeneGroupStatus

Group status values: `INTERNAL`, `EXPORTED`, `PUBLISHED`, `APPROVED`

### GeneGroupType

Group type values: `SET`, `SUBSET`, `OTHER`, `FAMILY`

## Full Model List

- `Gene` - Gene information
- `GeneGroup` - Gene family/group
- `GeneHasGeneGroup` - Gene-Group junction
- `FamHasSpecialist` - Specialist-Group junction
- `FamHasExtResource` - Resource-Group junction
- `FamHasCorr` - Correspondence-Group junction
- `Specialist` - Specialist organizations
- `ExternalResource` - External resources
- `Correspondence` - Correspondence records
- `User` - Application users
- `Editor` - Curator accounts
- `Reminder` - Reminder records
- `Grch38Mapping` - GRCh38 mapping data
- `Cytoband` - Cytoband data
- `HierarchyClosure` - Hierarchical relationship closure
- `GeneGroupAlias` - Group aliases
- `AuditLog` - Audit trail
