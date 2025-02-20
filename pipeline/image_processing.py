import logging
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from .base import PipelineComponent  # Import the base class

class ImageDescriptionGenerator(PipelineComponent):
    """Generates image captions using the BLIP model."""
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        super().__init__(name="ImageDescriptionGenerator")
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)

    def process(self, image_path):
        """Generate a description for the given image."""
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(image, return_tensors="pt")
            out = self.model.generate(**inputs)
            description = self.processor.decode(out[0], skip_special_tokens=True)
            self.logger.info(f"Generated description for {image_path}: {description}")
            return description
        except Exception as e:
            self.logger.error(f"Error generating description for {image_path}: {e}")
            return "No description available"
