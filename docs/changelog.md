# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.3] - 2025-11-18
### Added

- Add updated TMO API spec 20251117.

### Changed
- Updated to Python 3.14 for development

### Fixed

- Fixed path processing issue in tmoapi download.

## [0.1.2] - 2025-11-12
### Added

- Add inline documentations to partner and history endpoints.
- Add returned data structures to documentations

### Changed
- Refactor documentation deployment steps to remove unnecessary push flags

## [0.1.1] - 2025-11-11
### Fixed

- Fix tmoapi loading postman collection path issue

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

[0.1.3]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.3
[0.1.2]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.2
[0.1.1]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.1
[0.1.0]: https://github.com/inntran/tmo-api-python/releases/tag/v0.1.0
[0.0.1]: https://github.com/inntran/tmo-api-python/releases/tag/v0.0.1
