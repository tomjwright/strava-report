# Branch Strategy

This project uses a **Main + Develop** branch strategy for CI/CD and deployment.

## Branch Structure

- **main**: Production-ready code. Deployments to production environment.
- **develop**: Development branch. Deployments to preview/staging environment.
- **feature branches**: (Optional) For specific features, merged into develop.

## Workflow

1. **Development**: Work on `develop` branch or create feature branches from `develop`
2. **Testing**: CI/CD pipeline runs tests and linting on all branches
3. **Preview**: `develop` branch deploys to Vercel preview environment
4. **Production**: Merge `develop` → `main` deploys to Vercel production environment

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:

1. **Tests**: Runs pytest test suite
2. **Linting**: Runs flake8 for code quality
3. **Deployment**: 
   - `develop` branch → Vercel preview environment
   - `main` branch → Vercel production environment

## Deployment Rules

- All commits to `main` and `develop` must pass tests and linting
- Production deployments only happen from `main` branch
- Preview deployments happen from `develop` branch
- Use pull requests to merge `develop` → `main`

## Getting Started

```bash
# For development work
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/your-feature-name

# After completing work
git add .
git commit -m "Your changes"
git push origin feature/your-feature-name

# Create PR to merge into develop
```