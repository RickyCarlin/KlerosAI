from telegram import Bot
from src.utils.logger import SingletonLogger
import traceback
import asyncio
import threading
from telegram.error import BadRequest, RetryAfter, Unauthorized
import time

class UsersNotSubscribedException(Exception):
    pass

class TelegramConnectionService:

    def __init__(self,
                    bot_token: str):
        self.bot_token = bot_token
        self.bot = Bot(token=self.bot_token)
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_event_loop, daemon=True)
        self.subscribed_user_ids = []
        self.users_subsribed = False
        self.logger = SingletonLogger.getInstance()
        self.stop_event = threading.Event()
        self.thread.start()
        self.logger.log_info("Telegram connection service started")
        self.is_sleeping_for_retry_after = False
        return
    
    def _start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        return
    
    async def send_message_async(self, message: str):
        if self.users_subsribed == False:
            raise UsersNotSubscribedException("Users not subscribed yet")
        for user_id in self.subscribed_user_ids:
            try:
                self.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                # Prints the type of the exception in red using ansi escape codes
                print("\033[91m" + str(type(e)) + "\033[0m")
                print (user_id)

                if type(e) == BadRequest:
                    self.logger.log_warning(f"Bad request for user {user_id}: {str(e)}")
                elif type(e) == RetryAfter:
                    self.logger.log_warning(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
                    self.is_sleeping_for_retry_after = True
                    time.sleep(e.retry_after)
                    self.is_sleeping_for_retry_after = False
                elif type(e) == Unauthorized:
                    self.logger.log_warning(f"Unauthorized to send message to user {user_id}: {str(e)}")
                else:
                    self.logger.log_critical(f"Error sending message to user {user_id}: {str(e)}")
                    traceback.print_exc()

        return
    
    def send_message(self, message: str):
        asyncio.run_coroutine_threadsafe(self.send_message_async(message), self.loop)
        return
    
    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        self.loop.close()
        self.logger.log_info("Telegram connection service stopped")
        return
    
    def set_subscribed_user_ids(self, user_chat_ids: list):
        self.subscribed_user_ids = user_chat_ids
        self.users_subsribed = True
        return
    
    def send_message_to_all_users(self, message: str):
        if not self.is_sleeping_for_retry_after:
            for user_id in self.subscribed_user_ids:
                try:
                    self.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    # Prints the type of the exception in red using ansi escape codes
                    print("\033[91m" + str(type(e)) + "\033[0m")

                    if type(e) == BadRequest:
                        self.logger.log_warning(f"Bad request for user {user_id}: {str(e)}")
                    elif type(e) == RetryAfter:
                        self.logger.log_warning(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
                        self.is_sleeping_for_retry_after = True
                        time.sleep(e.retry_after)
                        self.is_sleeping_for_retry_after = False
                    elif type(e) == Unauthorized:
                        self.logger.log_warning(f"Unauthorized to send message to user {user_id}: {str(e)}")
                    else:
                        self.logger.log_critical(f"Error sending message to user {user_id}: {str(e)}")
                    traceback.print_exc()

        '''
        try:
            for user_id in self.subscribed_user_ids:
                self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            _traceback = traceback.format_exc()
            self.logger.log_critical("Error sending message to all users: " + str(e) + "\n" + _traceback)
        '''
        return
    
    