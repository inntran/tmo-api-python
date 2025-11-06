# Git Branching Strategy

This project follows a **Git Flow** branching model for organized development and releases.

## Branch Structure

### Main Branches

- **`main`** - Production-ready code
  - Protected branch
  - Only accepts merges from `staging` or hotfix branches
  - Tagged with version numbers for releases
  - Automatically deploys to PyPI (via GitHub Actions)

- **`develop`** - Main development branch
  - Integration branch for features
  - Default branch for development
  - Protected branch (requires PR reviews)
  - Base branch for all feature branches

- **`staging`** - Pre-production testing
  - Testing branch before production
  - Merge from `develop` when ready for release
  - Deploy to test PyPI or staging environment
  - Merge to `main` after validation

### Supporting Branches

These are temporary branches that should be deleted after merging:

- **`feature/*`** - New features
  - Branch from: `develop`
  - Merge back to: `develop`
  - Naming: `feature/short-description`
  - Example: `feature/add-authentication`

- **`bugfix/*`** - Bug fixes during development
  - Branch from: `develop`
  - Merge back to: `develop`
  - Naming: `bugfix/issue-description`
  - Example: `bugfix/fix-timeout-error`

- **`hotfix/*`** - Critical production fixes
  - Branch from: `main`
  - Merge to: `main` AND `develop`
  - Naming: `hotfix/critical-issue`
  - Example: `hotfix/security-vulnerability`

- **`release/*`** - Release preparation
  - Branch from: `develop`
  - Merge to: `main` AND `develop`
  - Naming: `release/version-number`
  - Example: `release/1.0.0`

## Workflow

### Feature Development
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature

# Work on your feature
git add .
git commit -m "Add new feature"

# Push and create PR to develop
git push -u origin feature/my-new-feature
```

### Bug Fixes
```bash
# Create bugfix branch from develop
git checkout develop
git pull origin develop
git checkout -b bugfix/fix-something

# Fix the bug
git add .
git commit -m "Fix something"

# Push and create PR to develop
git push -u origin bugfix/fix-something
```

### Release Process
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/1.0.0

# Update version numbers, changelog
git add .
git commit -m "Prepare release 1.0.0"

# Push to staging for testing
git checkout staging
git merge release/1.0.0
git push origin staging

# After validation, merge to main
git checkout main
git merge release/1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge release/1.0.0
git push origin develop

# Delete release branch
git branch -d release/1.0.0
git push origin --delete release/1.0.0
```

### Hotfix Process
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Fix the critical issue
git add .
git commit -m "Fix critical issue"

# Merge to main
git checkout main
git merge hotfix/critical-fix
git tag -a v1.0.1 -m "Hotfix 1.0.1"
git push origin main --tags

# Merge to develop
git checkout develop
git merge hotfix/critical-fix
git push origin develop

# Delete hotfix branch
git branch -d hotfix/critical-fix
git push origin --delete hotfix/critical-fix
```

## Branch Protection Rules

Configure these on GitHub (Settings → Branches):

### For `main`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (tests, linting)
- ✅ Require branches to be up to date before merging
- ✅ Require linear history
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push (only maintainers)

### For `develop`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Allow force pushes by maintainers (for cleanup)

### For `staging`:
- ✅ Require status checks to pass
- ✅ Allow direct pushes from release branches

## Best Practices

1. **Keep commits atomic** - One logical change per commit
2. **Write descriptive commit messages** - Explain why, not just what
3. **Keep branches short-lived** - Merge frequently to avoid conflicts
4. **Delete merged branches** - Keep the repository clean
5. **Never commit directly to main** - Always use PRs
6. **Tag all releases** - Use semantic versioning (v1.0.0)
7. **Update CHANGELOG.md** - Document all changes in releases
8. **Run tests locally** - Before pushing and creating PRs

## Quick Reference

```bash
# Start new feature
git checkout develop && git pull && git checkout -b feature/name

# Update from develop while working
git checkout develop && git pull && git checkout - && git rebase develop

# Finish feature
git push -u origin feature/name  # Then create PR on GitHub

# Check what branch you're on
git branch

# See recent commits
git log --oneline --graph --all -10
```
