import logging

class LoggingAdapter:
    def __init__(self, config):
        self.config = config
        logging.basicConfig(
            filename=self.config['persistence']['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_info(self, message):
        logging.info(message)

    def log_error(self, message):
        logging.error(message)
