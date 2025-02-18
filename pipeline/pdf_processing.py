import os
import logging
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling_core.types.doc import PictureItem
from docling.document_converter import PdfFormatOption

# Importing necessary classes
from docling.datamodel.base_models import InputFormat  # Correct import for InputFormat
from docling_core.types.doc import PictureItem  # Correct import for PictureItem

class PdfProcessor:
    """Handles the parsing and processing of PDF files."""
    
    def __init__(self, scale=2.0):
        self.scale = scale
        self.logger = logging.getLogger(__name__)

    def parse_pdf(self, pdf_path):
        """Parse the PDF and return the conversion result."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.scale
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        doc_converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        try:
            conv_res = doc_converter.convert(pdf_path)
            self.logger.info(f"Parsed {pdf_path.name} successfully.")
            return conv_res
        except Exception as e:
            self.logger.error(f"Error parsing PDF {pdf_path.name}: {e}")
            return None

    def extract_images(self, conv_res, output_dir):
        """Extract images from conversion result and save them."""
        if not conv_res:
            self.logger.error("No conversion result found, skipping image extraction.")
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
                    self.logger.error(f"Error saving image {image_number}: {e}")
        return images_list
