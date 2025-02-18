import os
import logging
from concurrent.futures import ThreadPoolExecutor
from .pdf_processing import PdfProcessor
from .image_processing import ImageDescriptionGenerator

class DocumentProcessor:
    """Handles the entire document processing pipeline."""
    
    def __init__(self, output_base_dir, scale=2.0):
        self.output_base_dir = output_base_dir
        self.pdf_processor = PdfProcessor(scale)
        self.image_description_generator = ImageDescriptionGenerator()
        self.logger = logging.getLogger(__name__)

    def process_pdf(self, pdf_path):
        """Process a single PDF file."""
        pdf_name = pdf_path.stem
        output_dir = os.path.join(self.output_base_dir, pdf_name)
        os.makedirs(output_dir, exist_ok=True)

        self.logger.info(f"Processing {pdf_path.name}...")
        conv_res = self.pdf_processor.parse_pdf(pdf_path)

        if conv_res:
            # Extract images
            images_dir = os.path.join(output_dir, "images")
            images = self.pdf_processor.extract_images(conv_res, images_dir)

            # Generate final output with image descriptions
            self.generate_final_output(images, output_dir)

            self.logger.info(f"Finished processing {pdf_path.name}. Extracted {len(images)} images.")
        else:
            self.logger.error(f"Skipping {pdf_path.name} due to parsing error.")

    def generate_final_output(self, images, output_dir):
        """Generate the final output text file with image descriptions."""
        output_text = ""
        for idx, (image_path, _) in enumerate(images, start=1):
            description = self.image_description_generator.generate_description(image_path)
            output_text += f"<image_{idx}>\n"
            output_text += f"{{image_{idx}_description: {description}}}\n\n"

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
