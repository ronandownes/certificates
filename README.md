# Certificates

This repository is designed to be almost maintenance-free.

## Normal workflow

1. Put certificate files in the `certificates/` folder.
2. Commit the change.
3. GitHub Actions rebuilds the website automatically.
4. GitHub Pages publishes the updated site.

Supported source files: PDF, PNG, JPG, JPEG and WEBP.

For PDFs, the first page is automatically converted into a thumbnail. Clicking a card opens the full document and each card also has a Download button.

## File naming

The website title is generated from the filename.

Examples:

- `msc-data-analytics-cct-2025.pdf` → `Msc Data Analytics Cct 2025`
- `higher_diploma_education.pdf` → `Higher Diploma Education`

Use clear kebab-case or snake_case filenames. The original file remains downloadable under that filename.

## Repository structure

```text
certificates/
├── certificates/              # only source documents go here
├── generate.py                # builds the website
├── .github/
│   └── workflows/
│       └── build-site.yml     # rebuilds and publishes automatically
└── README.md
```

The generated `public/` directory does not need to be maintained by hand. It is created during each build.

## One-time GitHub Pages setting

In GitHub open **Settings → Pages** and set the source to **GitHub Actions** if it is not already selected.

After that, the normal job is simply: add or remove files from `certificates/` and commit.
