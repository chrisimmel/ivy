from urllib.parse import urlparse

import html2text
import httpx


def is_url(string: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def get_markdown_from_web_page(
    url: str, ignore_links: bool = True, ignore_images: bool = True, timeout: int = 20
) -> str | None:
    """Convert HTML from a URL to nicely formatted markdown (async version).

    Args:
        url: The URL to fetch and convert
        ignore_links: If True, don't include links in the markdown output
        ignore_images: If True, don't include images in the markdown output
        timeout: Request timeout in seconds

    Returns:
        Markdown string or None if conversion failed
    """
    # Fetch the HTML with proper headers using httpx
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        # Configure the converter
        h = html2text.HTML2Text()
        h.ignore_links = ignore_links
        h.ignore_images = ignore_images
        h.body_width = 0  # Don't wrap lines
        h.unicode_snob = True
        h.bypass_tables = False
        h.ignore_emphasis = False  # Keep bold/italic formatting
        h.mark_code = True  # Mark code blocks

        # Convert and clean up
        markdown = h.handle(response.text)
        return markdown.strip()
