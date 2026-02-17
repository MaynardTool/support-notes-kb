# file: importers/import_files.py
import os
import sys
import click
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Note, Tag


@click.command()
@click.option("--path", required=True, help="Directory containing .txt and .md files")
@click.option(
    "--tag-from-folders", is_flag=True, help="Create tags from parent folder names"
)
@click.option("--default-tags", default="", help="Comma-separated default tags")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be imported without saving"
)
@click.option(
    "--user-id",
    default=None,
    help="User ID to set as creator (defaults to first admin)",
)
def import_files(path, tag_from_folders, default_tags, dry_run, user_id):
    """Import .txt and .md files from a directory as notes."""

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

        default_tag_list = [
            t.strip().lower() for t in default_tags.split(",") if t.strip()
        ]

        files_processed = 0
        files_created = 0
        files_updated = 0
        files_skipped = 0

        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            folder_tags = []
            if tag_from_folders:
                relative_parts = root_path.relative_to(path_obj).parts
                folder_tags = [p.lower() for p in relative_parts if p != "."]

            for filename in files:
                if not filename.endswith((".txt", ".md")):
                    continue

                file_path = root_path / filename
                full_path = str(file_path.resolve())

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    click.echo(f"Warning: Could not read {file_path}: {e}", err=True)
                    continue

                title = file_path.stem

                existing_note = Note.query.filter_by(source=full_path).first()

                if existing_note:
                    if dry_run:
                        click.echo(f"[DRY RUN] Would update: {title} ({full_path})")
                        files_updated += 1
                    else:
                        existing_note.title = title
                        existing_note.body = content
                        existing_note.updated_by_id = user.id
                        existing_note.updated_at = datetime.now(timezone.utc)

                        existing_note.tags.clear()
                        all_tags = folder_tags + default_tag_list
                        for tag_name in set(all_tags):
                            tag = Tag.get_or_create(tag_name)
                            if tag:
                                existing_note.tags.append(tag)

                        files_updated += 1
                        click.echo(f"Updated: {title}")
                else:
                    if dry_run:
                        click.echo(f"[DRY RUN] Would create: {title} ({full_path})")
                        files_created += 1
                    else:
                        note = Note(
                            title=title,
                            body=content,
                            source=full_path,
                            created_by_id=user.id,
                            updated_by_id=user.id,
                        )

                        all_tags = folder_tags + default_tag_list
                        for tag_name in set(all_tags):
                            tag = Tag.get_or_create(tag_name)
                            if tag:
                                note.tags.append(tag)

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
        click.echo(f"  Skipped: {files_skipped}")


if __name__ == "__main__":
    import_files()
