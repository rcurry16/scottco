"""Extract PSC EC Grade Matrix from PDF for analysis."""
import pdfplumber
import json

pdf_path = "Rationale Docs/PSC EC Grade Matrix Draft (2018).pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    print("=" * 80)

    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i+1} ---")
        text = page.extract_text()
        print(text)
        print("\n" + "=" * 80)

        # Extract tables if present
        tables = page.extract_tables()
        if tables:
            print(f"\nFound {len(tables)} table(s) on page {i+1}")
            for j, table in enumerate(tables):
                print(f"\nTable {j+1}:")
                for row in table[:5]:  # Show first 5 rows
                    print(row)
                if len(table) > 5:
                    print(f"... ({len(table)} total rows)")
