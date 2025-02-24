import logging
from pathlib import Path
from docling_core.types.doc import PictureItem
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from .base import PipelineComponent

class ProximityCaptioner(PipelineComponent):
    """Generates captions for images using proximity-based text extraction."""
    
    def __init__(self):
        super().__init__(name="ProximityCaptioner")
        self.logger = logging.getLogger(__name__)

    def find_caption_near_coordinates(self, doc, bbox, page_no):
        """Find caption text near the given coordinates."""
        caption = None
        min_distance = float('inf')
        
        # Look through all text elements
        for text_item in doc.texts:
            # Check if text is on the same page and near the image
            if hasattr(text_item, 'prov') and text_item.prov:
                text_prov = text_item.prov[0]
                if (text_prov.page_no == page_no and 
                    hasattr(text_item, 'text') and 
                    ('figure' in text_item.text.lower() or 'fig.' in text_item.text.lower())):
                    
                    # Calculate distance from image bottom to text
                    distance = abs(text_prov.bbox.t - bbox.b)
                    if distance < min_distance:
                        min_distance = distance
                        caption = text_item.text.strip()
        
        return caption

    def process(self, conv_res):
        """Extract images and their captions from a PDF conversion result."""
        if not conv_res:
            self.logger.error("No conversion result found")
            return []
        
        images_list = []
        image_number = 1
        
        # Process items
        for item, level in conv_res.document.iterate_items():
            if isinstance(item, PictureItem) and item.prov:
                try:
                    self.logger.info(f"Processing PictureItem {image_number}")
                    
                    # Get image location
                    bbox = item.prov[0].bbox
                    page_no = item.prov[0].page_no
                    
                    # Find caption near image
                    caption = self.find_caption_near_coordinates(conv_res.document, bbox, page_no)
                    if not caption:
                        caption = "No caption found"
                    
                    self.logger.info(f"Image {image_number} on page {page_no}")
                    self.logger.info(f"Location: {bbox.l:.2f}, {bbox.t:.2f}, {bbox.r:.2f}, {bbox.b:.2f}")
                    self.logger.info(f"Caption: {caption}")
                    
                    # Store result
                    images_list.append({
                        'number': image_number,
                        'page': page_no,
                        'caption': caption,
                        'bbox': bbox
                    })
                    
                    image_number += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing image {image_number}: {str(e)}")
                    continue
        
        self.logger.info(f"Found {len(images_list)} images with captions")
        return images_list