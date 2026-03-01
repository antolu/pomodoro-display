#!/usr/bin/env python3
"""
Download CDN dependencies for offline use
Run this script when you have internet access to cache dependencies locally
"""

from __future__ import annotations

import urllib.request
from pathlib import Path


def download_file(url: str, destination: Path) -> None:
    """Download a file from URL to destination"""
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            print(f"✓ Saved to {destination}")
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")


def main() -> None:
    """Download all CDN dependencies"""
    base_dir = Path(__file__).parent / "pomodoro_display" / "static"

    dependencies = {
        "js/alpine.min.js": "https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js",
        "js/tailwind.min.js": "https://cdn.tailwindcss.com/3.4.1",
    }

    print("Downloading CDN dependencies for offline use...\n")

    for dest_path, url in dependencies.items():
        destination = base_dir / dest_path
        download_file(url, destination)

    print("\n" + "=" * 60)
    print("✓ Download complete!")
    print("=" * 60)
    print("\nFiles saved to:")
    for dest_path in dependencies:
        print(f"  - static/{dest_path}")

    print("\nNote: Google Fonts (Inter) will still require internet access")
    print("or you can download them separately using google-webfonts-helper:")
    print("  https://gwfh.mranftl.com/fonts/inter")


if __name__ == "__main__":
    main()
