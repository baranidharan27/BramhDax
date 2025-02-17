# docling
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter
from docling.document_converter import PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
# other support libraries
import time
import requests
from pathlib import Path
from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import time
import logging
from pathlib import Path
import pandas as pd
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption

# Constants
IMAGE_RESOLUTION_SCALE = 2.0
OUTPUT_BASE_DIR = "./output"
LOG_FILE = "pipeline.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_pdf(pdf_path):
    """Parse the PDF and return the conversion result."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_res = doc_converter.convert(pdf_path)
    end_time = time.time() - start_time
    logging.info(f"Parsed {pdf_path.name} in {end_time:.2f} seconds.")
    return conv_res

def extract_images(conv_res, output_dir):
    """Extract images and save them to the specified directory."""
    os.makedirs(output_dir, exist_ok=True)
    images_list = []
    image_number = 1

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, PictureItem):
            element_image_filename = os.path.join(output_dir, f"image_{image_number}.png")
            with open(element_image_filename, "wb") as fp:
                image = element.get_image(conv_res.document)
                image.save(fp, "PNG")
            images_list.append((element_image_filename, element.caption if hasattr(element, 'caption') else "No caption"))
            image_number += 1
    return images_list

def extract_tables(conv_res, output_dir):
    """Extract tables and save them as images, CSVs, and HTMLs."""
    os.makedirs(output_dir, exist_ok=True)
    table_list = []
    table_number = 1

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            # Save table as image
            element_table_filename = os.path.join(output_dir, f"table_{table_number}.png")
            with open(element_table_filename, "wb") as fp:
                table_image = element.get_image(conv_res.document)
                table_image.save(fp, "PNG")
                table_list.append(table_image)

            # Save table as CSV
            table_df = element.export_to_dataframe()
            element_table_filename = os.path.join(output_dir, f"table_{table_number}.csv")
            table_df.to_csv(element_table_filename)

            # Save table as HTML
            table_html = element.export_to_html()
            element_table_filename = os.path.join(output_dir, f"table_{table_number}.html")
            with open(element_table_filename, "w") as fp:
                fp.write(table_html)

            table_number += 1
    return table_list

def generate_structured_output(images, tables, output_dir):
    """Generate structured output with image-caption pairs and table references."""
    structured_output_path = os.path.join(output_dir, "structured_output.txt")
    with open(structured_output_path, "w") as f:
        f.write("Structured Output\n")
        f.write("================\n\n")
        f.write("Images:\n")
        for idx, (image_path, caption) in enumerate(images, start=1):
            f.write(f"Image {idx}:\n")
            f.write(f"  Path: {image_path}\n")
            f.write(f"  Caption: {caption}\n\n")
        f.write("\nTables:\n")
        for idx, table_image in enumerate(tables, start=1):
            f.write(f"Table {idx}:\n")
            f.write(f"  Image: {os.path.join(output_dir, f'table_{idx}.png')}\n")
            f.write(f"  CSV: {os.path.join(output_dir, f'table_{idx}.csv')}\n")
            f.write(f"  HTML: {os.path.join(output_dir, f'table_{idx}.html')}\n\n")

def process_pdf(pdf_path, output_base_dir):
    """Process a single PDF file."""
    pdf_name = pdf_path.stem
    output_dir = os.path.join(output_base_dir, pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    logging.info(f"Processing {pdf_path.name}...")
    conv_res = parse_pdf(pdf_path)

    # Extract images and captions
    images_dir = os.path.join(output_dir, "images")
    images = extract_images(conv_res, images_dir)

    # Extract tables
    tables_dir = os.path.join(output_dir, "tables")
    tables = extract_tables(conv_res, tables_dir)

    # Generate structured output
    generate_structured_output(images, tables, output_dir)

    logging.info(f"Finished processing {pdf_path.name}. Extracted {len(images)} images and {len(tables)} tables.")

def main(pdf_paths, output_base_dir):
    """Process multiple PDF files."""
    for pdf_path in pdf_paths:
        try:
            process_pdf(pdf_path, output_base_dir)
        except Exception as e:
            logging.error(f"Error processing {pdf_path.name}: {e}")

if __name__ == "__main__":
    # Define input PDF paths (can be a single file or a list of files)
    pdf_paths = [Path("2502.10322v1.pdf")]  # Add more PDFs as needed

    # Run the pipeline
    main(pdf_paths, OUTPUT_BASE_DIR)