import sys
from pathlib import Path

# Choose the folder to import based on a condition or flag
USE_NEW_CODE = True  # Set this flag based on your need (True for `pipeline_copy`, False for `pipeline`)

# Dynamically set the folder path
if USE_NEW_CODE:
    sys.path.insert(0, str(Path(__file__).parent / 'pipeline_copy'))  # Add `pipeline_copy` folder to path
else:
    sys.path.insert(0, str(Path(__file__).parent / 'pipeline'))  # Add `pipeline` folder to path

from pipeline.document_processing import DocumentProcessor  # Or 'pipeline.document_processing' if USE_NEW_CODE is False
from pipeline.logger import setup_logging  # Same for other imports

def main():
    setup_logging()  # Initialize logging
    output_base_dir = "./output"
    pdf_paths = [Path("data/paper.pdf"), Path("data/paper2.pdf"), Path("data/paper3.pdf")]  # Add more PDFs as needed

    processor = DocumentProcessor(output_base_dir)
    processor.process_batch(pdf_paths)

if __name__ == "__main__":
    main()
