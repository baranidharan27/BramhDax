import logging
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

class ImageDescriptionGenerator:
    """Generates image captions using the BLIP model."""
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        self.logger = logging.getLogger(__name__)

    def generate_description(self, image_path):
        """Generate a detailed description for the given image using BLIP model."""
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
