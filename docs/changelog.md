# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.1] - 2025-11-11

## [0.1.0] - 2025-11-10
### Added

- Add VScode Python pytest settings

### Changed

- Set package-ecosystem to 'pip' in dependabot config
- Updated changed names in tests.

### Documentation

- Docs workflow runs only when triggered by others.

### Fixed

- Fix Codecov upload condition and correct file parameter in CI workflow
- Fix mypy typing issue, add CLI config tests

## [0.0.1] - 2024-11-06
### Added

- Initial release
- Support for Pools, Partners, Distributions, Certificates, and History resources

- Add GitHub Actions workflow for automated testing

- Update pyproject.toml:
  - Add requests dependency
  - Add dev dependencies (pytest, black, flake8, isort, mypy)
  - Configure tool settings for linting and testing

### Documentation
- Getting Started: Installation, Quick Start, Authentication
- User Guide: Client, Pools, Partners, Distributions, Certificates, History
- API Reference: Client, Models, Resources, Exceptions
- Contributing: Development Setup, Testing, Code Style
- Changelog

[0.1.1]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.1
[0.1.0]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.0
[0.0.1]: https://github.com/inntran/tmo-api-python/releases/tag/v0.0.1
