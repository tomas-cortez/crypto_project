import logging

def setup_logging():
    """Configures basic logging to a file"""
    
    logging.basicConfig(
        filename="../logs/crypto_data.log",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )