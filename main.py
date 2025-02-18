from pathlib import Path
from pipeline.logger import setup_logging
from pipeline.document_processing import DocumentProcessor

def main():
    setup_logging()  # Initialize logging
    output_base_dir = "./output"
    pdf_paths = [Path("data/paper.pdf"), Path("data/paper2.pdf")]  # Add more PDFs as needed

    processor = DocumentProcessor(output_base_dir)
    processor.process_batch(pdf_paths)

if __name__ == "__main__":
    main()
