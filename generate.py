from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "certificates"
ASSETS = ROOT / "assets"
PUBLIC = ROOT / "public"
PUBLIC_ASSETS = PUBLIC / "assets"
FILES = PUBLIC / "files"
THUMBS = PUBLIC / "thumbnails"

SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def display_name(path: Path) -> str:
    name = path.stem.replace("_", " ").replace("-", " ")
    return " ".join(name.split()).strip().title()


def make_pdf_thumbnail(source: Path, destination: Path) -> bool:
    prefix = destination.with_suffix("")
    try:
        subprocess.run(
            ["pdftoppm", "-f", "1", "-singlefile", "-jpeg", "-r", "115", str(source), str(prefix)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        generated = prefix.with_suffix(".jpg")
        if generated.exists() and generated != destination:
            generated.replace(destination)
        return destination.exists()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def build() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    FILES.mkdir(parents=True)
    THUMBS.mkdir(parents=True)
    PUBLIC_ASSETS.mkdir(parents=True)

    logo = ASSETS / "certificates-logo.svg"
    if logo.exists():
        shutil.copy2(logo, PUBLIC_ASSETS / logo.name)

    items = []
    for source in sorted(SOURCE.iterdir(), key=lambda p: p.name.lower()):
        if not source.is_file() or source.name.startswith(".") or source.suffix.lower() not in SUPPORTED:
            continue

        target = FILES / source.name
        shutil.copy2(source, target)

        suffix = source.suffix.lower()
        thumb_rel = None
        if suffix == ".pdf":
            thumb_name = f"{source.stem}.jpg"
            thumb_path = THUMBS / thumb_name
            if make_pdf_thumbnail(source, thumb_path):
                thumb_rel = f"thumbnails/{thumb_name}"
        else:
            thumb_name = source.name
            shutil.copy2(source, THUMBS / thumb_name)
            thumb_rel = f"thumbnails/{thumb_name}"

        items.append(
            {
                "name": display_name(source),
                "file": f"files/{source.name}",
                "thumb": thumb_rel,
                "kind": suffix.lstrip(".").upper(),
            }
        )

    cards = []
    for item in items:
        if item["thumb"]:
            preview = (
                f'<img src="{html.escape(item["thumb"])}" '
                f'alt="Preview of {html.escape(item["name"])}" loading="lazy">'
            )
        else:
            preview = '<div class="placeholder">PDF</div>'

        cards.append(
            f'''<article class="certificate-card">
  <a class="preview" href="{html.escape(item["file"])}" target="_blank" rel="noopener">{preview}</a>
  <div class="card-body">
    <div class="file-type">{html.escape(item["kind"])}</div>
    <h2>{html.escape(item["name"])}</h2>
    <div class="actions">
      <a href="{html.escape(item["file"])}" target="_blank" rel="noopener">View</a>
      <a href="{html.escape(item["file"])}" download>Download</a>
    </div>
  </div>
</article>'''
        )

    empty = "" if items else '<p class="empty">No certificates have been added yet.</p>'
    count_text = f"{len(items)} document" + ("" if len(items) == 1 else "s")

    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Certificates | Ronan Downes</title>
  <style>
    :root {{
      color-scheme: light;
      --ink:#202124;
      --muted:#5f6368;
      --line:#dfe3e7;
      --paper:#ffffff;
      --wash:#f1f3f4;
      --blue:#174ea6;
      --blue-soft:#e8f0fe;
    }}
    * {{ box-sizing:border-box; }}
    html {{ background:var(--wash); }}
    body {{ margin:0; font-family:Arial,Helvetica,sans-serif; color:var(--ink); background:var(--wash); }}
    .site-header {{ position:sticky; top:0; z-index:10; background:#fff; border-bottom:1px solid var(--line); }}
    .header-inner {{ max-width:1320px; min-height:86px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; justify-content:space-between; gap:24px; }}
    .brand img {{ display:block; width:220px; max-width:48vw; height:auto; }}
    .top-nav {{ display:flex; align-items:stretch; align-self:stretch; }}
    .top-nav a {{ display:flex; align-items:center; padding:0 18px; border-bottom:3px solid #5f6368; color:var(--ink); text-decoration:none; font-weight:700; font-size:14px; }}
    .page-wrap {{ max-width:1060px; margin:28px auto 70px; padding:0 18px; }}
    .sheet {{ background:var(--paper); border:1px solid var(--line); box-shadow:0 1px 3px rgba(60,64,67,.10); padding:48px 58px 58px; }}
    .eyebrow {{ margin:0 0 10px; color:#69757f; font-size:12px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; }}
    h1 {{ margin:0; font-size:clamp(2rem,4.5vw,3.25rem); line-height:1.06; letter-spacing:-.025em; }}
    .intro {{ margin:14px 0 0; max-width:720px; color:var(--muted); font-size:16px; line-height:1.6; }}
    .rule {{ margin:30px 0 24px; border:0; border-top:1px solid #eceff1; }}
    .catalogue-head {{ display:flex; justify-content:space-between; gap:20px; align-items:end; margin-bottom:18px; }}
    .catalogue-head h2 {{ margin:0; font-size:20px; }}
    .count {{ color:var(--muted); font-size:13px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:20px; }}
    .certificate-card {{ border:1px solid var(--line); background:#fff; overflow:hidden; transition:box-shadow .15s ease, transform .15s ease; }}
    .certificate-card:hover {{ box-shadow:0 4px 14px rgba(60,64,67,.14); transform:translateY(-1px); }}
    .preview {{ display:block; aspect-ratio:4/3; background:#f8f9fa; border-bottom:1px solid var(--line); overflow:hidden; }}
    .preview img {{ width:100%; height:100%; object-fit:contain; display:block; background:#fff; }}
    .placeholder {{ height:100%; display:grid; place-items:center; color:#8a9298; font-weight:700; }}
    .card-body {{ padding:16px; }}
    .file-type {{ color:#6a737d; font-size:11px; font-weight:700; letter-spacing:.1em; margin-bottom:7px; }}
    .card-body h2 {{ margin:0 0 14px; font-size:17px; line-height:1.35; }}
    .actions {{ display:flex; gap:8px; flex-wrap:wrap; }}
    .actions a {{ color:var(--blue); background:#fff; text-decoration:none; border:1px solid #c9d5e6; border-radius:3px; padding:7px 11px; font-size:13px; font-weight:700; }}
    .actions a:hover {{ background:var(--blue-soft); }}
    .empty {{ margin:8px 0 0; padding:34px; background:#f8f9fa; border:1px dashed #cfd5da; color:var(--muted); text-align:center; }}
    footer {{ max-width:1060px; margin:0 auto 34px; padding:0 18px; color:#7a8085; font-size:12px; }}
    @media (max-width:700px) {{
      .header-inner {{ min-height:72px; padding:8px 14px; }}
      .brand img {{ width:190px; max-width:65vw; }}
      .top-nav a {{ padding:0 10px; font-size:13px; }}
      .page-wrap {{ margin-top:16px; padding:0 10px; }}
      .sheet {{ padding:32px 22px 38px; }}
      .catalogue-head {{ align-items:start; flex-direction:column; gap:4px; }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="./" aria-label="Ronan Downes Certificates home">
        <img src="assets/certificates-logo.svg" alt="Ronan Downes Certificates">
      </a>
      <nav class="top-nav" aria-label="Primary">
        <a href="./">Certificates</a>
      </nav>
    </div>
  </header>

  <main class="page-wrap">
    <section class="sheet">
      <p class="eyebrow">Professional Records</p>
      <h1>Certificates</h1>
      <p class="intro">Professional qualifications, degrees, diplomas, registrations and supporting documents.</p>
      <hr class="rule">
      <div class="catalogue-head">
        <h2>Documents</h2>
        <div class="count">{count_text} · rebuilt automatically</div>
      </div>
      {empty}
      <section class="grid" aria-label="Certificate documents">
        {''.join(cards)}
      </section>
    </section>
  </main>

  <footer>Ronan Downes · Certificates</footer>
</body>
</html>
'''
    (PUBLIC / "index.html").write_text(page, encoding="utf-8")
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(items)} certificate card(s) into {PUBLIC}")


if __name__ == "__main__":
    build()
