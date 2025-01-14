import requests
from src.utils.logger import SingletonLogger
from src.utils.fileutils import FileUtils
from src.models.PriceDataModel import PriceDataModel
from src.data.Exchanges import Exchanges
import time
import threading
import traceback

class BinanceEndpoints:
    _BASE_URL = "https://api.binance.com/api/v3"
    _EXCHANGE_INFO = "/exchangeInfo"
    _24HR_TICKER_PRICE_CHANGE = "/ticker/24hr"

class BinanceIntegrationService:

    INTERVAL_IN_SEC = 5
    def __init__(self):
        self.logger = SingletonLogger.getInstance()
        
        self.rulebooks_folder_path = FileUtils.join_paths(FileUtils.current_directory(), "rulebooks")
        FileUtils.create_directory_if_not_exists(self.rulebooks_folder_path)
        
        self.rulebook_path = FileUtils.join_paths(self.rulebooks_folder_path, "binance_symbol_rules.json")

        self.exchange_info = None

        self.usdt_pairs_dictionary = {}
        self.usdt_pairs_dictionary_lock = threading.Lock()
        
        self._initialize_price_retrieval_thread_params()
        return
    
    '''   THREAD MANAGEMENT   '''
    def _initialize_price_retrieval_thread_params(self):
        self.price_retrieval_thread = threading.Thread(target=self._price_data_retrieval)
        self.price_retrieval_thread_running = False
        self.price_retrieved_event = threading.Event()
        self.price_retrieved_event_sleep_time = self.INTERVAL_IN_SEC
        self.price_retrieved_event_timeout = self.INTERVAL_IN_SEC + 1
        return
    
    def start_price_retrieval_thread(self):
        self.price_retrieval_thread_running = True
        self.price_retrieval_thread.start()
        return
    
    def stop_price_retrieval_thread(self):
        self.price_retrieval_thread_running = False
        self.price_retrieval_thread.join()
        self.price_retrieved_event.set()
        return

    def get_price_retrieved_event(self):
        return self.price_retrieved_event

    def clear_price_retrieved_event(self):
        self.price_retrieved_event.clear()
        return
    
    def is_price_retrieved_event_set(self):
        return self.price_retrieved_event.is_set()
    
    def wait_for_price_retrieved_event(self, timeout=None):
        self.price_retrieved_event.wait(timeout)
        return

    def get_usdt_pairs_and_clear_event(self):
        usdt_pairs = self.get_usdt_pairs_dictionary()
        self.clear_price_retrieved_event()
        return usdt_pairs

    def set_sleep_duration(self, sleep_duration: int):
        self.price_retrieved_event_sleep_time = sleep_duration
        return
    
    def _price_data_retrieval(self):
        self.fetch_exchange_info()
        while self.price_retrieval_thread_running:
            current_time_in_ms = int(round(time.time() * 1000))
            price_data_fetched = self.fetch_24hr_price_changes()
            if price_data_fetched:
                self.price_retrieved_event.set()
            end_time_in_ms = int(round(time.time() * 1000))
            time_diff = end_time_in_ms - current_time_in_ms
            sleep_time = self.price_retrieved_event_sleep_time - (time_diff / 1000)
            if sleep_time > 0:
                time.sleep(sleep_time)
        return

    def _generic_exception_handler(self, e: Exception, log: str):
        self.logger.log_critical(log + str(e), str(traceback.format_exc()))
        return
    
    def get_symbol_rules(self):
        if self.exchange_info is None:
            raise RuntimeError("Exchange info not loaded yet")
        return self.exchange_info["symbols"]
    
    def is_symbol_trading(self, symbol):
        if self.exchange_info is None:
            raise RuntimeError("Exchange info not loaded yet")
        
        for symbol_info in self.exchange_info["symbols"]:
            if symbol_info["symbol"] == symbol:
                return symbol_info['status'] == "TRADING"
        return False
    
    def save_exchange_info(self):
        if self.exchange_info is None:
            raise RuntimeError("Exchange info not loaded yet")
        
        FileUtils.write_json_to_file(self.rulebook_path, self.exchange_info)
        return
    
    def _update_usdt_pairs_dictionary(self,
                                        symbol: str,
                                        price_data_model: PriceDataModel):
        self.usdt_pairs_dictionary_lock.acquire()
        self.usdt_pairs_dictionary[symbol] = price_data_model
        self.usdt_pairs_dictionary_lock.release()
        return
    
    def get_usdt_pairs_dictionary(self):
        copied_dict = {}
        self.usdt_pairs_dictionary_lock.acquire()
        copied_dict = self.usdt_pairs_dictionary.copy()
        self.usdt_pairs_dictionary_lock.release()
        return copied_dict
    
    def fetch_ticker_info(self):
        if self.exchange_info is None:
            self.fetch_exchange_info()

        return self.fetch_24hr_price_changes()
    
    def fetch_24hr_price_changes(self):
        if self.exchange_info is None:
            raise RuntimeError("Exchange info not loaded yet")
        
        end_point = BinanceEndpoints._BASE_URL + BinanceEndpoints._24HR_TICKER_PRICE_CHANGE

        try:
            response = requests.get(end_point)
            response.raise_for_status()
            data = response.json()
            
            data_retrieval_time = int(round((time.time()  + (3 * 3600)) * 1000))

            for item in data:
                try:
                    index_of_usdt = item["symbol"].index("USDT")
                    if self.is_symbol_trading(item["symbol"]):
                        symbol_price_data_model = PriceDataModel(
                            item["symbol"],
                            item["lastPrice"],
                            Exchanges.BINANCE.value,
                            data_retrieval_time,
                            item["volume"]
            )
                        self._update_usdt_pairs_dictionary(item["symbol"], symbol_price_data_model)
                except ValueError:
                    pass
            return True
        except requests.exceptions.RequestException as e:
            self.logger.log_critical("Failed Binance API Call: " + str(e), str(traceback.format_exc()))
            return False
        except Exception as e:
            self._generic_exception_handler(e, "Error getting 24hr price changes: ")
            return False
        
    def fetch_exchange_info(self):
        end_point = BinanceEndpoints._BASE_URL + BinanceEndpoints._EXCHANGE_INFO

        try:
            response = requests.get(end_point)
            response.raise_for_status()
            data = response.json()
            self.exchange_info = data
            self.exchange_info["program_update_timestamp"] = round(time.time() * 1000)
            return True
        except requests.exceptions.RequestException as e:
            self.logger.log_critical("Failed Binance API Call: " + str(e), str(traceback.format_exc()))
            return False
        except Exception as e:
            self._generic_exception_handler(e, "Error getting exchange info: ")
            return False
        
        return
    