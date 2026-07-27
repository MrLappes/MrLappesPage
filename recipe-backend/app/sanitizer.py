"""Server-side HTML sanitisation and slug helpers.

All rich text from the admin editor is sanitised here before it is stored, so
even the trusted admin cannot persist XSS that would later render to visitors.
"""
import re
import unicodedata

import nh3

ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "strike",
    "h1", "h2", "h3", "h4", "ul", "ol", "li", "blockquote",
    "a", "code", "pre", "hr", "span",
}

ALLOWED_ATTRIBUTES = {
    # "rel" is managed automatically by link_rel below, so it must not be listed here.
    "a": {"href", "title", "target"},
    "span": {"class"},
    "code": {"class"},
}


def sanitize_html(html: str) -> str:
    if not html:
        return ""
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
    )


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "item"
