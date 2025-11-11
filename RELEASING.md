# Release Process

This document describes how to release a new version of tmo-api.

## Tools

- **bump-my-version**: Manages version numbers and git tags
- **git-cliff**: Generates changelog entries from git commits

## Quick Release Steps

### 1. Generate Changelog Entries

Use git-cliff to generate changelog entries from recent commits:

```bash
# See changes since last tag
git-cliff --unreleased

# See changes from specific commit range
git-cliff HEAD~10..HEAD

# See changes since a specific tag
git-cliff v0.0.1..HEAD

# Copy to clipboard (macOS)
git-cliff --unreleased | pbcopy

# Copy to clipboard (Linux with xclip)
git-cliff --unreleased | xclip -selection clipboard
```

### 2. Update Changelog

Edit `docs/changelog.md` and add the generated entries under the `[Unreleased]` section:

```markdown
## [Unreleased]

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

### Changed
- Updated something

## [0.0.1] - 2024-11-06
...
```

Commit your changelog updates:

```bash
git add docs/changelog.md
git commit -m "docs: Update changelog for upcoming release"
```

### 3. Bump Version

Use bump-my-version to update version numbers and create git tags:

```bash
# Bump patch version (0.0.1 → 0.0.2)
bump-my-version bump patch

# Bump minor version (0.0.1 → 0.1.0)
bump-my-version bump minor

# Bump major version (0.0.1 → 1.0.0)
bump-my-version bump major

# Dry run to see what would change (requires clean working directory or --allow-dirty)
bump-my-version bump --dry-run --allow-dirty patch
```

This will automatically:
- Update version in `pyproject.toml`
- Update version in `src/tmo_api/_version.py`
- Convert `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` in `docs/changelog.md`
- Add release link at the bottom of changelog
- Create a git commit with message: `Bump version: X.Y.Z → X.Y.Z`
- Create a git tag: `vX.Y.Z`

### 4. Push to GitHub

```bash
# Push commits and tags
git push && git push --tags
```

### 5. Create GitHub Release

The GitHub Actions workflow will automatically create a release and publish to PyPI when you push the tag.

Alternatively, manually create a release on GitHub:
1. Go to https://github.com/inntran/tmo-api-python/releases/new
2. Select the tag you just created
3. Copy the changelog section for this version as the release notes
4. Publish the release

## Useful Commands

### Check Current Version

```bash
bump-my-version show current_version
```

### Show What Versions Would Be

```bash
bump-my-version show-bump
```

### View Recent Commits

```bash
# Simple list
git log --oneline -10

# With dates
git log --pretty=format:"%h - %s (%ar)" -10

# Since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Customize git-cliff Output

Edit `cliff.toml` to customize:
- Commit categorization rules
- Output format
- Which commits to include/exclude
- GitHub issue linking

## Commit Message Guidelines

For better changelog generation, follow these conventions:

- **Added**: `Add`, `New`, `Implement`, `feat:`
- **Fixed**: `Fix`, `Bug`, `Potential fix`
- **Changed**: `Update`, `Increase`, `Set`
- **Documentation**: `Doc`, `docs:`
- **Security**: Include "security" in the message

Examples:
```
Add support for multiple authentication methods
Fix rate limiting issue in API client
Update dependencies to latest versions
docs: Improve API documentation
```

## Configuration Files

- `.bumpversion.toml` - bump-my-version configuration
- `cliff.toml` - git-cliff configuration
- `docs/changelog.md` - Changelog file

## Troubleshooting

### Git working directory is not clean

If bump-my-version complains about a dirty working directory:
```bash
# Check what's uncommitted
git status

# Either commit your changes, or use --allow-dirty (not recommended for releases)
bump-my-version bump --allow-dirty patch
```

### No commits found

If git-cliff shows no commits, you might need to specify a range:
```bash
# All commits
git-cliff

# Since beginning
git-cliff --all
```
