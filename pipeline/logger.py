import logging

def setup_logging(log_file="pipeline.log"):
    """Set up the logger."""
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
