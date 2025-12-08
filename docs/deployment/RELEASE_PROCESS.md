# Release Process Guide 🚀

This document serves as a manual for releasing new versions of the Patient Triage System. As we are learning, we will perform these steps manually to understand the lifecycle of a software release.

---

## 1. Understanding Versioning (SemVer)

We use **Semantic Versioning** (SemVer), which looks like `MAJOR.MINOR.PATCH` (e.g., `1.2.3`).

-   **MAJOR**: When you make incompatible API changes (breaking changes).
-   **MINOR**: When you add functionality in a backward compatible manner (new features).
-   **PATCH**: When you make backward compatible bug fixes.

**Example:**
-   Current: `0.1.0`
-   Bug fix? → `0.1.1`
-   New feature? → `0.2.0`
-   Breaking change? → `1.0.0`

---

## 2. Pre-Release Checklist

Before starting a release, ensure:
1.  [ ] You are on the `main` branch.
2.  [ ] Your git working directory is clean (`git status` shows no changes).
3.  [ ] All tests are passing locally (`pdm run test`).
4.  [ ] You have pulled the latest changes (`git pull origin main`).

---

## 3. The Release Steps

### Step 1: Update the Version Number
Open `pyproject.toml` and find the `version` key under `[project]`. Update it to your new target version.

```toml
[project]
name = "patient-triage-system"
version = "0.1.0"  # <--- Change this
```

### Step 2: Update the Changelog
Open `CHANGELOG.md`.
-   Move "Unreleased" changes into a new section for your version.
-   Add the current date.

Example:
```markdown
## [0.1.0] - 2025-12-08
### Added
- Initial release of Phase 1...
```

### Step 3: Commit the Changes
Create a specific commit just for the release. This helps keep history clean.

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.1.0"
```

### Step 4: Create a Git Tag
A **Tag** is like a sticky note on a specific commit in history. It tells deployment tools "This exact point in history is version 0.1.0".

```bash
# -a creates an annotated tag (stores who made it and when)
# -m is the message for the tag
git tag -a v0.1.0 -m "Release v0.1.0: Phase 1 Complete"
```

### Step 5: Push to GitHub
Pushing the tag is what usually triggers deployment pipelines (CI/CD).

```bash
# Push the commit
git push origin main

# Push the tag
git push origin v0.1.0
```

---

## 4. What Happens Next?

Once you push the tag:
1.  GitHub Actions detects the tag starting with `v`.
2.  It triggers the `deploy.yml` workflow.
3.  It builds the Docker images.
4.  It pushes them to the Container Registry with your tag (e.g., `backend:v0.1.0`).

---

## 5. Verification

After pushing, go to GitHub:
1.  Check the **Actions** tab to see the build running.
2.  Once green, check the **Packages** section on the main page to see your new container image.
