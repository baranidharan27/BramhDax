# llm_enricher.py
import torch
import re
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from .base import PipelineComponent

class LLMEnricher(PipelineComponent):
    """Enriches image captions using an LLM."""
    
    def __init__(self):
        super().__init__(name="LLMEnricher")
        # Load pre-trained model and tokenizer for GPT-2
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Set pad_token to eos_token
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)

    def generate_caption(self, description):
        """Generate a detailed caption for the given description."""
        input_text = f"Generate a detailed and unique caption for the figure described below:\n{description}\nCaption:"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        max_new_tokens = 100
        input_length = inputs['input_ids'].shape[1]
        if input_length + max_new_tokens > self.model.config.max_position_embeddings:
            max_new_tokens = self.model.config.max_position_embeddings - input_length

        outputs = self.model.generate(inputs['input_ids'], 
                                     attention_mask=inputs['attention_mask'], 
                                     max_new_tokens=max_new_tokens, 
                                     num_return_sequences=1, 
                                     pad_token_id=self.tokenizer.eos_token_id,
                                     temperature=0.7, 
                                     top_p=0.9, 
                                     no_repeat_ngram_size=2)
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated caption (after "Caption:")
        caption_start = full_text.find("Caption:") + len("Caption:")
        caption = full_text[caption_start:].strip()
        return caption

    def generate_key_insights(self, description):
        """Generate key insights for the given description."""
        input_text = f"What are the key insights or conclusions from the figure described below?\n{description}\nKey Insights:"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        max_new_tokens = 100
        input_length = inputs['input_ids'].shape[1]
        if input_length + max_new_tokens > self.model.config.max_position_embeddings:
            max_new_tokens = self.model.config.max_position_embeddings - input_length

        outputs = self.model.generate(inputs['input_ids'], 
                                     attention_mask=inputs['attention_mask'], 
                                     max_new_tokens=max_new_tokens, 
                                     num_return_sequences=1, 
                                     pad_token_id=self.tokenizer.eos_token_id,
                                     temperature=0.7, 
                                     top_p=0.9, 
                                     no_repeat_ngram_size=2)
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated insights (after "Key Insights:")
        insights_start = full_text.find("Key Insights:") + len("Key Insights:")
        insights = full_text[insights_start:].strip()
        return insights

    def generate_mathematical_context(self, description):
        """Generate mathematical context for the given description."""
        input_text = f"What is the mathematical or theoretical background related to the figure described below?\n{description}\nMathematical Context:"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        max_new_tokens = 100
        input_length = inputs['input_ids'].shape[1]
        if input_length + max_new_tokens > self.model.config.max_position_embeddings:
            max_new_tokens = self.model.config.max_position_embeddings - input_length

        outputs = self.model.generate(inputs['input_ids'], 
                                     attention_mask=inputs['attention_mask'], 
                                     max_new_tokens=max_new_tokens, 
                                     num_return_sequences=1, 
                                     pad_token_id=self.tokenizer.eos_token_id,
                                     temperature=0.7, 
                                     top_p=0.9, 
                                     no_repeat_ngram_size=2)
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated mathematical context (after "Mathematical Context:")
        context_start = full_text.find("Mathematical Context:") + len("Mathematical Context:")
        math_context = full_text[context_start:].strip()
        return math_context

    def process(self, image_data):
        """Enrich image captions using the LLM."""
        enriched_data = []
        for img in image_data:
            try:
                description = img['caption']
                enriched_data.append({
                    'image': img['number'],
                    'page': img['page'],
                    'data': {
                        'image_description': description,
                        'image_caption': self.generate_caption(description),
                        'key_insights': self.generate_key_insights(description),
                        'mathematical_context': self.generate_mathematical_context(description)
                    }
                })
            except Exception as e:
                self.logger.error(f"Error enriching caption for image {img['number']}: {e}")
        return enriched_data