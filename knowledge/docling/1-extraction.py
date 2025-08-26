from docling.document_converter import DocumentConverter
from utils.sitemap import get_sitemap_urls

converter = DocumentConverter()

# --------------------------------------------------------------
# Basic PDF extraction from local file
# --------------------------------------------------------------

# Use the local KFH Real Estate Report PDF
result = converter.convert("KFH_Real_Estate_Report_2025_Q1.pdf")

document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()

print("Extracted PDF content:")
print("=" * 50)
print(markdown_output[:1000] + "..." if len(markdown_output) > 1000 else markdown_output)
print("=" * 50)

# --------------------------------------------------------------
# Basic HTML extraction (keeping for reference)
# --------------------------------------------------------------

# result = converter.convert("https://ds4sd.github.io/docling/")
# document = result.document
# markdown_output = document.export_to_markdown()
# print(markdown_output)

# --------------------------------------------------------------
# Scrape multiple pages using the sitemap (keeping for reference)
# --------------------------------------------------------------

# sitemap_urls = get_sitemap_urls("https://ds4sd.github.io/docling/")
# conv_results_iter = converter.convert_all(sitemap_urls)

# docs = []
# for result in conv_results_iter:
#     if result.document:
#         document = result.document
#         docs.append(document)
