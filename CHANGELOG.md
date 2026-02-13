# CHANGELOG


## v0.2.10 (2026-02-13)


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
