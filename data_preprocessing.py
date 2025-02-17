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
#code part for this file
import os
import time
import logging
from pathlib import Path
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Constants
IMAGE_RESOLUTION_SCALE = 2.0
OUTPUT_BASE_DIR = "./output"
LOG_FILE = "pipeline.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load pre-trained image captioning model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_image_description(image_path):
    """Generate a description for the given image using a pre-trained model."""
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokens=True)
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

def generate_final_output(images, output_dir):
    """Generate the final output text file with image descriptions."""
    output_text = ""
    for idx, (image_path, _) in enumerate(images, start=1):
        description = generate_image_description(image_path)
        output_text += f"<image_{idx}>\n"
        output_text += f"{{image_{idx}_description: {description}}}\n\n"

    output_file_path = os.path.join(output_dir, "final_output.txt")
    with open(output_file_path, "w") as f:
        f.write(output_text)
    logging.info(f"Final output saved to {output_file_path}")

def process_pdf(pdf_path, output_base_dir):
    """Process a single PDF file."""
    pdf_name = pdf_path.stem
    output_dir = os.path.join(output_base_dir, pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    logging.info(f"Processing {pdf_path.name}...")
    conv_res = parse_pdf(pdf_path)

    # Extract images
    images_dir = os.path.join(output_dir, "images")
    images = extract_images(conv_res, images_dir)

    # Generate final output with image descriptions
    generate_final_output(images, output_dir)

    logging.info(f"Finished processing {pdf_path.name}. Extracted {len(images)} images.")

def main(pdf_paths, output_base_dir):
    """Process multiple PDF files."""
    for pdf_path in pdf_paths:
        try:
            process_pdf(pdf_path, output_base_dir)
        except Exception as e:
            logging.error(f"Error processing {pdf_path.name}: {e}")

if __name__ == "__main__":
    # Define input PDF paths (can be a single file or a list of files)
    pdf_paths = [Path("paper.pdf")]  # Add more PDFs as needed

    # Run the pipeline
    main(pdf_paths, OUTPUT_BASE_DIR)