import logging
import os

def setup_logger():
    log_file = 'library_system.log'
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() # Also output to console
        ]
    )
    
    return logging.getLogger('LibrarySystem')

logger = setup_logger()
