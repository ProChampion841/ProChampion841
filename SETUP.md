# Installation and Launch Checklist

This package is designed for the public GitHub profile repository:

```text
ProChampion841/ProChampion841
```

GitHub displays a profile README when the public repository name matches the account username and `README.md` is in the repository root.

## 1. Copy the package into the profile repository

Preserve this structure:

```text
README.md
SETUP.md
assets/
  brandon-3d-banner.gif
  brandon-3d-banner.png
.github/
  workflows/
    profile-3d.yml
    snake.yml
tools/
  generate_banner.py
```

Example:

```bash
git clone https://github.com/ProChampion841/ProChampion841.git
cd ProChampion841
# Copy the package contents into this directory.
git add README.md SETUP.md assets .github tools
git commit -m "feat: redesign GitHub profile"
git push origin main
```

## 2. Generate the live 3D contribution map

1. Open the repository's **Actions** tab.
2. Select **Generate 3D contribution graph**.
3. Choose **Run workflow**.
4. Wait for the workflow to commit the `profile-3d-contrib/` directory.

The README uses:

```text
profile-3d-contrib/profile-night-rainbow.svg
```

The workflow refreshes it daily.

## 3. Generate the contribution snake

1. Open **Actions**.
2. Select **Generate contribution snake**.
3. Choose **Run workflow**.
4. Confirm that an `output` branch is created.

The README automatically chooses the light or dark animation based on the visitor's GitHub theme.

## 4. Fix workflow permissions only when needed

The workflows request `contents: write`. If a run fails with a permission or push error:

1. Open **Settings → Actions → General**.
2. Under **Workflow permissions**, allow read and write access.
3. Re-run the failed workflow.

Organization-level policy can override repository settings.

## 5. Profile SEO and discovery checklist

The README already includes keyword-rich, readable content for agentic AI, LLM engineering, RAG, OCR, document intelligence, computer vision, full-stack development, cloud architecture, DevOps, and automation. Complete the surrounding GitHub metadata as well:

- Keep the GitHub bio aligned with the first headline in the README.
- Pin the four repositories listed under **Featured Engineering Work**.
- Add concise repository descriptions, websites, and relevant topics to every featured project.
- Use descriptive README titles and image alt text inside each project repository.
- Keep portfolio and LinkedIn URLs current.
- Replace delivery metrics immediately if their underlying measurement changes.

## 6. Optional banner regeneration

The animated hero is already generated and optimized. To create a new version after changing the source script:

```bash
python tools/generate_banner.py
```

The script requires Pillow. ImageMagick can be used afterward for additional GIF optimization:

```bash
magick assets/brandon-3d-banner.gif -coalesce -fuzz 3% \
  -layers OptimizeTransparency -colors 128 -layers OptimizePlus \
  assets/brandon-3d-banner-optimized.gif
```

Replace the original GIF with the optimized file after reviewing it.

## 7. Reliability note for dynamic cards

The typing effect, Shields badges, and GitHub statistics are externally rendered images. The local 3D banner remains available even when an external card service is temporarily unavailable. For mission-critical statistics, self-host the card generator or replace the cards with workflow-generated assets committed to this repository.
