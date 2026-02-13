.PHONY: help

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PYTHON_VERSION := 3.13
VENV := .venv
SRC := src/genew4_orm
TESTS := tests

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_RED := \033[31m

help: ## Show this help message
	@echo "$(COLOR_BOLD)genew4-orm - Available commands:$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Development:$(COLOR_RESET)"
	@echo "  make venv           # Create virtual environment"
	@echo "  make install        # Install dependencies"
	@echo "  make pre-commit     # Install pre-commit hooks"
	@echo ""
	@echo "$(COLOR_GREEN)Testing:$(COLOR_RESET)"
	@echo "  make test           # Run all tests"
	@echo "  make test-unit      # Run unit tests only"
	@echo "  make test-integration     # Run integration tests (requires postgres)"
	@echo "  make test-e2e       # Run e2e tests"
	@echo "  make test-cov       # Run tests with coverage report"
	@echo ""
	@echo "$(COLOR_GREEN)Linting & Type Checking:$(COLOR_RESET)"
	@echo "  make lint           # Run all linters"
	@echo "  make ruff           # Run ruff linter"
	@echo "  make mypy           # Run mypy type checker"
	@echo "  make black          # Run black formatter check"
	@echo "  make isort          # Run isort import sorter check"
	@echo "  make format         # Format code with black and isort"
	@echo ""
	@echo "$(COLOR_GREEN)Database:$(COLOR_RESET)"
	@echo "  make db-up          # Start PostgreSQL with Docker"
	@echo "  make db-down        # Stop PostgreSQL"
	@echo "  make db-shell       # Open PostgreSQL shell"
	@echo ""
	@echo "$(COLOR_GREEN)Documentation:$(COLOR_RESET)"
	@echo "  make docs-serve     # Serve documentation locally"
	@echo "  make docs-build     # Build documentation"
	@echo ""
	@echo "$(COLOR_GREEN)Cleanup:$(COLOR_RESET)"
	@echo "  make clean          # Remove build artifacts"
	@echo "  make clean-all      # Remove all generated files"
	@echo ""

## Development
venv: ## Create virtual environment
	@echo "$(COLOR_GREEN)Creating virtual environment...$(COLOR_RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(COLOR_GREEN)Virtual environment created at $(VENV)$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Activate with: source $(VENV)/bin/activate$(COLOR_RESET)"

install: ## Install dependencies
	@echo "$(COLOR_GREEN)Installing dependencies...$(COLOR_RESET)"
	uv pip install -e .
	uv pip install -e ".[dev]"
	uv pip install pre-commit
	@echo "$(COLOR_GREEN)Dependencies installed!$(COLOR_RESET)"

pre-commit: ## Install pre-commit hooks
	@echo "$(COLOR_GREEN)Installing pre-commit hooks...$(COLOR_RESET)"
	pre-commit install
	@echo "$(COLOR_GREEN)Pre-commit hooks installed!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Run 'make pre-commit' to try the hooks$(COLOR_RESET)"

## Testing
test: ## Run all tests
	@echo "$(COLOR_GREEN)Running all tests...$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS)/ -v
	@echo "$(COLOR_GREEN)All tests completed!$(COLOR_RESET)"

test-unit: ## Run unit tests only
	@echo "$(COLOR_GREEN)Running unit tests...$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS)/unit/ -v
	@echo "$(COLOR_GREEN)Unit tests completed!$(COLOR_RESET)"

test-integration: ## Run integration tests (requires PostgreSQL)
	@echo "$(COLOR_GREEN)Running integration tests...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Ensuring PostgreSQL is running (start with 'make db-up')$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS)/integration/ -v
	@echo "$(COLOR_GREEN)Integration tests completed!$(COLOR_RESET)"

test-e2e: ## Run e2e tests
	@echo "$(COLOR_GREEN)Running e2e tests...$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS)/e2e/ -v
	@echo "$(COLOR_GREEN)E2E tests completed!$(COLOR_RESET)"

test-cov: ## Run tests with coverage
	@echo "$(COLOR_GREEN)Running tests with coverage...$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS)/ -v --cov=genew4_orm --cov-report=html --cov-report=term-missing
	@echo "$(COLOR_GREEN)Tests with coverage completed!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Open htmlcov/index.html to view coverage report$(COLOR_RESET)"

## Linting & Type Checking
lint: ## Run all linters
	@echo "$(COLOR_GREEN)Running all linters...$(COLOR_RESET)"
	@$(MAKE) ruff
	@$(MAKE) mypy
	@echo "$(COLOR_GREEN)All linters completed!$(COLOR_RESET)"

ruff: ## Run ruff linter
	@echo "$(COLOR_GREEN)Running ruff...$(COLOR_RESET)"
	ruff check $(SRC)
	@echo "$(COLOR_GREEN)Ruff check completed!$(COLOR_RESET)"

mypy: ## Run mypy type checker
	@echo "$(COLOR_GREEN)Running mypy...$(COLOR_RESET)"
	mypy $(SRC)
	@echo "$(COLOR_GREEN)MyPy check completed!$(COLOR_RESET)"

black: ## Run black formatter check
	@echo "$(COLOR_GREEN)Checking code formatting with black...$(COLOR_RESET)"
	black --check $(SRC)
	@echo "$(COLOR_GREEN)Black check completed!$(COLOR_RESET)"

isort: ## Run isort import sorter check
	@echo "$(COLOR_GREEN)Checking import sorting with isort...$(COLOR_RESET)"
	isort --check-only --profile black $(SRC)
	@echo "$(COLOR_GREEN)Isort check completed!$(COLOR_RESET)"

format: ## Format code with black and isort
	@echo "$(COLOR_YELLOW)Formatting code...$(COLOR_RESET)"
	black $(SRC)
	isort $(SRC)
	@echo "$(COLOR_GREEN)Code formatted!$(COLOR_RESET)"

## Database
db-up: ## Start PostgreSQL with Docker
	@echo "$(COLOR_GREEN)Starting PostgreSQL...$(COLOR_RESET)"
	docker-compose up -d postgres
	@echo "$(COLOR_GREEN)PostgreSQL started on localhost:5432$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Use 'make db-shell' to connect$(COLOR_RESET)"

db-down: ## Stop PostgreSQL
	@echo "$(COLOR_YELLOW)Stopping PostgreSQL...$(COLOR_RESET)"
	docker-compose down
	@echo "$(COLOR_GREEN)PostgreSQL stopped$(COLOR_RESET)"

db-shell: ## Open PostgreSQL shell
	@echo "$(COLOR_GREEN)Opening PostgreSQL shell...$(COLOR_RESET)"
	docker-compose exec postgres psql -U genew4_test -d genew4_test

## Documentation
docs-serve: ## Serve documentation locally
	@echo "$(COLOR_GREEN)Serving documentation at http://127.0.0.1:8000$(COLOR_RESET)"
	mkdocs serve

docs-build: ## Build documentation
	@echo "$(COLOR_GREEN)Building documentation...$(COLOR_RESET)"
	mkdocs build
	@echo "$(COLOR_GREEN)Documentation built in site/$(COLOR_RESET)"

## Cleanup
clean: ## Remove build artifacts
	@echo "$(COLOR_YELLOW)Cleaning build artifacts...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	@echo "$(COLOR_GREEN)Clean completed!$(COLOR_RESET)"

clean-all: ## Remove all generated files
	@echo "$(COLOR_YELLOW)Cleaning all generated files...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	rm -rf htmlcov/ site/ .coverage.xml
	rm -rf .mkdocs_cache/
	@echo "$(COLOR_GREEN)Deep clean completed!$(COLOR_RESET)"

## CI Commands (used by GitHub Actions)
ci-install: ## Install CI dependencies
	pip install ruff mypy black isort

ci-lint: ## Run all linters (CI)
	ruff check $(SRC)
	mypy $(SRC)
	black --check $(SRC)
	isort --check-only --profile black $(SRC)

## Development helpers
dev-setup: venv install pre-commit ## Full development setup
	@$(MAKE) venv
	@$(MAKE) install
	@$(MAKE) pre-commit
	@echo "$(COLOR_GREEN)$(COLOR_BOLD)Development environment ready!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Activate with: source $(VENV)/bin/activate$(COLOR_RESET)"

.PHONY: venv install pre-commit test test-unit test-integration test-e2e test-cov lint ruff mypy black isort format docs-serve docs-build clean clean-all db-up db-down db-shell ci-install ci-lint dev-setup
