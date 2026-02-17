# file: app/cli.py
import click
from app import create_app
from app.extensions import db
from app.models import User


@click.group()
def cli():
    """Support Notes KB CLI commands."""
    pass


@cli.command("create-admin")
@click.option("--email", required=True, help="Admin email address")
@click.option("--name", required=True, help="Admin display name")
@click.option("--password", required=True, help="Admin password")
def create_admin(email, name, password):
    """Create or update an admin user."""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if user:
            user.display_name = name
            user.set_password(password)
            user.is_admin = True
            user.is_active = True
            click.echo(f"Updated existing user: {email}")
        else:
            user = User(email=email, display_name=name, is_admin=True, is_active=True)
            user.set_password(password)
            db.session.add(user)
            click.echo(f"Created new admin user: {email}")

        db.session.commit()


@cli.command("import-files")
@click.option("--path", required=True, help="Directory containing .txt and .md files")
@click.option(
    "--tag-from-folders", is_flag=True, help="Create tags from parent folder names"
)
@click.option("--default-tags", default="", help="Comma-separated default tags")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be imported without saving"
)
def import_files(path, tag_from_folders, default_tags, dry_run):
    """Import .txt and .md files as notes."""
    from importers.import_files import import_files as do_import

    ctx = click.Context(do_import)
    ctx.invoke(
        do_import,
        path=path,
        tag_from_folders=tag_from_folders,
        default_tags=default_tags,
        dry_run=dry_run,
        user_id=None,
    )


@cli.command("import-onenote")
@click.option("--path", required=True, help="Directory containing .html files")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be imported without saving"
)
def import_onenote(path, dry_run):
    """Import OneNote HTML exports as notes."""
    from importers.import_onenote_html import import_onenote as do_import

    ctx = click.Context(do_import)
    ctx.invoke(do_import, path=path, dry_run=dry_run, user_id=None)


if __name__ == "__main__":
    cli()
