import logging
from datetime import datetime

def setup_logging():
    current_date = datetime.now().strftime('%m_%d')
    log_filename = f'app_{current_date}.log'

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger