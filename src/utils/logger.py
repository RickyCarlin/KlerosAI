import os
import datetime
import enum
import threading
import traceback

class LogLevel(enum.Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    EXCEPTION = 'EXCEPTION'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class SingletonLogger:
    __instance = None

    @staticmethod
    def getInstance():
        if SingletonLogger.__instance is None:
            SingletonLogger()
            SingletonLogger.__instance.initialize_logger()
        return SingletonLogger.__instance
    
    def __init__(self):
        if SingletonLogger.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            SingletonLogger.__instance = Logger()
        return

class Logger:

    def __init__(self):
        return
    
    def initialize_logger(self,
                            log_file_path: str = 'logs.log'):
        self.current_dir = os.getcwd()
        self.log_data_lock = threading.Lock()
        self.log_file_path = os.path.join(self.current_dir, 'logs.log')
        self._create_log_file()
        return
    
    def log_info(self,
                 message: str):
        self.log_data_lock.acquire()
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(self._log_format(LogLevel.INFO, message))
        self.log_data_lock.release()
        return
    
    def log_warning(self,
                    message: str):
        self.log_data_lock.acquire()
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(self._log_format(LogLevel.WARNING, message))
        self.log_data_lock.release()
        return
    
    def log_exception(self,
                        exception: Exception):
            self.log_data_lock.acquire()
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                _traceback = traceback.format_exc()
                log_file.write(self._log_format(LogLevel.EXCEPTION, _traceback))
            self.log_data_lock.release()
            return
    
    def log_error(self,
                    message: str):
        self.log_data_lock.acquire()
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(self._log_format(LogLevel.ERROR, message))
        self.log_data_lock.release()
        return
    
    def log_critical(self,
                    message: str):
        self.log_data_lock.acquire()
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(self._log_format(LogLevel.CRITICAL, message))
        self.log_data_lock.release()
        return
    
    def _create_log_file(self):
        if os.path.exists(self.log_file_path):
            return
        self.log_data_lock.acquire()
        with open(self.log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write('')
            creation_info = self._log_format(LogLevel.INFO, 'Log file created')
            log_file.write(creation_info)
        self.log_data_lock.release()
        return
    
    def _log_format(self,
                    log_level: LogLevel,
                    message: str):
        return f'{datetime.datetime.now()} - {log_level.value} - {message}\n'
    
