# CHANGELOG


## v0.1.0 (2026-02-13)

### Chores

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
