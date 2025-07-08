import logging
from logging.handlers import TimedRotatingFileHandler

class BaseSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(BaseSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger():
    def __init__(self, filename, *args, **kwargs):
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)20s() - %(message)s")
        handler = TimedRotatingFileHandler(filename, when="midnight", backupCount=7)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def error(self, msg, *args, **kwargs):
       self.logger.error(msg = msg, *args, **kwargs)
    
    def warn(self, msg, *args, **kwargs):
       self.logger.warning(msg = msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
       self.logger.warning(msg = msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
       self.logger.info(msg = msg, *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
       self.logger.exception(msg = msg, *args, **kwargs)

class commonLogger(Logger, metaclass = BaseSingleton):
   def __init__(self, filename, *args, **kwargs):
      super().__init__(filename=filename, *args, **kwargs)

class scrapperLogger(Logger, metaclass = BaseSingleton):
   def __init__(self, filename, *args, **kwargs):
      super().__init__(filename=filename, *args, **kwargs)