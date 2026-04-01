# Changelog

All notable changes to ChromaOracle CLI are documented here.

For the web version changelog, see [chromaoracle.com](https://chromaoracle.com).

## [2.1.0] - 2026-03-28

### Changed
- **BFS optimization** — linked-list paths and early bailout for faster solves
- **ContainerCollection optimization** — efficient state expansion with cached keys
- **Container optimization** — immutability with property caching
- Ruff lint and mypy type checking fixes

### Added
- Project metadata and homepage URL in pyproject.toml
- Web version promotion with screenshots in README

## [2.0.0] - 2026-03-10

### Changed
- **Migrated to uv & ruff** from pip/setuptools
- **Requires Python 3.13+**
- Renamed internal modules for consistency
- Updated CLI output wording

### Fixed
- Unknown color handling in mystery solver
- Stack move decision logic
- Docker entrypoint and dependency constraints

### Added
- **Win strategy** (`win_strategy`) — find common prefix across all mystery solutions
- **Match first steps algorithm** — identify guaranteed safe moves
- Docker support with publish CI workflow

## [1.0.0] - 2025-12-01

### Added
- **BFS/DFS solver** for color-sorting puzzles (Water Sort, Ball Sort)
- **Mystery solver** — guess unknown/hidden colors via permutation analysis
- **CLI interface** via Click (`chroma-oracle solve <file>`)
- JSON level file input
- Verbose output mode
- Unit tests for all core modules (container, collection, search, CLI)
- GitHub Actions CI for tests
- Docker support
