
import logging

class HasLog:
    def info(self, msg):
        logging.info(msg)
    def warning(self, msg):
        logging.warning(f'WARNING:{msg}')
    def error(self, msg):
        logging.error(f'ERROR:{msg}')