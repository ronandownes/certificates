from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "certificates"
PUBLIC = ROOT / "public"
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
            f'''<article class="card">
  <a class="preview" href="{html.escape(item["file"])}" target="_blank" rel="noopener">{preview}</a>
  <div class="body">
    <h2>{html.escape(item["name"])}</h2>
    <p>{html.escape(item["kind"])}</p>
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
  <title>Certificates</title>
  <style>
    :root {{ color-scheme: light; --ink:#202124; --muted:#686b70; --line:#dadce0; --paper:#ffffff; --wash:#f7f7f5; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Georgia,'Times New Roman',serif; color:var(--ink); background:var(--wash); }}
    header {{ max-width:1180px; margin:0 auto; padding:52px 24px 24px; }}
    h1 {{ margin:0 0 8px; font-size:clamp(2.2rem,5vw,4.2rem); font-weight:500; letter-spacing:-.03em; }}
    header p {{ margin:0; color:var(--muted); font-family:Arial,sans-serif; }}
    main {{ max-width:1180px; margin:0 auto; padding:16px 24px 64px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:22px; }}
    .card {{ background:var(--paper); border:1px solid var(--line); border-radius:10px; overflow:hidden; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
    .preview {{ display:block; aspect-ratio:4/3; background:#efefec; border-bottom:1px solid var(--line); overflow:hidden; }}
    .preview img {{ width:100%; height:100%; object-fit:contain; display:block; background:white; }}
    .placeholder {{ height:100%; display:grid; place-items:center; color:var(--muted); font-family:Arial,sans-serif; font-weight:700; }}
    .body {{ padding:16px; }}
    h2 {{ margin:0 0 6px; font-size:1.18rem; line-height:1.25; font-weight:600; }}
    .body p {{ margin:0 0 14px; color:var(--muted); font:12px/1.4 Arial,sans-serif; letter-spacing:.08em; }}
    .actions {{ display:flex; gap:10px; font-family:Arial,sans-serif; }}
    .actions a {{ color:var(--ink); text-decoration:none; border:1px solid var(--line); border-radius:6px; padding:8px 11px; font-size:14px; }}
    .actions a:hover {{ background:#f2f2ef; }}
    .empty {{ padding:40px 0; color:var(--muted); }}
  </style>
</head>
<body>
  <header>
    <h1>Certificates</h1>
    <p>{count_text} · rebuilt automatically from the repository</p>
  </header>
  <main>
    {empty}
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
'''
    (PUBLIC / "index.html").write_text(page, encoding="utf-8")
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(items)} certificate card(s) into {PUBLIC}")


if __name__ == "__main__":
    build()
