import logging

class Log:
    def __init__(self,log_level='debug'):
        self.log_level = log_level
        self._set_log_level()
        
    def _set_log_level(self):
        log_level = self.log_level.lower()
        level = logging.INFO
        if log_level == 'debug':
            level = logging.DEBUG
        elif log_level == 'warning':
            level = logging.WARNING
        elif log_level == 'error':
            level = logging.ERROR
        elif log_level == 'critical':
            level = logging.CRITICAL
        # set logging config
        logging.basicConfig(level=level, format='%(asctime)s %(message)s')
    
    def debug(self,msg):
        logging.debug(msg)
    
    def info(self,msg):
        logging.info(msg)
    
    def warning(self,msg):
        logging.warning(msg)
    
    def error(self,msg):
        logging.error(msg)
    
    def critical(self,msg):
        logging.critical(msg)
    
