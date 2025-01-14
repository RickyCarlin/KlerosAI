import requests
from src.data.Exchanges import Exchanges
from src.utils.logger import SingletonLogger
from src.models.PriceDataModel import PriceDataModel
from src.utils.fileutils import FileUtils
import time
import threading
import traceback

class KuCoinEndpoints:
    _BASE_URL = "https://api.kucoin.com"
    _EXCHANGE_INFO = "/api/v2/symbols"
    _ALL_TICKERS = "/api/v1/market/allTickers"

class KuCoinIntegrationService:
    
    INTERVAL_IN_SEC = 5
    def __init__(self):
        self.logger = SingletonLogger.getInstance()

        self.rulebooks_folder_path = FileUtils.join_paths(FileUtils.current_directory(), "rulebooks")
        FileUtils.create_directory_if_not_exists(self.rulebooks_folder_path)

        self.rulebook_path = FileUtils.join_paths(self.rulebooks_folder_path, "kucoin_symbol_spot_rules.json")

        self.spot_rules = None
        self.spot_rules_update_time = 0

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
    
    def get_refined_usdt_pairs_and_clear_event(self):
        usdt_pairs = self.get_refined_usdt_pairs_dictionary()
        self.clear_price_retrieved_event()
        return usdt_pairs
    
    def set_sleep_duration(self, sleep_duration: int):
        self.price_retrieved_event_sleep_time = sleep_duration
        return
    
    def _price_data_retrieval(self):
        self.fetch_spot_symbols_info()
        while self.price_retrieval_thread_running:
            current_time_in_ms = int(round(time.time() * 1000))
            price_data_fetched = self.fetch_latest_prices()
            if price_data_fetched:
                self.price_retrieved_event.set()
            end_time_in_ms = int(round(time.time() * 1000))
            time_diff = end_time_in_ms - current_time_in_ms
            sleep_time = self.price_retrieved_event_sleep_time - (time_diff / 1000)
            if sleep_time > 0:
                time.sleep(sleep_time)
        return
    
    def _generic_exception_handler(self, e: Exception, log: str):
        self.logger.log_critical(log + str(e) + str(traceback.format_exc()))
        return
    
    def get_spot_symbol_rules(self):
        return self.spot_rules
    
    def is_symbol_trading(self, symbol: str):
        if self.spot_rules is None:
            raise RuntimeError("Spot rules not loaded yet")
        for rule in self.spot_rules:
            if rule["symbol"] == symbol:
                return rule["enableTrading"]
        return False
    
    def save_spot_rules(self):
        if self.spot_rules is None:
            raise RuntimeError("Spot rules not loaded yet")
        FileUtils.write_json_to_file(self.rulebook_path, self.spot_rules)
        return
    
    def _update_usdt_pairs_dictionary(self, symbol: str, price_data_model: PriceDataModel):
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
    
    def get_refined_usdt_pairs_dictionary(self):
        refined_dict = {}
        self.usdt_pairs_dictionary_lock.acquire()
        for key in self.usdt_pairs_dictionary:
            refined_dict[key.replace("-", "")] = self.usdt_pairs_dictionary[key]
        self.usdt_pairs_dictionary_lock.release()
        return refined_dict
    
    def fetch_ticker_info(self):
        if self.spot_rules is None:
            self.fetch_spot_symbols_info()

        return self.fetch_latest_prices()
    
    def fetch_latest_prices(self):
        if self.spot_rules is None:
            raise RuntimeError("Spot rules not loaded yet")
        end_point = KuCoinEndpoints._BASE_URL + KuCoinEndpoints._ALL_TICKERS
        try:
            response = requests.get(end_point)
            response.raise_for_status()
            tickers = response.json().get("data", []).get("ticker", [])

            data_retrieval_time = int(round((time.time() + 3*3600) * 1000))
            for ticker in tickers:
                symbol = ticker["symbol"]
                try:
                    index_of_usdt = symbol.index("USDT")
                    if self.is_symbol_trading(symbol):
                        price_data_model = PriceDataModel(
                            symbol,
                            float(ticker["last"] or 0),
                            Exchanges.KUCOIN.value,
                            data_retrieval_time,
                            float(ticker["vol"] or 0)
                        )
                        self._update_usdt_pairs_dictionary(symbol, price_data_model)
                except ValueError:
                    continue
            return True
        except requests.exceptions.RequestException as e:
            self.logger.log_critical("Failed KuCoin API Call: " + str(e), str(traceback.format_exc()))
            return False
        except Exception as e:
            self._generic_exception_handler(e, "Error in fetch_latest_prices: ")
            return False
    
    def fetch_spot_symbols_info(self):
        end_point = KuCoinEndpoints._BASE_URL + KuCoinEndpoints._EXCHANGE_INFO

        try:
            response = requests.get(end_point)
            response.raise_for_status()
            self.spot_rules = response.json().get("data", [])
            self.spot_rules_update_time = int(round(time.time() * 1000))
            self.save_spot_rules()
            return True
        except requests.exceptions.RequestException as e:
            self.logger.log_critical("Failed KuCoin API Call: " + str(e), str(traceback.format_exc()))
            return False
        except Exception as e:
            self._generic_exception_handler(e, "Error in fetch_spot_symbols_info: ")
            return False    