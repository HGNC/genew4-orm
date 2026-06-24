# CHANGELOG


## v0.5.2 (2026-06-24)

### Bug Fixes

- **models**: Persist enum values, not member names, in enum_field
  ([`4e15e09`](https://github.com/HGNC/genew4-orm/commit/4e15e0914600d803a52998a34d487264ea27c462))

enum_field built SQLEnum(native_enum=False), which by default persists the enum member NAME
  ('INTERNAL', 'PENDING') rather than its value ('internal', 'pending'). This contradicted
  docs/models.md and the real family_new / comment columns — which are lowercase and owned by the
  TypeScript ORM — and would raise CheckViolation against production's lowercase CHECK constraints
  if ever exercised there.

Add values_callable so both the stored bytes and the generated CHECK constraint use the StrEnum
  values. Affects GeneGroup.status, GeneGroup.type, and Comment.status.

Align the 14 raw-SQL test inserts against family_new (which bypass the ORM and so must supply the
  now-required status) to 'internal'. Add a unit test asserting col.type.enums equals the enum
  values, and two PostgreSQL integration tests that read the raw status/type columns and assert the
  persisted case.


## v0.5.1 (2026-06-24)

### Bug Fixes

- **models**: Bind GeneGroup.status/type enum columns via enum_field (Task ...)
  ([`0aa41b0`](https://github.com/HGNC/genew4-orm/commit/0aa41b0cb63c6e3cd7b91ebb9cc867f7affbdd1b))

### Chores

- **deps**: Bump db-common pin to v0.2.0 and fix surfaced redundant casts (Task T6)
  ([`5caaf68`](https://github.com/HGNC/genew4-orm/commit/5caaf68b6b8a76848668510afbb4b935b59b4257))

### Code Style

- **format**: Apply ruff format to align with CI formatters gate
  ([`34f9d68`](https://github.com/HGNC/genew4-orm/commit/34f9d688309a6fe94c0546611a76abc88ce79074))


## v0.5.0 (2026-06-19)

### Bug Fixes

- **audit-log**: Make field_changes a real dict via JSONEncodedDict TypeDecorator
  ([`726059a`](https://github.com/HGNC/genew4-orm/commit/726059ac694fd536ba024dbef8d2257937b2a464))

AuditLog.field_changes was declared Mapped[dict] but stored as a plain Text column: a dict could not
  be persisted (SQLite rejected it), and a DB-loaded row came back as a JSON string, so
  get_field_diff()/get_changed_fields() raised AttributeError. Existing accessor tests only used
  in-memory objects, so it went undetected.

Add a JSONEncodedDict TypeDecorator (impl=Text, so DDL is unchanged -> no migration) that serializes
  dict->JSON on write and deserializes on read; delegate to the previously-dead
  _serialize/_deserialize helpers. Drop the now-redundant json.dumps in audit.py (3 sites) so the
  TypeDecorator is the single serialization owner. Update callers/tests that json.loads'd the string
  (1 readonly + 5 pg-integration + 2 e2e + 1 gene_lifecycle + 1 smoke where audit_payload is now a
  dict). Add round-trip unit tests that RED-failed before (dict not bindable) and pass now.

Verified: ruff/black/mypy clean; 368 passed (+4), no new failures vs baseline; e2e/PG-gated files
  collect cleanly (unrunnable without PG).

- **readonly-session**: Query audit log by reliable fields, not entity_id (Task T2)
  ([`9b39101`](https://github.com/HGNC/genew4-orm/commit/9b39101f5dbc6a945b9673b09e259dcf674e8383))

The audit before_flush listener writes entity_id=0 for INSERTs because the autoincrement PK isn't
  assigned until the INSERT runs (after before_flush) — documented in audit.py and pinned by
  tests/unit/test_audit.py. So test_readwrite_session_creates_audit_logs's match loop
  (entry.entity_id == gene.hgnc_id) never matched and always fell through to the skip removed in
  d968e93. Query instead by the fields the audit module documents as reliable for a CREATE
  (entity_type + operation + user); this test creates exactly one gene so that uniquely identifies
  the entry.

Proven via a SQLite probe (listener is global): old query WOULD FAIL, new query finds the entry.
  Corrected the spec's "Why" to name both root causes of the original skip (registration [T1] +
  entity_id=0 [T2 query]). No change to conftest.py or audit.py; no new regressions vs baseline.

### Build System

- **deps**: Wire db-common as a git dependency pinned to v0.1.0 (Task T1)
  ([`a9eb856`](https://github.com/HGNC/genew4-orm/commit/a9eb856f1e1b587df0cd6adcbfb1ce6e69b72f20))

Add db-common>=0.1.0 to dependencies and a [tool.uv.sources] git source pinned to the immutable tag
  v0.1.0 on HGNC/db-common, mirroring ensembl-orm. Resolves from the git source at commit 67b6cae.

Adds a regression guard (tests/unit/test_db_common_dependency.py) that is the executable form of the
  T1 verify line: the module-level imports prove db-common resolves and its public symbols import;
  the test pins those symbols to db_common.__all__ so a silent privatization fails here.

### Chores

- Ignore .pi/ directory
  ([`6be6fa7`](https://github.com/HGNC/genew4-orm/commit/6be6fa777a4116b00b8efcfcc4fefcfcf9f0b60c))

CLAUDE.md was the final line with no trailing newline, so appending .pi/ concatenated both into a
  single non-matching pattern (CLAUDE.md.pi/). Split into two lines so each is ignored.

### Documentation

- Sync markdown + docstrings to SQLAlchemy/db-common migration
  ([`2054e3f`](https://github.com/HGNC/genew4-orm/commit/2054e3f2b1b5fe0b517b209af99c6a3d4084edf7))

Update README and all docs/* pages to the post-migration API: SQLAlchemy 2.0 select()/scalars()
  patterns, correct config fields (Genew4DatabaseSettings, DATABASESETTINGS_PG_* env vars, plain-str
  password), fixed model fields and enum values, and the real query-helper names.

Fix broken .options() examples in query_helpers.py docstrings — the list-returning helpers must be
  splatted. Modernize legacy session.query() comments in models to select().

- **audit**: Document field_changes as a dict, not a JSON string
  ([`82ff676`](https://github.com/HGNC/genew4-orm/commit/82ff676a6d2875bcce449fa930e622934edcdb4e))

Since 726059a (JSONEncodedDict TypeDecorator), AuditLog.field_changes is a real dict on load/write.
  Update audit-logging.md and testing.md so the contract, the constructor/query examples, and the
  fields table stop showing json.loads/json.dumps and pass/read dicts directly. mkdocs build
  --strict passes.

ci: fix schema-init (sqlmodel removed) and docs.yml (db-common git dep)

test.yml/ci.yml: the "Initialize database schema" step imported sqlmodel and called
  SQLModel.metadata.create_all, but sqlmodel was dropped in the db-common migration ->
  ModuleNotFoundError before any PG test ran. Use db_common.DeclarativeBase.metadata.create_all (the
  pattern in conftest.py). DDL unchanged (audit_log.field_changes stays TEXT -> no migration).

docs.yml: pip install -e . cannot resolve db-common (git-only via [tool.uv.sources]; not on PyPI,
  verified 404). Add a `docs` dependency-group (mkdocs-material, mkdocstrings[python]) and switch to
  uv sync --group docs + uv run mkdocs build, so the git pin resolves. mkdocs build --strict passes.

- **query-helpers**: Convert session.exec → session.scalars in docstrings (Task T5)
  ([`640b96c`](https://github.com/HGNC/genew4-orm/commit/640b96c1c4ed7294645fa38610b2a9155e660f5f))

Finish the SQLModel→SQLAlchemy docstring conversion in query_helpers.py: the import lines were
  already flipped to `from sqlalchemy import select` in T5, but the 6 example calls still used
  SQLModel's session.exec(...). Switch them to session.scalars(...) (the SQLAlchemy 2.0 equivalent
  that the module's own runtime already uses) so the examples are internally consistent with the
  now-SQLAlchemy-only runtime.

### Features

- **audit**: Auto-register before_flush listener on package import (Task T1)
  ([`99ef3f0`](https://github.com/HGNC/genew4-orm/commit/99ef3f073188387eaf85c0d0d72626facf55e488))

### Refactoring

- **config**: Replace DatabaseSettings with Genew4DatabaseSettings(db_common.DatabaseSettings) (Task
  T3)
  ([`931426f`](https://github.com/HGNC/genew4-orm/commit/931426f1a3b96beac02423d4f83b633e380cab62))

Subclass db_common.DatabaseSettings, inheriting its URL builder (get_url) and pool fields while
  keeping the DATABASESETTINGS_ prefix, PostgreSQL defaults, and legacy DATABASESETTINGS_PG_*
  env-var names via AliasChoices. Expose pg_host/pg_port/pg_name/pg_user/pg_password as read/write
  property aliases (also accepted as constructor kwargs via a before model validator). Preserve
  get_connection_url and get_engine_kwargs as compat shims delegating to db-common; add a
  genew4-only pool_timeout field. Drop SecretStr (password is now plain str), drop
  get_async_engine_kwargs (db-common is sync-only), and mask password in repr via Field(repr=False).

- **migration**: Drop sqlmodel and finish db-common migration (Task T5)
  ([`7d50290`](https://github.com/HGNC/genew4-orm/commit/7d50290cc31ee724796a718cd6109e9a90b7709d))

Switch alembic + conftest metadata to db_common.DeclarativeBase.metadata, remove the sqlmodel
  dependency (deps/keywords/isort/mypy-override), and clear the db-common-under-strict mypy
  regression (disallow_subclassing_any= false + db_common import override, 27 dead type: ignore
  removed, and the [no-any-return]/[type-arg] introduced by T3/T4 delegating to untyped db-common).
  Add an end-to-end SQLite smoke test through the migrated session path asserting alembic targets
  DeclarativeBase.metadata. Clean up the remaining sqlmodel docstring references. mypy src/ and the
  sqlmodel grep gate are both green; unit suite + smoke test pass.

- **models**: Convert 28 models + enum_field to SQLAlchemy on db_common.DeclarativeBase (Task T2)
  ([`e5cf257`](https://github.com/HGNC/genew4-orm/commit/e5cf2575aadc1865aeeeb31ee5388468188d7d9b))

Rewrite all 28 SQLModel-based models as plain SQLAlchemy 2.0 classes on db_common.DeclarativeBase
  (Mapped/mapped_column/relationship), and rewrite enum_field to return a mapped_column(SAEnum(...))
  spec. Five models whose instantiation defaults are pinned by unchanged tests (User, Reminder,
  AuditLog, Comment, GeneHasComment) gain a hand-written __init__ restoring SQLModel-parity
  construction defaults; User also tolerates unknown kwargs to match SQLModel.

Mapper verified byte-for-byte identical to the prior SQLModel baseline (tablename, columns, types,
  nullable, PK, unique, FKs, relationships, cascades). All 332 unit tests green; ruff clean.

Note: mypy src/ regresses 0->83 (db_common lacks py.typed under strict=true); this is the
  documented, T5-deferred gap recorded in the spec Decisions.

- **session**: Migrate session infra + exceptions to db-common delegation (Task T4)
  ([`04ef142`](https://github.com/HGNC/genew4-orm/commit/04ef1424aa1d7c63de58165a304d8efd544ca34b))

### Testing

- **audit**: Surface which registration condition failed in listener test
  ([`133dc8b`](https://github.com/HGNC/genew4-orm/commit/133dc8b5870d21a812a9c8e5a99151eaa0e35a76))

- **audit-log**: Reuse sqlite_session fixture and tighten field_changes type
  ([`5e23f8f`](https://github.com/HGNC/genew4-orm/commit/5e23f8fde58cdafea994cf51903ddd3e764bd1c5))

Refactor TestAuditLogFieldChangesRoundTrip to use the project's function-scoped sqlite_session
  fixture instead of building its own engine/schema/session per test, and annotate
  _commit_and_reload's field_changes param as dict[str, Any] (matching AuditLog's Mapped[dict] and
  the sibling _serialize/_deserialize helpers) rather than bare dict.

Annotation-only on the runtime path; 21 model-unit tests still pass, no regressions vs baseline (368
  passed).

- **readonly-session**: Assert audit logs directly instead of skipping (Task T2)
  ([`d968e93`](https://github.com/HGNC/genew4-orm/commit/d968e9393d6a722f8b4a3dc99a62a8a16dee9898))

Now that T1 (99ef3f0) auto-registers the before_flush listener on package import, drop the defensive
  pytest.skip("Audit event listener not properly attached...") escape hatch from
  test_readwrite_session_creates_audit_logs and assert audit_entry is not None + audit_entry.user ==
  "audit_test_user" directly.

Also fix tests/conftest.py::postgres_engine to call _try_postgres_connection() before constructing
  DatabaseSettings(): previously DatabaseSettings() ran unconditionally and raised a pydantic
  ValidationError on missing PG creds, so every postgres_session integration test errored instead of
  skipping. Pre-existing (45fae83, regresses 4a57405); required so T2's "module-level skipped when
  PG unavailable" Verify holds. No change to the PG-available path.

- **readonly-session**: Assert field_changes ties audit entry to the gene (Task T2)
  ([`4f3e0b7`](https://github.com/HGNC/genew4-orm/commit/4f3e0b7d5dce64a2840ac732a7029cdaf76bae98))

Strengthen test_readwrite_session_creates_audit_logs: beyond confirming a Gene CREATE audit log
  exists for audit_test_user, also assert
  json.loads(audit_entry.field_changes)["approved_symbol"]["new"] == "RW_AUDIT_TEST". entity_id is 0
  for INSERTs, so field_changes is the only reliable discriminator tying the entry to the specific
  gene. approved_symbol is in ALWAYS_LOG_FIELDS so it is always recorded.

field_changes reads back as a JSON string (the model declares Mapped[dict] but wires no
  deserializer; get_field_diff() is broken for DB-loaded rows — flagged in spec, out of scope), so
  parse with json.loads in the test. Proven on SQLite: positive matches, a different symbol does
  not. No new regressions vs baseline.


## v0.4.0 (2026-05-28)

### Features

- Add 10 Phase 2 ORM models and 5 Gene columns
  ([`1101fa3`](https://github.com/HGNC/genew4-orm/commit/1101fa3ddf878ee4b97351ea174219ed013d379e))

New SQLModel classes for Phase 2 batch job data access: - TableModDate, Ccds, CcdsSequence,
  Gene2Refseq, GeneInfo - PseudogeneOrg, OtterSequence, EnsemblSequence, Hseq, HgncId2CcdsId

Gene model gains 5 new columns: - ccds_ids, hseq_ids, public_hseq_id, pseudogene_id, vega_ids

Key pattern: PK fields use Field(primary_key=True) with field name matching column name; non-PK
  fields with custom column names use sa_column=Column(). This avoids SQLModel's RuntimeError when
  combining primary_key=True with sa_column=.

53 new tests, all passing. Total: 319 unit tests green.

- Export all Phase 2 models from package __init__
  ([`85587b9`](https://github.com/HGNC/genew4-orm/commit/85587b905a59b86ff3e51504a4f23f241b803e1f))

Update models/__init__.py to import and re-export all 10 new Phase 2 model classes and add them to
  __all__.

Add test_phase2_model_exports.py with 12 tests verifying all new models are importable via
  genew4_orm.models and present in __all__.

### Refactoring

- Clean up SQLModel imports and improve code readability in models and tests
  ([`3e8bba2`](https://github.com/HGNC/genew4-orm/commit/3e8bba2caa60871ffe6334d0660389f79cd62ac7))


## v0.3.0 (2026-05-20)

### Documentation

- Add MCP server section for interactive help in README and getting-started
  ([`2822ac9`](https://github.com/HGNC/genew4-orm/commit/2822ac979389ed451d198fd611cd28c6cf92367c))

- Update MCP server chat URL in documentation
  ([`f50a3e6`](https://github.com/HGNC/genew4-orm/commit/f50a3e634dde8f10ddb73aa6bfc055b7311e479f))

- Update Python version requirement to 3.13+ in getting-started
  ([`1709ccd`](https://github.com/HGNC/genew4-orm/commit/1709ccded44210c14323d73f37a94c0f99935bb7))

Align Python version requirement across all documentation.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Features

- Add Comment and GeneHasComment models with publication workflow support
  ([`f18a4f5`](https://github.com/HGNC/genew4-orm/commit/f18a4f5f14e669bcbdbc47e53ffca7c19006710f))


## v0.2.21 (2026-02-16)

### Bug Fixes

- Correct GitHub organization name in URLs
  ([`717589b`](https://github.com/HGNC/genew4-orm/commit/717589b80c48caa89d62fb98bd58b7b0372fe5a7))

Change repo URLs from genew4 to HGNC (correct organization name).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.20 (2026-02-16)

### Bug Fixes

- Remove destination_dir for project pages
  ([`31fdbbd`](https://github.com/HGNC/genew4-orm/commit/31fdbbd367f01e6cfaa2637dd539e68d1ad7a40e))

For GitHub Pages project pages (orgname.github.io/repo), files should be at the root of gh-pages
  branch. GitHub automatically serves them at the repo-name subdirectory.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.19 (2026-02-16)

### Bug Fixes

- Deploy docs to genew4-orm subdirectory for org GitHub Pages
  ([`7b46617`](https://github.com/HGNC/genew4-orm/commit/7b46617ca02536e784e56560636392379be04388))

For organization GitHub Pages (hgnc.github.io), projects must be in subdirectories. Set
  destination_dir to genew4-orm so docs are deployed to hgnc.github.io/genew4-orm/

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.18 (2026-02-16)

### Bug Fixes

- Download artifact in docs deploy job
  ([`c768256`](https://github.com/HGNC/genew4-orm/commit/c7682566186d09c5b399fffa128af61f2514e00a))

The deploy job was not downloading the site artifact from the build job, so it was deploying an
  empty directory. Added download-artifact step to properly deploy the built documentation.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.17 (2026-02-16)

### Documentation

- Update URLs and badges for GitHub Pages
  ([`63cac7d`](https://github.com/HGNC/genew4-orm/commit/63cac7d3c921fe96984bf2fadd16d0f3438cc7a3))

- Update documentation links to hgnc.github.io/genew4-orm - Add site_url to mkdocs.yml - Update
  documentation URL in pyproject.toml - Remove PyPI badge (package not yet published)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.16 (2026-02-16)

### Bug Fixes

- Correct badge formatting in README
  ([`f34e3f1`](https://github.com/HGNC/genew4-orm/commit/f34e3f17f592acd5c445ef6ebd5cb30bff3d83a1))

- Update deploy condition to allow manual workflow dispatch
  ([`70a8a40`](https://github.com/HGNC/genew4-orm/commit/70a8a408782604bd34c51087c52a9b437476b094))


## v0.2.15 (2026-02-16)

### Bug Fixes

- **ci**: Multiply line-rate by 100 for coverage percentage
  ([`843dd24`](https://github.com/HGNC/genew4-orm/commit/843dd24039e56f8d969c22a54dee270fe8a56273))

The coverage.xml line-rate attribute is stored as a decimal (0-1), not a percentage. Multiply by 100
  to convert to percentage before comparing to 90% threshold.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Documentation

- Update documentation links to use the correct base URL
  ([`47493a8`](https://github.com/HGNC/genew4-orm/commit/47493a8340da8d759b9230a60031ac454a9c6c41))


## v0.2.14 (2026-02-16)

### Chores

- **ci**: Print all coverage.xml content for debugging
  ([`dc281c6`](https://github.com/HGNC/genew4-orm/commit/dc281c63fa1cc5ff935a884ba136277812655d6b))

Change from printing first 50 lines to printing entire coverage.xml file content to help diagnose
  coverage threshold issues.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **ci**: Print coverage.xml content for debugging
  ([`9a16cb3`](https://github.com/HGNC/genew4-orm/commit/9a16cb39cd7901f3923fea3e0a4b0a30b52e9ea4))

Add debug output to print first 50 lines of coverage.xml before checking threshold. This helps
  diagnose why coverage is showing 1.0% instead of the expected value.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.13 (2026-02-16)

### Bug Fixes

- **ci**: Use getroot() instead of find() for coverage.xml parsing
  ([`a748d15`](https://github.com/HGNC/genew4-orm/commit/a748d15e9bb1dab42b50b7e7eb0dac73f8691c3f))

The coverage.xml file from coverage.py has <coverage> as the root element with line-rate as a direct
  attribute. Using tree.getroot() is more direct and reliable than tree.find('.//coverage').

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Chores

- **ci**: Remove artifact upload and HTML report from test.yml
  ([`339cb8e`](https://github.com/HGNC/genew4-orm/commit/339cb8edba09592f89b12ebb18fa8e2c4f9953b8))

Since test.yml doesn't use Codecov and we're not keeping coverage artifacts, remove: - Upload
  coverage to Artifacts step - --cov-report=html flag (no longer needed without artifact upload)

Simplifies workflow and reduces CI time.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.12 (2026-02-13)

### Bug Fixes

- **ci**: Add None check for coverage element in XML parsing
  ([`cbc0019`](https://github.com/HGNC/genew4-orm/commit/cbc001944cf98e8a12d5b583bab5c23be2e13103))

The tree.find() method returns None when element is not found, which causes AttributeError when
  calling .get() on None. Add explicit check to handle missing coverage element gracefully.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.11 (2026-02-13)

### Bug Fixes

- **ci**: Fix AttributeError in exception formatting (test.yml)
  ([`49b4ca5`](https://github.com/HGNC/genew4-orm/commit/49b4ca5ef02ab38ab8ccf9caa810d12adb23616c))

The debug print statement was using f-string formatting on exception object {e}, which fails with
  AttributeError when e is NoneType. Change to use {type(e).__name__} which works for all exception
  types.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.10 (2026-02-13)

### Bug Fixes

- **ci**: Add debug output and better error handling in coverage check
  ([`eefc354`](https://github.com/HGNC/genew4-orm/commit/eefc354d9733355eeaad9b452517eb95550029ff))

- Add explicit cov_file variable for coverage.xml path - Check if file exists before parsing - Catch
  ET.ParseError specifically - Add generic exception fallback - More descriptive error messages

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **ci**: Add explicit shell: bash to coverage threshold step
  ([`244ee5f`](https://github.com/HGNC/genew4-orm/commit/244ee5fd4a094674769ef0eec23bdbf602ca50e5))

Add explicit shell: bash directive to ensure proper output capture for GitHub Actions warning
  annotations from the Python script.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **ci**: Use python3 in coverage check (test.yml)
  ([`34799cd`](https://github.com/HGNC/genew4-orm/commit/34799cd03b6c40db7c9af64fc2ee2590622d4e92))

Use python3 explicitly to avoid issues with python command not being found or pointing to wrong
  Python version.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.9 (2026-02-13)

### Bug Fixes

- **ci**: Use heredoc for coverage check script in test.yml
  ([`a7e6c7f`](https://github.com/HGNC/genew4-orm/commit/a7e6c7f2737c4799d52c4b6a7641193925ea66a0))

Use heredoc (<<'EOF' ... EOF) instead of quoted Python -c to avoid YAML parsing issues with
  multi-line strings and special characters.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.8 (2026-02-13)

### Bug Fixes

- **ci**: Simplify coverage threshold check using Python
  ([`5474bf7`](https://github.com/HGNC/genew4-orm/commit/5474bf795b9756050248a40144a8fc4a6cb9a2a6))

Replace bash/bc approach with pure Python comparison to avoid: - Bash syntax issues with multi-line
  scripts - bc dependency - Environment variable substitution problems

Now handles XML parsing and threshold comparison entirely in Python with proper GitHub Actions
  warning format output.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **ci**: Use SQLAlchemy .is_() for null-safe boolean comparison
  ([`453919e`](https://github.com/HGNC/genew4-orm/commit/453919ecb5e9e8e6a46048d7560bd4573245f219))

Use .is_(False) instead of == False for comparing boolean fields in SQLAlchemy. This generates "IS
  FALSE" in SQL which correctly matches the boolean value while satisfying ruff E712 rule.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.7 (2026-02-13)

### Code Style

- **ci**: Fix ruff E712 comparisons to False in test files
  ([`1a7a190`](https://github.com/HGNC/genew4-orm/commit/1a7a19095ea409828e0234e7d041e7cae1221cae))

- test_external_resource.py: use not ExternalResource.approved - test_reminder.py: use not
  Reminder.sent

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.6 (2026-02-13)

### Bug Fixes

- **ci**: Fix bash syntax in coverage threshold check (test.yml)
  ([`2001704`](https://github.com/HGNC/genew4-orm/commit/20017044aed671effdb6885e8cd009fc826b26b5))

The if statement was using (( )) construct with command substitution which caused bash syntax
  errors. Fixed to use [ ] for proper string comparison with bc -l result.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Code Style

- **ci**: Format conftest.py with ruff
  ([`cff0127`](https://github.com/HGNC/genew4-orm/commit/cff01276014607cbd5e9e2fab239211aabf8228a))

Fix ruff formatting issue with multi-line string argument to text().

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.5 (2026-02-13)

### Bug Fixes

- **ci**: Add database env vars to coverage report step in ci.yml
  ([`278acf9`](https://github.com/HGNC/genew4-orm/commit/278acf967c40ad6fd9545f928fbd0f22ae97f4f0))

The "Generate coverage report" step now includes DATABASESETTINGS_* environment variables, ensuring
  e2e and integration/postgresql tests run correctly instead of skipping due to missing database
  credentials.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.4 (2026-02-13)

### Bug Fixes

- **ci**: Handle missing database credentials gracefully in tests
  ([`4a57405`](https://github.com/HGNC/genew4-orm/commit/4a574056fe44835b4d7adbb75af3e999f2eecb33))

Tests that require PostgreSQL (e2e, integration/postgresql) now skip gracefully when
  DATABASESETTINGS_PG_USER and DATABASESETTINGS_PG_PASSWORD are not set, instead of failing with
  ValidationError.

This fixes CI failures when running all tests together, as the tests that require database
  credentials will skip cleanly rather than crashing during fixture setup.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.2.3 (2026-02-13)

### Bug Fixes

- **tests**: Update junction table association handling to use merge for duplicates
  ([`7cca375`](https://github.com/HGNC/genew4-orm/commit/7cca3751b8ef7bcf3afcdb16be2ed8d0cb29800a))


## v0.2.2 (2026-02-13)

### Bug Fixes

- **tests**: Create gene group before testing alias creation
  ([`9167d87`](https://github.com/HGNC/genew4-orm/commit/9167d875bb5f3c57fa24cd6577d36c4428744f3f))

- **tests**: Update query conditions to use explicit comparison for boolean fields
  ([`fec284f`](https://github.com/HGNC/genew4-orm/commit/fec284fdce74599ab1a4e5612c877a6ab714b106))


## v0.2.1 (2026-02-13)

### Bug Fixes

- **tests**: Add cleanup step to truncate PostgreSQL tables after tests
  ([`ce0c260`](https://github.com/HGNC/genew4-orm/commit/ce0c2602a07f6f7e64a10c89a42d7bc4b0fe4595))

### Refactoring

- **tests**: Add debug print statement for session type in TestReminderCRUD
  ([`7f205f7`](https://github.com/HGNC/genew4-orm/commit/7f205f7dc4fdad82678370205ad841cc762f79cb))

- **tests**: Remove clean_database fixture for integration tests
  ([`89e3762`](https://github.com/HGNC/genew4-orm/commit/89e3762c0ced14d32193da827a98fc4b6650c278))


## v0.2.0 (2026-02-13)

### Features

- **ci**: Add manual creation of cytoband table in database initialization
  ([`5f81c3d`](https://github.com/HGNC/genew4-orm/commit/5f81c3d197ce223fed57786150f40c21c4a46fee))

### Refactoring

- **ci**: Enhance database schema initialization with detailed output and PYTHONPATH adjustment
  ([`ac85019`](https://github.com/HGNC/genew4-orm/commit/ac85019050fb50092ddc0aad66d6cd3bbd37e207))

- **ci**: Rename database migration step and initialize schema directly
  ([`9634eb7`](https://github.com/HGNC/genew4-orm/commit/9634eb7e13cdc5330a6d1e947758dfba70a718d3))

- **ci, test**: Import models to register with SQLModel during database initialization
  ([`dde5f53`](https://github.com/HGNC/genew4-orm/commit/dde5f53aae902a6086bae6eea0a9f4ea6af59e4d))

- **ci, test**: Update database schema initialization to set PYTHONPATH
  ([`d836367`](https://github.com/HGNC/genew4-orm/commit/d8363671a6bd632d5e52ad8bfeebce2a5d07b3d9))

- **tests**: Update clean_database fixture to autouse for integration tests
  ([`ed057d6`](https://github.com/HGNC/genew4-orm/commit/ed057d63ae5510c6060b7587fc6f73a505ebfe6e))


## v0.1.3 (2026-02-13)

### Refactoring

- **audit_log**: Remove obsolete migration and update revision references
  ([`f1f1839`](https://github.com/HGNC/genew4-orm/commit/f1f1839e253ee0ca8037e4527153c0db7bdc8374))


## v0.1.2 (2026-02-13)

### Bug Fixes

- **dependencies**: Add alembic as a dependency for database migrations
  ([`3295b5a`](https://github.com/HGNC/genew4-orm/commit/3295b5a1ef8f064a01ee7090273063038de971fe))


## v0.1.1 (2026-02-13)

### Bug Fixes

- **ci**: Add database migration step to CI workflow
  ([`74fbe61`](https://github.com/HGNC/genew4-orm/commit/74fbe61e94d1abd49adeec38a131b41b65b7851a))

- **ci**: Add postgres service container to ci.yml
  ([`a85bba1`](https://github.com/HGNC/genew4-orm/commit/a85bba1707ba36373c14a6877a1adb68558072c5))

The ci.yml workflow was failing because integration and E2E tests require a PostgreSQL database
  connection, but there was no service container running. This commit adds a PostgreSQL 16 service
  container matching the configuration used in test.yml.

Fixes connection errors: "connection to server at 127.0.0.1, port 5432 failed"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **ci**: Correct postgres health check flags in service containers
  ([`951785d`](https://github.com/HGNC/genew4-orm/commit/951785d5f6f0dbbb649ef0a9a345a5358c3c7cd8))

The GitHub Actions service containers were using incorrect health check flags, causing "unknown
  flag: --interval" errors. Docker health checks require the --health- prefix for health-related
  options.

Changes: - --interval → --health-interval - --timeout → --health-timeout - --retries →
  --health-retries

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.1.0 (2026-02-13)

### Chores

- Add environment variables for integration and e2e tests in CI workflow
  ([`9b995c3`](https://github.com/HGNC/genew4-orm/commit/9b995c33e3a3658e55c55d526b70feb0859b4a1d))

- Remove PostgreSQL service and related database setup from CI workflow
  ([`4202dcb`](https://github.com/HGNC/genew4-orm/commit/4202dcbb083ffac20974eaaaf969868c005c1a46))

- Remove redundant formatting checks from lint workflow
  ([`0c0582a`](https://github.com/HGNC/genew4-orm/commit/0c0582a4496feb40686d8e91ee040810c3cec561))

- Streamline CI workflows by removing unused environment variables and optimizing dependency
  installation
  ([`f00ba96`](https://github.com/HGNC/genew4-orm/commit/f00ba96970edcea2526c46a8bbe003f8c3c2d846))

- Update CI workflows for improved dependency management and Python version consistency
  ([`0be863b`](https://github.com/HGNC/genew4-orm/commit/0be863b07dd37ef9bf0281a5973f97e57abe0b42))

- Update Python Semantic Release action version and configure PostgreSQL service for testing
  ([`5f66fb2`](https://github.com/HGNC/genew4-orm/commit/5f66fb2eea192857fe538b724b8d65282ba35b3e))

### Features

- Enhance README with CI/CD details and contributing workflow
  ([`aae6c3e`](https://github.com/HGNC/genew4-orm/commit/aae6c3e320760f703049f5de6995da140b4fa6c6))

feat: add docker-compose for PostgreSQL integration testing

docs: create development workflow guide for contributors

docs: update getting started guide with development workflow link

docs: add CI/CD pipeline information to index page

docs: include development workflow in navigation

chore: update project metadata in pyproject.toml for better clarity

fix: clean up imports and unused code in model files

fix: update session initialization to handle settings correctly

refactor: modify query helper functions to use scalars for better performance

test: update unit tests to reflect changes in query helper functions
