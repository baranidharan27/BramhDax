# IBM Docling Document Processing Pipeline

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Pipeline Components](#pipeline-components)
- [Output Format](#output-format)
- [Logging](#logging)
- [Extending the Pipeline](#extending-the-pipeline)
- [Additional Resources](#additional-resources)
- [License](#license)

## Overview

This repository provides a robust document processing pipeline built around IBM's Docling tool. The pipeline is designed for large-scale document parsing, focusing on efficient extraction of text, images, and tables from documents. While the pipeline can be used with RAG systems (example implementation provided in notebooks), its primary purpose is document preprocessing and parsing.

### Key Objectives
- Extract structured content from documents using IBM Docling
- Process images and generate captions using BLIP
- Extract and format tables from documents
- Provide scalable, parallel processing capabilities
- Enable easy integration with downstream LLM systems

## Features

### Core Functionality
- **Document Parsing**
  - Text extraction from PDFs using Docling
  - Metadata extraction and preservation
  - Structured content organization

- **Image Processing**
  - Automated image extraction
  - BLIP-powered image captioning
  - Organized image storage

- **Table Processing**
  - Table detection and extraction
  - Multiple format outputs (CSV, TXT)
  - Structure preservation

### Technical Features
- Multi-threaded parallel processing using ThreadPoolExecutor
- Batch processing capabilities
- Comprehensive logging system
- Modular, extensible architecture
- Robust error handling

## Project Structure

Here is the structure of the repository:

```
├── data/
│   ├── paper1.pdf # Input file 
│   ├── paper2.pdf # Input file 
│   └── ...
├── env/  #environment
├── notebooks/
│   ├── docling_parsing.ipynb # Docling implementation
│   ├── try_rag.ipynb # RAG implementation using granite and docling
├── output/
│   ├── paper/
│   │   ├── images/ # output images
│   │   ├── tables/ # output tables
│   │   ├── table_1.txt
│   │   └── final_output.txt
├── pipeline/
│   ├── __pycache__/
│   ├── base.py
│   ├── document_processing.py #document orchestration
│   ├── image_processing.py # image processing 
│   ├── logger.py # logging file
│   ├── pdf_processing.py # pdf processing 
│   ├── table_processing.py # table processing
│   └── __init__.py
├── .env
├── .gitignore
├── data_preprocessing.py 
├── main.py
├── pipeline.log
├── README.md
└── requirements.txt
```

### Notebooks
- **`docling_parsing.ipynb`**: This notebook contains the exploration of the Docling tool for document parsing and extraction of various components like images and tables.
- **`try_rag.ipynb`**: This notebook demonstrates the RAG (Retrieval-Augmented Generation) implementation using the extracted data for various tasks.


## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/baranidharan27/IBM.git
cd IBM
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify Installation**
```bash
python main.py --test
```

## Usage

### Basic Usage
```bash
python main.py
```
This will process all documents in the `data/` directory.

### Configuration
Create a `.env` file in the root directory:
```
LOG_LEVEL=INFO
BATCH_SIZE=10
USE_GPU=True
```

## Pipeline Components

### Base Class (base.py)
The foundation class providing:
- Configuration management
- Logging setup
- Error handling
- Common utilities

### Document Processing (document_processing.py)
Handles:
- PDF parsing
- Text extraction
- Document structure analysis

### Image Processing (image_processing.py)
Manages:
- Image extraction
- BLIP captioning integration
- Image storage

### Table Processing (table_processing.py)
Responsible for:
- Table detection
- Format conversion
- Structure preservation

## Output Format

### Directory Structure
```
output/
└── document_name/
    ├── images/
    ├── tables/
    └── final_output.txt
```

### Sample Output
```
<image_1>
{image_1_description: a diagram of the two phases of the algorithm}

<table_1>
[table content in structured format]
```

## Logging

The pipeline uses a centralized logging system:

```yaml
2025-02-20 11:18:38,377 - INFO - Processing paper.pdf...
2025-02-20 11:18:38,675 - INFO - Accelerator device: 'cuda:0'
2025-02-20 11:19:00,845 - INFO - Finished converting document paper.pdf
2025-02-20 11:19:21,036 - INFO - Generated description for ./output/paper/images/image_1.png: the plot of the fourier plot is shown in the following diagram
2025-02-20 11:19:21,036 - INFO - Final output saved to ./output/paper/final_output.txt
2025-02-20 11:19:21,036 - INFO - Finished processing paper.pdf. Extracted 21 images and 1 tables.
```

## Extending the Pipeline

### Adding New Processors
1. Create a new class in `pipeline/`
2. Inherit from `BaseProcessor`
3. Implement required methods
4. Register in `main.py`

### Custom Output Formats
Modify `document_processing.py` to add new output formats.

## Additional Resources

### Notebooks
- `docling_parsing.ipynb`: Examples and tutorials for using Docling
- `try_rag.ipynb`: Optional RAG implementation example using Granite model

## License

This project is licensed under the MIT License - see the LICENSE file for details.