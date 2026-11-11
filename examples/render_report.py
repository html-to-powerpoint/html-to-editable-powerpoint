import html
import os
from pathlib import Path

import requests

HOST = "html-to-editable-powerpoint.p.rapidapi.com"


def slide(title: str, subtitle: str):
    # Escape report values rather than inserting arbitrary text as HTML.
    return (
        "\u003c!doctype html\u003e\u003chtml\u003e\u003chead\u003e\u003cmeta charset='utf-8'\u003e\u003c/head\u003e"
        "\u003cbody style='margin:0;width:960px;height:540px;"
        "background:#f5f7fb;font-family:Arial'\u003e"
        "\u003ch1 style='position:absolute;left:70px;top:90px;margin:0;"
        "font-size:48px;color:#16324f'\u003e"
        + html.escape(title)
        + "\u003c/h1\u003e\u003cp style='position:absolute;left:70px;top:200px;margin:0;"
        "font-size:28px;color:#374151'\u003e"
        + html.escape(subtitle)
        + "\u003c/p\u003e\u003c/body\u003e\u003c/html\u003e"
    )


def render(slides: list[str], output_type: str, destination: Path):
    if output_type not in {"pptx", "pdf", "png", "jpeg"}:
        raise ValueError("Unsupported output type")
    if len(slides) not in range(1, 21):
        raise ValueError("Supply 1 to 20 slides")
    if output_type in {"png", "jpeg"} and len(slides) != 1:
        raise ValueError("Image exports require exactly one slide")

    response = requests.post(
        f"https://{HOST}/api/render",
        headers={
            "X-RapidAPI-Key": os.environ["RAPIDAPI_KEY"],
            "X-RapidAPI-Host": HOST,
        },
        json={
            "slides": slides,
            "title": "Monthly report",
            "type": output_type,
            "aspectRatio": "16:9",
        },
        timeout=(10, 190),
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Render failed: HTTP {response.status_code}; "
            f"Retry-After={response.headers.get('Retry-After', 'not supplied')}; "
            f"{response.text[:500]}"
        )

    signatures = {
        "pptx": b"PK\x03\x04",
        "pdf": b"%PDF-",
        "png": b"\x89PNG\r\n\x1a\n",
        "jpeg": b"\xff\xd8\xff",
    }
    if not response.content.startswith(signatures[output_type]):
        raise RuntimeError("Unexpected response: output signature did not match")

    destination.write_bytes(response.content)
    print(f"Saved {destination}: {len(response.content):,} bytes")
    for name in (
        "X-PPTXRenderer-Slide-Count",
        "X-RateLimit-Slides-Remaining",
        "X-RateLimit-Requests-Remaining",
    ):
        value = response.headers.get(name)
        if value is not None:
            print(f"{name}: {value}")


if __name__ == "__main__":
    deck = [
        slide("Monthly business review", "Example data for a sample report"),
        slide("Next steps", "Edit this text after opening the PowerPoint file"),
    ]
    render(deck, "pptx", Path("report.pptx"))
    # Optional: this is a separate two-slide conversion and uses more quota.
    # render(deck, "pdf", Path("report.pdf"))
