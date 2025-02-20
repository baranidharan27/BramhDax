import os
import logging
from pathlib import Path
import pandas as pd
from .base import PipelineComponent
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter
from docling_core.types.doc import TableItem

class TableProcessor(PipelineComponent):
    """Handles the extraction of tables from a PDF file and saves as text files."""
    
    def __init__(self, scale=2.0):
        super().__init__(name="TableProcessor")
        self.scale = scale
        self.logger = logging.getLogger(__name__)

    def process(self, conv_res, output_dir):
        """Extract tables from a PDF and save them as text files."""
        if not conv_res:
            self.logger.error("No conversion result found, skipping table extraction.")
            return []

        os.makedirs(output_dir, exist_ok=True)
        table_number = 1
        table_list = []

        for element, _level in conv_res.document.iterate_items():
            if isinstance(element, TableItem):
                # Use export_to_dataframe() to get table content as DataFrame
                try:
                    table_df = element.export_to_dataframe()  # This returns a Pandas DataFrame
                    
                    # Save the table as a text file
                    table_txt_filename = os.path.join(output_dir, f"table_{table_number}.txt")
                    with open(table_txt_filename, "w") as fp:
                        table_df.to_csv(fp, sep="\t", index=False)  # Save as tab-separated text
                        
                    # Append to table_list
                    table_list.append(table_txt_filename)
                    table_number += 1
                except Exception as e:
                    self.logger.error(f"Error saving table {table_number}: {e}")
        return table_list
