# file: app/utils/markdown.py
import bleach
from markdown import markdown
from flask import current_app


def render_markdown(text):
    if not text:
        return ""

    allowed_tags = current_app.config.get(
        "BLEACH_ALLOWED_TAGS",
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "br",
            "hr",
            "ul",
            "ol",
            "li",
            "blockquote",
            "pre",
            "code",
            "a",
            "img",
            "strong",
            "em",
            "b",
            "i",
            "u",
            "s",
            "del",
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
        ],
    )

    allowed_attrs = current_app.config.get(
        "BLEACH_ALLOWED_ATTRS",
        {
            "a": ["href", "title", "target", "rel"],
            "img": ["src", "alt", "title", "width", "height"],
            "td": ["colspan", "rowspan"],
            "th": ["colspan", "rowspan"],
        },
    )

    html = markdown(
        text,
        extensions=current_app.config.get(
            "MARKDOWN_EXTENSIONS",
            ["extra", "codehilite", "toc", "tables", "fenced_code"],
        ),
    )

    html = bleach.linkify(html)

    html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    return html
