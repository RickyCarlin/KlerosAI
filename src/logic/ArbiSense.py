from src.services.BinanceIntegrationService import BinanceIntegrationService
from src.services.ByBitIntegrationService import ByBitIntegrationService
from src.services.KrakenIntegrationService import KrakenIntegrationService
from src.services.KuCoinIntegrationService import KuCoinIntegrationService
from src.services.OKXIntegrationService import OKXIntegrationService
from src.services.TelegramConnectionService import TelegramConnectionService
from src.data.Exchanges import Exchanges
import threading

class SingletonArbiSense:
    __instance = None

    @staticmethod
    def getInstance():
        if SingletonArbiSense.__instance is None:
            SingletonArbiSense()
        return SingletonArbiSense.__instance
    
    def __init__(self):
        if SingletonArbiSense.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            SingletonArbiSense.__instance = ArbiSense()
        return
    
class ArbiSense:

    DEFAULT_PERIOD = 2
    DEFAULT_VOLUME_THRESHOLD = 100000
    DEFAULT_ARBITRAGE_PERCENTAGE_THRESHOLD = 1
    DEFAULT_ABSURD_PERCENTAGE_THRESHOLD = 10

    def __init__(self):
        self.retrieve_period_in_seconds = self.DEFAULT_PERIOD
        self.retrieve_time_out_in_seconds = self.retrieve_period_in_seconds + 1
        self._initialie_exchange_services()

        self.cross_arbitrage_analyzer_thread = None
        self.cross_arbitrage_analyzer_thread_running = False
        self.cross_arbitrage_analyzer_thread = threading.Thread(target=self.process)
        self.cross_arbitrage_analyzed_event = threading.Event()

        self.binance_usdt_pairs = None
        self.bybit_usdt_pairs = None
        self.kraken_usdt_pairs = None
        self.kucoin_usdt_pairs = None
        self.okx_usdt_pairs = None

        self.common_pairs = []
        self.market_pairs_list = [
            (Exchanges.BINANCE.value, Exchanges.KUCOIN.value),
            (Exchanges.BINANCE.value, Exchanges.OKX.value),
            (Exchanges.BINANCE.value, Exchanges.BYBIT.value),
            (Exchanges.BINANCE.value, Exchanges.KRAKEN.value),
            (Exchanges.KUCOIN.value, Exchanges.OKX.value),
            (Exchanges.KUCOIN.value, Exchanges.BYBIT.value),
            (Exchanges.KUCOIN.value, Exchanges.KRAKEN.value),
            (Exchanges.OKX.value, Exchanges.BYBIT.value),
            (Exchanges.OKX.value, Exchanges.KRAKEN.value),
            (Exchanges.BYBIT.value, Exchanges.KRAKEN.value)
        ]

        self.volume_threshold = self.DEFAULT_VOLUME_THRESHOLD
        self.arbitrage_percentage_threshold = self.DEFAULT_ARBITRAGE_PERCENTAGE_THRESHOLD

        self.arbitrage_percentages = []

        return
    
    def set_telegram_connection_service(self, tcs: TelegramConnectionService = None):
        self.tcs = tcs

    def _send_message_through_telegram(self):
        if self.tcs:
            message = ""
            for percentage_data in self.arbitrage_percentages:
                message += f"{percentage_data['symbol']} {percentage_data['first_market']} {percentage_data['first_market_price']} {percentage_data['second_market']} {percentage_data['second_market_price']} {percentage_data['arbitrage_percentage']:.2f}%\n"
            self.tcs.send_message(message)
        return
    
    def process(self):
        self._start_exchange_services()
        if self._wait_for_price_retrievals():
            self._get_pairs_from_services()
            self._detect_common_pairs()
            pass
        while self.cross_arbitrage_analyzer_thread_running:
            if self._wait_for_price_retrievals():
                # Prints "Cross Arbitrage Analyzer: All Exchanges Price Retrieved" in green using ansi escape codes
                self._get_pairs_from_services()
                self._calculate_arbitrage_percentages()
                self.cross_arbitrage_analyzed_event.set()
                print("\033[92mCross Arbitrage Analyzer: All Exchanges Price Retrieved\033[0m")
                pass
            else:
                self._clear_service_events()
                print("\033[91mCross Arbitrage Analyzer: Price Retrieval Timeout\033[0m")
                pass
        return
    
    def clear_cross_arbitrage_analyzed_event(self):
        self.cross_arbitrage_analyzed_event.clear()
        return
    
    def wait_for_cross_arbitrage_analyzed_event(self, timeout=None):
        return self.cross_arbitrage_analyzed_event.wait(timeout)
    
    def start(self):
        self.cross_arbitrage_analyzer_thread_running = True
        self.cross_arbitrage_analyzer_thread.start()
        return
    
    def stop(self):
        self.cross_arbitrage_analyzer_thread_running = False
        self.cross_arbitrage_analyzer_thread.join()
        self._stop_exchange_services()
        return
    
    def _detect_common_pairs(self):
        markets = {
            Exchanges.BINANCE.value: self.binance_usdt_pairs.keys(),
            Exchanges.BYBIT.value: self.bybit_usdt_pairs.keys(),
            Exchanges.KRAKEN.value: self.kraken_usdt_pairs.keys(),
            Exchanges.KUCOIN.value: self.kucoin_usdt_pairs.keys(),
            Exchanges.OKX.value: self.okx_usdt_pairs.keys()
        }
        self.common_pairs = []
        for exchange1, exchange2 in self.market_pairs_list:
            pairs1 = set(markets.get(exchange1, []))
            pairs2 = set(markets.get(exchange2, []))
            common_pairs = list(pairs1.intersection(pairs2))
            self.common_pairs.append(common_pairs)
            #print(f"Common pairs between {exchange1} and {exchange2}: {common_pairs}")
        return

    def _get_related_data_for_market(self, market):
        if market == Exchanges.BINANCE.value:
            return self.binance_usdt_pairs
        elif market == Exchanges.BYBIT.value:
            return self.bybit_usdt_pairs
        elif market == Exchanges.KRAKEN.value:
            return self.kraken_usdt_pairs
        elif market == Exchanges.KUCOIN.value:
            return self.kucoin_usdt_pairs
        elif market == Exchanges.OKX.value:
            return self.okx_usdt_pairs
        else:
            return None

    def _calculate_arbitrage_percentages(self):
        self.arbitrage_percentages = []
        for i in range(len(self.market_pairs_list)):
            first_market, second_market = self.market_pairs_list[i]
            common_market_pairs = self.common_pairs[i]
            for symbol in common_market_pairs:
                first_market_pairs = self._get_related_data_for_market(first_market)
                second_market_pairs = self._get_related_data_for_market(second_market)
                first_market_common_pair = first_market_pairs.get(symbol, None)
                second_market_common_pair = second_market_pairs.get(symbol, None)
                over_threshold_pairs = {}
                if first_market_common_pair and second_market_common_pair:
                    first_market_common_pair_volume = first_market_common_pair.volume_in_quote_currency()
                    second_market_common_pair_volume = second_market_common_pair.volume_in_quote_currency()
                    if first_market_common_pair_volume > self.volume_threshold and second_market_common_pair_volume > self.volume_threshold:
                        first_market_common_pair_price = first_market_common_pair.price
                        second_market_common_pair_price = second_market_common_pair.price
                        arbitrage_percentage = (first_market_common_pair_price - second_market_common_pair_price) / first_market_common_pair_price * 100
                        if arbitrage_percentage < 0 and abs(arbitrage_percentage) > self.arbitrage_percentage_threshold and abs(arbitrage_percentage) < self.DEFAULT_ABSURD_PERCENTAGE_THRESHOLD:
                            over_threshold_pairs["first_market"] = second_market
                            over_threshold_pairs["second_market"] = first_market
                            over_threshold_pairs["symbol"] = symbol
                            over_threshold_pairs["first_market_price"] = second_market_common_pair.price
                            over_threshold_pairs["second_market_price"] = first_market_common_pair.price
                            over_threshold_pairs["arbitrage_percentage"] = abs(arbitrage_percentage)
                            self.arbitrage_percentages.append(over_threshold_pairs)
                        elif arbitrage_percentage > 0 and arbitrage_percentage > self.arbitrage_percentage_threshold and arbitrage_percentage < self.DEFAULT_ABSURD_PERCENTAGE_THRESHOLD:
                            over_threshold_pairs["first_market"] = first_market
                            over_threshold_pairs["second_market"] = second_market
                            over_threshold_pairs["symbol"] = symbol
                            over_threshold_pairs["first_market_price"] = first_market_common_pair.price
                            over_threshold_pairs["second_market_price"] = second_market_common_pair.price
                            over_threshold_pairs["arbitrage_percentage"] = arbitrage_percentage
                            self.arbitrage_percentages.append(over_threshold_pairs)
        return
    
    def _get_pairs_from_services(self):
        self.binance_usdt_pairs = self.binance_integration_service.get_usdt_pairs_and_clear_event()
        self.bybit_usdt_pairs = self.bybit_integration_service.get_usdt_pairs_and_clear_event()
        self.kraken_usdt_pairs = self.kraken_integration_service.get_usdt_pairs_and_clear_event()
        self.kucoin_usdt_pairs = self.kucoin_integration_service.get_refined_usdt_pairs_and_clear_event()
        self.okx_usdt_pairs = self.okx_integration_service.get_refined_usdt_pairs_and_clear_event()
        return
    
    def _initialie_exchange_services(self):
        self.binance_integration_service = BinanceIntegrationService()
        self.binance_integration_service.set_sleep_duration(self.retrieve_period_in_seconds)
        self.bybit_integration_service = ByBitIntegrationService()
        self.bybit_integration_service.set_sleep_duration(self.retrieve_period_in_seconds)
        self.kraken_integration_service = KrakenIntegrationService()
        self.kraken_integration_service.set_sleep_duration(self.retrieve_period_in_seconds)
        self.kucoin_integration_service = KuCoinIntegrationService()
        self.kucoin_integration_service.set_sleep_duration(self.retrieve_period_in_seconds)
        self.okx_integration_service = OKXIntegrationService()
        self.okx_integration_service.set_sleep_duration(self.retrieve_period_in_seconds)
        return
    
    def _start_exchange_services(self):
        self.binance_integration_service.start_price_retrieval_thread()
        self.bybit_integration_service.start_price_retrieval_thread()
        self.kraken_integration_service.start_price_retrieval_thread()
        self.kucoin_integration_service.start_price_retrieval_thread()
        self.okx_integration_service.start_price_retrieval_thread()
        return
    
    def _wait_for_price_retrievals(self):
        self.binance_integration_service.wait_for_price_retrieved_event(self.retrieve_time_out_in_seconds)
        self.bybit_integration_service.wait_for_price_retrieved_event(self.retrieve_time_out_in_seconds)
        self.kraken_integration_service.wait_for_price_retrieved_event(self.retrieve_time_out_in_seconds)
        self.kucoin_integration_service.wait_for_price_retrieved_event(self.retrieve_time_out_in_seconds)
        self.okx_integration_service.wait_for_price_retrieved_event(self.retrieve_time_out_in_seconds)
        return (self.binance_integration_service.is_price_retrieved_event_set() and
                self.bybit_integration_service.is_price_retrieved_event_set() and
                self.kraken_integration_service.is_price_retrieved_event_set() and
                self.kucoin_integration_service.is_price_retrieved_event_set() and
                self.okx_integration_service.is_price_retrieved_event_set())
    
    def _clear_service_events(self):
        self.binance_integration_service.clear_price_retrieved_event()
        self.bybit_integration_service.clear_price_retrieved_event()
        self.kraken_integration_service.clear_price_retrieved_event()
        self.kucoin_integration_service.clear_price_retrieved_event()
        self.okx_integration_service.clear_price_retrieved_event()
        return
    
    def _stop_exchange_services(self):
        self.binance_integration_service.stop_price_retrieval_thread()
        self.bybit_integration_service.stop_price_retrieval_thread()
        self.kraken_integration_service.stop_price_retrieval_thread()
        self.kucoin_integration_service.stop_price_retrieval_thread()
        self.okx_integration_service.stop_price_retrieval_thread()
        return
    