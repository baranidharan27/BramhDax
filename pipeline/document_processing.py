import os
import logging
from concurrent.futures import ThreadPoolExecutor
from .pdf_processing import PdfProcessor
from .image_processing import ImageDescriptionGenerator

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
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from .pdf_processing import PdfProcessor
from .proximity_captioner import ProximityCaptioner  # Import the ProximityCaptioner
from .table_processing import TableProcessor

class DocumentProcessor:
    """Handles the entire document processing pipeline."""
    
    def __init__(self, output_base_dir, scale=2.0):
        self.output_base_dir = output_base_dir
        self.pdf_processor = PdfProcessor(scale)
        self.proximity_captioner = ProximityCaptioner()  # Use ProximityCaptioner instead of ImageDescriptionGenerator
        self.table_processor = TableProcessor(scale)  # Initialize TableProcessor
        self.logger = logging.getLogger(__name__)

    def process_pdf(self, pdf_path):
        """Process a single PDF file."""
        pdf_name = pdf_path.stem
        output_dir = os.path.join(self.output_base_dir, pdf_name)
        os.makedirs(output_dir, exist_ok=True)

        self.logger.info(f"Processing {pdf_path.name}...")
        conv_res = self.pdf_processor.process(pdf_path)

        if conv_res:
            # Extract images
            images_dir = os.path.join(output_dir, "images")
            images = self.pdf_processor.extract_images(conv_res, images_dir)

            # Extract tables and save them as text files
            tables_dir = os.path.join(output_dir, "tables")
            tables = self.table_processor.process(conv_res, tables_dir)  # Pass conversion result to TableProcessor

            # Generate final output with image descriptions and table details
            self.generate_final_output(images, tables, output_dir, conv_res)  # Pass conv_res for captioning

            self.logger.info(f"Finished processing {pdf_path.name}. Extracted {len(images)} images and {len(tables)} tables.")
        else:
            self.logger.error(f"Skipping {pdf_path.name} due to parsing error.")

    def generate_final_output(self, images, tables, output_dir, conv_res):
        """Generate the final output text file with image descriptions and table details."""
        output_text = ""

        # Use ProximityCaptioner to generate captions
        images_list = self.proximity_captioner.process(conv_res)  # Use ProximityCaptioner for caption extraction

        # Add descriptions for images
        for img in images_list:
            output_text += f"<image_{img['number']}>\n"
            output_text += f"Page {img['page']}\n"
            output_text += f"{{image_{img['number']}_description: {img['caption']}}}\n\n"

        # Add table details (linking to the text files)
        for idx, table_filename in enumerate(tables, start=1):
            output_text += f"<table_{idx}>\n"
            output_text += f"{{table_{idx}_text: {table_filename}}}\n\n"

        # Save the final output
        output_file_path = os.path.join(output_dir, "final_output.txt")
        try:
            with open(output_file_path, "w") as f:
                f.write(output_text)
            self.logger.info(f"Final output saved to {output_file_path}")
        except Exception as e:
            self.logger.error(f"Error saving final output text file: {e}")

    def process_batch(self, pdf_paths):
        """Process multiple PDF files in parallel."""
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_pdf, pdf_path) for pdf_path in pdf_paths]
            for future in futures:
                try:
                    future.result()  # Re-raises any exception caught inside the thread
                except Exception as e:
                    self.logger.error(f"Error processing PDF in batch: {e}")
