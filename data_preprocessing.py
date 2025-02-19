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



#code part

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
import logging
import concurrent.futures
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image


# Constants
IMAGE_RESOLUTION_SCALE = 2.0
OUTPUT_BASE_DIR = "./output"
LOG_FILE = "pipeline.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load pre-trained BLIP model for image captioning
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Helper functions
def generate_image_description(image_path):
    """Generate a detailed description for the given image using BLIP model."""
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        
        # Use the BLIP model to generate a description
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
        
        logging.info(f"Generated description for {image_path}: {description}")
        return description
    except Exception as e:
        logging.error(f"Error generating description for {image_path}: {e}")
        return "No description available"

def parse_pdf(pdf_path):
    """Parse the PDF and return the conversion result."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    try:
        start_time = time.time()
        conv_res = doc_converter.convert(pdf_path)
        end_time = time.time() - start_time
        logging.info(f"Parsed {pdf_path.name} in {end_time:.2f} seconds.")
        return conv_res
    except Exception as e:
        logging.error(f"Error parsing PDF {pdf_path.name}: {e}")
        return None

def extract_images(conv_res, output_dir):
    """Extract images and save them to the specified directory."""
    if not conv_res:
        logging.error("No conversion result found, skipping image extraction.")
        return []

    os.makedirs(output_dir, exist_ok=True)
    images_list = []
    image_number = 1

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, PictureItem):
            element_image_filename = os.path.join(output_dir, f"image_{image_number}.png")
            try:
                with open(element_image_filename, "wb") as fp:
                    image = element.get_image(conv_res.document)
                    image.save(fp, "PNG")
                images_list.append((element_image_filename, element.caption if hasattr(element, 'caption') else "No caption"))
                image_number += 1
            except Exception as e:
                logging.error(f"Error saving image {image_number}: {e}")
    return images_list

def extract_tables(conv_res, output_dir):
    """Extract tables and save them to the specified directory as text files."""
    if not conv_res:
        logging.error("No conversion result found, skipping table extraction.")
        return []

    os.makedirs(output_dir, exist_ok=True)
    table_number = 1
    table_list = []

    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            # Use export_to_dataframe() to get table content as DataFrame
            try:
                table_df = element.export_to_dataframe()  # This returns a Pandas DataFrame
                
                # Save the table as CSV
                table_csv_filename = os.path.join(output_dir, f"table_{table_number}.txt")
                table_df.to_csv(table_csv_filename, index=False)
                
                # Save the table as HTML
                table_html_filename = os.path.join(output_dir, f"table_{table_number}.html")
                table_df.to_html(table_html_filename, index=False)
                
                # Append to table_list
                table_list.append({
                    "txt": table_csv_filename,
                    "html": table_html_filename
                })
                
                table_number += 1
            except Exception as e:
                logging.error(f"Error saving table {table_number}: {e}")
    return table_list


def generate_final_output(images, tables, output_dir):
    """Generate the final output text file with image descriptions and table details."""
    output_text = ""

    # Add descriptions for images
    for idx, (image_path, _) in enumerate(images, start=1):
        description = generate_image_description(image_path)
        output_text += f"<image_{idx}>\n"
        output_text += f"{{image_{idx}_description: {description}}}\n\n"

    # Add table details (now linking only to the text files)
    for idx, table_filename in enumerate(tables, start=1):
        output_text += f"<table_{idx}>\n"
        output_text += f"{{table_{idx}_text: {table_filename}}}\n\n"

    # Save the final output
    output_file_path = os.path.join(output_dir, "final_output.txt")
    try:
        with open(output_file_path, "w") as f:
            f.write(output_text)
        logging.info(f"Final output saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving final output text file: {e}")

def process_pdf(pdf_path, output_base_dir):
    """Process a single PDF file."""
    pdf_name = pdf_path.stem
    output_dir = os.path.join(output_base_dir, pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    logging.info(f"Processing {pdf_path.name}...")
    conv_res = parse_pdf(pdf_path)

    if conv_res:
        # Extract images
        images_dir = os.path.join(output_dir, "images")
        images = extract_images(conv_res, images_dir)

        # Extract tables and save them as text files directly under the output directory
        tables_dir = output_dir  # Save tables directly under output_dir
        tables = extract_tables(conv_res, tables_dir)

        # Generate final output with image descriptions and table details
        generate_final_output(images, tables, output_dir)

        logging.info(f"Finished processing {pdf_path.name}. Extracted {len(images)} images and {len(tables)} tables.")
    else:
        logging.error(f"Skipping {pdf_path.name} due to parsing error.")

def process_pdf_batch(pdf_paths, output_base_dir):
    """Process multiple PDF files in parallel."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_pdf, pdf_path, output_base_dir) for pdf_path in pdf_paths]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Re-raises any exception caught inside the thread
            except Exception as e:
                logging.error(f"Error processing PDF in batch: {e}")

# Main script
if __name__ == "__main__":
    # Define input PDF paths (can be a single file or a list of files)
    pdf_paths = [Path("data/paper.pdf")]  # Add more PDFs as needed

    # Run the pipeline
    process_pdf_batch(pdf_paths, OUTPUT_BASE_DIR)
