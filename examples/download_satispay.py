#!/usr/bin/env python
"""
Download the Satispay "Open Positions" page both as raw HTML and as
clean Markdown, saving everything inside the local ./output directory.
"""

from pathlib import Path

from url2md4ai import ContentExtractor, Config


def main() -> None:
    """Run the extraction workflow for the Satispay careers page."""
    url = "https://www.satispay.com/en-it/work-at-satispay/open-positions/"

    # 1️⃣ Ensure the output directory exists
    output_dir = Path("output")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Quick write test to ensure permission
        test_file = output_dir / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
    except (PermissionError, OSError):
        # Fallback to a directory in the user's home if not writable
        fallback = Path.home() / "url2md_output"
        fallback.mkdir(parents=True, exist_ok=True)
        print(f"⚠️  Directory '{output_dir}' is not writable. Falling back to '{fallback}'.")
        output_dir = fallback

    # 2️⃣ Initialise the extractor with custom options
    #    - human-readable filenames (instead of hash)
    #    - filter out cookie/legal boiler-plate lines
    config = Config(
        output_dir=str(output_dir),
        use_hash_filenames=False,
        drop_phrases=[
            "cookie policy",
            "Payment services are provided",
            "Corporate welfare services are provided",
            "Investment services are provided",
        ],
    )
    extractor = ContentExtractor(config=config)

    # 3️⃣ Extract Markdown (this also returns the raw HTML)
    result = extractor.extract_markdown_sync(url)
    if result is None:
        raise RuntimeError("Extraction failed – check the URL or network connection")

    # 4️⃣ Save the raw HTML with the same base name as the markdown
    md_path = Path(result["output_path"])
    html_path = md_path.with_suffix(".html")
    html_path.write_text(result["html_content"], encoding="utf-8")

    print("✅ HTML saved to :", html_path)
    print("✅ Markdown saved:", md_path)


if __name__ == "__main__":
    main() 