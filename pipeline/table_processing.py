import os
import logging
import pandas as pd
from pathlib import Path
from .base import PipelineComponent
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend

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

# Import necessary libraries
import os
import time
import logging
from pathlib import Path
from PIL import Image
from IPython.display import display
import requests
import pandas as pd
import matplotlib.pyplot as plt
import concurrent.futures
from transformers import BlipProcessor, BlipForConditionalGeneration
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.document_converter import DocumentConverter
from docling.document_converter import PdfFormatOption
from docling_core.types.doc import PictureItem
from docling.datamodel.pipeline_options import PdfPipelineOptions
import math



class TableProcessor(PipelineComponent):
    """Handles the extraction of tables from a PDF file."""
    
    def __init__(self, scale=2.0):
        super().__init__(name="TableProcessor")
        self.scale = scale
        self.logger = logging.getLogger(__name__)

    def process(self, pdf_path):
        """Extract tables from a PDF and save them as images, CSVs, and HTMLs."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.scale
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = False  # Disable image generation for non-table content
        
        doc_converter = DocumentConverter(format_options={InputFormat.PDF: pipeline_options})

        try:
            conv_res = doc_converter.convert(pdf_path)
            self.logger.info(f"Successfully parsed {pdf_path.name} for tables.")
            
            # Directories for saving table outputs
            table_output_dir = Path(f"./tables/{pdf_path.stem}")
            os.makedirs(table_output_dir, exist_ok=True)
            os.makedirs(table_output_dir / "images", exist_ok=True)
            os.makedirs(table_output_dir / "CSVs", exist_ok=True)
            os.makedirs(table_output_dir / "HTMLs", exist_ok=True)

            table_number = 1

            # Iterate over the PDF document items to find TableItems
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    # Save tables as images
                    table_image_filename = table_output_dir / "images" / f"table_{table_number}.png"
                    with open(table_image_filename, "wb") as fp:
                        table_image = element.get_image(conv_res.document)
                        table_image.save(fp, "PNG")
                    self.logger.info(f"Table {table_number} image saved: {table_image_filename}")

                    # Save tables as CSV files
                    table_df: pd.DataFrame = element.export_to_dataframe()
                    table_csv_filename = table_output_dir / "CSVs" / f"table_{table_number}.csv"
                    table_df.to_csv(table_csv_filename)
                    self.logger.info(f"Table {table_number} CSV saved: {table_csv_filename}")

                    # Save tables as HTML files
                    table_html = element.export_to_html()
                    table_html_filename = table_output_dir / "HTMLs" / f"table_{table_number}.html"
                    with open(table_html_filename, "w") as fp:
                        fp.write(table_html)
                    self.logger.info(f"Table {table_number} HTML saved: {table_html_filename}")

                    table_number += 1

        except Exception as e:
            self.logger.error(f"Error processing tables in {pdf_path.name}: {e}")
