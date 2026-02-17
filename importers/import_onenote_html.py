# file: importers/import_onenote_html.py
import os
import sys
import click
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from markdownify import markdownify as md
except ImportError:
    md = None

from app import create_app
from app.extensions import db
from app.models import Note, Tag


@click.command()
@click.option("--path", required=True, help="Directory containing .html files")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be imported without saving"
)
@click.option(
    "--user-id",
    default=None,
    help="User ID to set as creator (defaults to first admin)",
)
def import_onenote(path, dry_run, user_id):
    """Import .html files (e.g., OneNote exported HTML) as notes."""

    if md is None:
        click.echo(
            "Error: markdownify not installed. Run: pip install markdownify", err=True
        )
        sys.exit(1)

    app = create_app()

    with app.app_context():
        user = None
        if user_id:
            from app.models import User

            user = User.query.get(user_id)
        else:
            from app.models import User

            user = User.query.filter_by(is_admin=True).first()

        if not user:
            click.echo(
                "Error: No user found. Please provide --user-id or create an admin user first.",
                err=True,
            )
            sys.exit(1)

        path_obj = Path(path)
        if not path_obj.exists():
            click.echo(f"Error: Path does not exist: {path}", err=True)
            sys.exit(1)

        files_processed = 0
        files_created = 0
        files_updated = 0

        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            for filename in files:
                if not filename.endswith(".html"):
                    continue

                file_path = root_path / filename
                full_path = str(file_path.resolve())

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                except Exception as e:
                    click.echo(f"Warning: Could not read {file_path}: {e}", err=True)
                    continue

                import re

                title_match = re.search(
                    r"<title>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL
                )
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = file_path.stem

                try:
                    markdown_content = md(html_content)
                    markdown_content = markdown_content.strip()
                except Exception as e:
                    click.echo(f"Warning: Could not convert {file_path}: {e}", err=True)
                    continue

                existing_note = Note.query.filter_by(source=full_path).first()

                if existing_note:
                    if dry_run:
                        click.echo(f"[DRY RUN] Would update: {title} ({full_path})")
                        files_updated += 1
                    else:
                        existing_note.title = title
                        existing_note.body = markdown_content
                        existing_note.updated_by_id = user.id
                        existing_note.updated_at = datetime.now(timezone.utc)

                        files_updated += 1
                        click.echo(f"Updated: {title}")
                else:
                    if dry_run:
                        click.echo(f"[DRY RUN] Would create: {title} ({full_path})")
                        files_created += 1
                    else:
                        note = Note(
                            title=title,
                            body=markdown_content,
                            source=full_path,
                            created_by_id=user.id,
                            updated_by_id=user.id,
                        )

                        db.session.add(note)
                        files_created += 1
                        click.echo(f"Created: {title}")

                files_processed += 1

        if not dry_run:
            db.session.commit()

        click.echo(f"\nSummary:")
        click.echo(f"  Files processed: {files_processed}")
        click.echo(f"  Created: {files_created}")
        click.echo(f"  Updated: {files_updated}")


if __name__ == "__main__":
    import_onenote()
