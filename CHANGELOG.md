# CHANGELOG


## v0.1.3 (2026-02-13)


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
