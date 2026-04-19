import logging
import sys

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger