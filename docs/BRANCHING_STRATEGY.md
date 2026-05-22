# Branching Strategy

This document outlines the Git branching strategy used for the Strava Report project.

## Overview

We use a modified GitFlow branching strategy to manage development, releases, and hotfixes while maintaining a clean and organized git history.

## Main Branches

### `main`
- **Purpose**: Production-ready code
- **Protection**: 
  - Required status checks (CI/CD pipeline must pass)
  - Require pull request reviews
  - No direct commits allowed
- **Deployment**: Automatic deployment to production on merge
- **Status**: Always deployable

### `develop`
- **Purpose**: Integration branch for features
- **Protection**:
  - Required status checks (CI/CD pipeline must pass)
  - Require pull request reviews
  - No direct commits allowed
- **Deployment**: Automatic deployment to staging on merge
- **Status**: Should be stable but not necessarily production-ready

## Supporting Branches

### `feature/*`
- **Purpose**: Develop new features
- **Naming Convention**: `feature/description-of-feature`
- **Source**: Branch from `develop`
- **Destination**: Merge back to `develop` via pull request
- **Lifecycle**: Short-lived (days to weeks)
- **Example**: `feature/user-authentication`, `activity-filtering`

### `bugfix/*`
- **Purpose**: Fix bugs that don't require immediate production deployment
- **Naming Convention**: `bugfix/description-of-bugfix`
- **Source**: Branch from `develop`
- **Destination**: Merge back to `develop` via pull request
- **Lifecycle**: Short-lived
- **Example**: `bugfix/fix-date-filter`, `bugfix/api-timeout`

### `hotfix/*`
- **Purpose**:紧急修复生产环境的严重问题**
- **Naming Convention**: `hotfix/description-of-hotfix`
- **Source**: Branch from `main`
- **Destination**: Merge to both `main` and `develop`
- **Lifecycle**: Very short-lived (hours to days)
- **Example**: `hotfix/security-patch`, `hotfix/database-connection`

## Workflow

### Feature Development Workflow

```bash
# 1. Create a new feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... commit changes ...

# 3. Push and create pull request
git push origin feature/your-feature-name
# Create PR: feature/your-feature-name -> develop

# 4. After review and CI/CD passes, merge the PR
# Delete the feature branch
```

### Bugfix Workflow

```bash
# 1. Create a bugfix branch from develop
git checkout develop
git pull origin develop
git checkout -b bugfix/your-bugfix-name

# 2. Fix the bug
# ... commit changes ...

# 3. Push and create pull request
git push origin bugfix/your-bugfix-name
# Create PR: bugfix/your-bugfix-name -> develop

# 4. After review and CI/CD passes, merge the PR
# Delete the bugfix branch
```

### Hotfix Workflow

```bash
# 1. Create a hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/your-hotfix-name

# 2. Fix the critical issue
# ... commit changes ...

# 3. Push and create pull request to main
git push origin hotfix/your-hotfix-name
# Create PR: hotfix/your-hotfix-name -> main

# 4. After review and CI/CD passes, merge to main
# Delete the hotfix branch

# 5. Merge the hotfix back to develop
git checkout develop
git pull origin develop
git merge main
git push origin develop
```

## Branch Protection Rules

### `main` Branch
- ✅ Require pull request before merging
- ✅ Require approval from 1 reviewer
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ❌ Restrict who can push to this branch
- ❌ Do not allow bypassing the above settings

### `develop` Branch
- ✅ Require pull request before merging
- ✅ Require approval from 1 reviewer
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ❌ Restrict who can push to this branch
- ❌ Do not allow bypassing the above settings

## Commit Message Convention

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples
```
feat(api): add activity filtering by date range

- Add start_date and end_date parameters to GET /api/activities/
- Update API documentation
- Add unit tests for date filtering logic

Closes #123
```

```
fix(etl): handle null values in bronze layer

- Add null checks for distance and time fields
- Update data cleaning logic
- Add test cases for null handling

Fixes #45
```

## Pull Request Guidelines

### Title Format
- Use the same format as commit messages
- Include the ticket/issue number if applicable
- Example: `feat(api): add activity filtering (#123)`

### Description
- Describe what changes were made and why
- Include screenshots for UI changes
- List any breaking changes
- Reference related issues

### Review Process
1. Create PR from feature/bugfix branch to develop (or hotfix to main)
2. Ensure all CI/CD checks pass
3. Request at least one reviewer approval
4. Address review comments
5. Merge after approval

## Release Process

### Preparing for Release
1. Ensure `develop` branch is stable
2. Update version number in `pyproject.toml`
3. Update CHANGELOG.md
4. Create PR: `develop` -> `main`
5. Merge after review and testing

### Post-Release
1. Tag the release commit
2. Deploy to production
3. Merge `main` back to `develop` to sync changes
4. Announce release

## Best Practices

1. **Keep branches focused**: One branch should address one issue or feature
2. **Update frequently**: Regularly merge changes from the source branch
3. **Write clear commit messages**: Follow the convention above
4. **Don't break the build**: Ensure CI/CD passes before creating PR
5. **Clean up branches**: Delete branches after merging
6. **Use descriptive names**: Branch names should clearly indicate their purpose
7. **Test thoroughly**: Write tests for new features and bug fixes
8. **Document changes**: Update relevant documentation

## Emergency Situations

If a critical bug is found in production:

1. Immediately create a `hotfix/*` branch from `main`
2. Implement the fix with minimal changes
3. Create PR to `main` with expedited review
4. Merge and deploy to production
5. Backport the fix to `develop`
6. Create regular bug fix branch for non-critical issues

## Tools and Automation

- **GitHub Actions**: CI/CD pipeline
- **Branch Protection**: Enforces rules defined above
- **Dependabot**: Automated dependency updates
- **CodeQL**: Security analysis

## Questions?

For questions about this branching strategy, please:
- Open an issue with the "question" label
- Contact the team lead
- Review this document regularly for updates
