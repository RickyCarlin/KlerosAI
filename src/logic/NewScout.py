from src.services.TelethonService import TelethonService
import threading
from src.utils.logger import SingletonLogger
from src.services.TelegramConnectionService import TelegramConnectionService
from src.services.ChatGPTConnectionService import ChatGPTConnectionService
from src.logic.ArbiSense import SingletonArbiSense
from src.services.AppDataService import AppDataService
import time

class NewScout:

    ARBITRAGE_NOTIFY_PERIOD_IN_MINUTES = 5
    def __init__(self,
                    telethon_service: TelethonService,
                    telegram_connection_service: TelegramConnectionService):
        self.logger = SingletonLogger.getInstance()
        self.telethon_service = telethon_service
        self.telegram_connection_service = telegram_connection_service

        self.telegram_scout_thread = threading.Thread(target=self._scout_telegram_for_news_thread)
        self.telegram_scout_thread_running = False

        self.gpt_connection_service = ChatGPTConnectionService()
        
        self.arbisense = SingletonArbiSense.getInstance()
        if not self.arbisense.cross_arbitrage_analyzer_thread_running:
            self.start_arbisense = True
        else:
            self.start_arbisense = False
        self.arbitrage_scout_thread = threading.Thread(target=self._scout_arbitrage_thread)
        self.arbitrage_scout_thread_running = False

        self.arbitrage_notify_period = self.ARBITRAGE_NOTIFY_PERIOD_IN_MINUTES

        self.followed_news_group_1 = AppDataService.getFollowedNewsGroup1()
        
        return

    def _start_client_with_phone_number(self):
        self.telethon_service.start_client_with_phone_number()
        return

    def start(self):
        self._start_client_with_phone_number()
        self.telethon_service.start()
        self._start_scouting_telegram_for_news_thread()
        if self.start_arbisense:
            self._start_scouting_arbitrage_thread()
        return
    
    def stop(self):
        self._stop_scouting_telegram_for_news_thread()
        if self.start_arbisense:
            self._stop_scouting_arbitrage_thread()
        self.telethon_service.stop()
        self.telegram_connection_service.stop()
        return

    def _start_scouting_arbitrage_thread(self):
        self.arbitrage_scout_thread_running = True
        self.arbitrage_scout_thread.start()
        return
    
    def _stop_scouting_arbitrage_thread(self):
        self.arbitrage_scout_thread_running = False
        self.arbitrage_scout_thread.join()
        return
    
    def _form_arbitrage_message(self, arbitrage_percentages):
        arbitrage_message = "📊 Arbitrage Opportunity Detected!\n\n"
        for i in range(len(arbitrage_percentages)):
            current_opp = arbitrage_percentages[i]
            arbitrage_message += f"💰{current_opp['symbol']} Prices:\n"
            arbitrage_message += f"*\t📈{current_opp['first_market']}: ${current_opp['first_market_price']}\n"
            arbitrage_message += f"*\t📉{current_opp['second_market']}: ${current_opp['second_market_price']}\n"
            arbitrage_message += f"🔍 Price Difference: {current_opp['arbitrage_percentage']:.2f}%\n"
            arbitrage_message += "\n"
        arbitrage_message += "🚀Don't miss this Opportunitiy!\n\n"
        arbitrage_message += "**Disclaimer: Not a Financial Advice**"
        return arbitrage_message
    
    def _scout_arbitrage_thread(self):
        arbitrage_scout_timer = round(time.time() * 1000)
        while self.arbitrage_scout_thread_running:
            current_time = round(time.time() * 1000)
            if current_time - arbitrage_scout_timer > self.arbitrage_notify_period * 60 * 1000:
                arbitrage_analyzed = self.arbisense.wait_for_cross_arbitrage_analyzed_event(int((self.arbisense.DEFAULT_PERIOD * 1.5) * 1000))
                if arbitrage_analyzed:
                    arb_percentages = self.arbisense.arbitrage_percentages
                    if len(arb_percentages) > 0 and not self.telegram_connection_service.is_sleeping_for_retry_after:
                        arbitrage_message = self._form_arbitrage_message(arb_percentages)
                        self.telegram_connection_service.send_message(arbitrage_message)
                self.arbisense.clear_cross_arbitrage_analyzed_event()
                arbitrage_scout_timer = round(time.time() * 1000)
            else:
                time.sleep(0.1)
        return
    
    def _start_scouting_telegram_for_news_thread(self):
        self.telegram_scout_thread_running = True
        self.telegram_scout_thread.start()
        return

    def _stop_scouting_telegram_for_news_thread(self):
        self.telegram_scout_thread_running = False
        self.telegram_scout_thread.join()
        return

    def _is_user_from_news_group(self, username):
        print (username)
        if username in self.followed_news_group_1['news_group']:
            return True
        return False

    def _scout_telegram_for_news_thread(self):
        while self.telegram_scout_thread_running:
            if self.telethon_service.wait_for_message_retrieved_event(1000):
                event = self.telethon_service.retrieved_event
                message_chat = self.telethon_service.message_chat
                does_event_have_media = event.message.media
                if does_event_have_media:
                    print ("Media found")
                    pass
                else:
                    username = getattr(message_chat, 'username', None)
                    if username is not None:
                        if self._is_user_from_news_group(str(username)):
                            comment_of_gpt = self.gpt_connection_service.ask_question_to_gpt(self.telethon_service.get_retrieved_message())
                            self.telegram_connection_service.send_message(comment_of_gpt)
                self.telethon_service.clear_message_retrieved_event()
            else:
                pass
        return