from telethon import TelegramClient, events
import asyncio
import threading

class TelethonService:

    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        
        self.chats = []
        self.chat_lock = threading.Lock()
        self.chat_entities = []

        self.retrieved_symbols = []
        self.retrieved_symbols_lock = threading.Lock()

        self._initialize_client_object()

        self._initialize_async_loop()

        self._initialize_thread()

        self.retrieved_message = None
        self.retrieved_event = None
        self.retrieved_message_lock = threading.Lock()
        self.message_retrieved_event = threading.Event()
        return

    def _set_retrieved_message(self, message):
        self.retrieved_message_lock.acquire()
        self.retrieved_message = message
        self.retrieved_message_lock.release()
        return
    
    def _get_retrieved_message(self):
        self.retrieved_message_lock.acquire()
        message = self.retrieved_message
        self.retrieved_message_lock.release()
        return message
    
    def get_retrieved_message(self):
        return self._get_retrieved_message()
    
    def wait_for_message_retrieved_event(self, timeout=None):
        return self.message_retrieved_event.wait(timeout)
    
    def clear_message_retrieved_event(self):
        self.message_retrieved_event.clear()
        return
    
    def add_chat(self, chat_name):
        self._add_chat(chat_name)
        return

    def start_client_with_phone_number(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_client_with_phone_number())
        return
    
    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run_client, args=(self.loop,))
            self.thread.start()
        else:
            print ('Thread is already running')
        return
    
    def stop(self):
        if self.thread is not None:
            print ('Stopping Thread')
            if not self.symbols_retrieved_event.is_set():
                self._set_symbols_retrieved_event()
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.client.disconnect()
            self.thread.join()
            self.thread = None
            print ('Thread Stopped')
        else:
            print ('Thread is not running')
        return
    
    def get_symbols_retrieved_event(self):
        return self.symbols_retrieved_event
    
    def get_retrieved_symbols(self):
        self.retrieved_symbols_lock.acquire()
        symbol_list = self.retrieved_symbols
        self.retrieved_symbols_lock.release()
        return symbol_list
    
    def clear_retrieved_symbols(self):
        self._clear_symbols_retrieved_event()
        return
    
    def _initialize_client_object(self):
        self.client = TelegramClient(self.phone_number, self.api_id, self.api_hash)
        return
    
    def _initialize_async_loop(self):
        self.loop = asyncio.get_event_loop()
        return
    
    def _initialize_thread(self):
        self.thread = None
        self.symbols_retrieved_event = threading.Event()
        return
    
    def _add_chat(self, chat_name):
        self.chat_lock.acquire()
        self.chats.append(chat_name)
        self.chat_lock.release()
        return
    
    def wait_for_symbols_retrieved_event(self, timeout=None):
        return self.symbols_retrieved_event.wait(timeout)
    
    def clear_symbols_retrieved_event(self):
        self._clear_symbols_retrieved_event()
        return
    
    def _set_symbols_retrieved_event(self):
        self.symbols_retrieved_event.set()
        return
    
    def _clear_symbols_retrieved_event(self):
        self.symbols_retrieved_event.clear()
        self.retrieved_symbols_lock.acquire()
        self.retrieved_symbols = []
        self.retrieved_symbols_lock.release()
        return
    
    def _set_retrieved_symbols(self, symbol_list):
        self.retrieved_symbols_lock.acquire()
        if self.symbols_retrieved_event.is_set():
            self._clear_symbols_retrieved_event()
        self._set_symbols_retrieved_event()
        self.retrieved_symbols = symbol_list
        self.retrieved_symbols_lock.release()
        return
    
    async def _start_client_with_phone_number(self):
        await self.client.start(phone=self.phone_number)
        return
   
    def _check_if_message_contains_all_keywords(self, message: str, keywords: list):
        message_contains_all_keywords = True
        for keyword in keywords:
            if keyword not in message:
                message_contains_all_keywords = False
                break
        return message_contains_all_keywords

    def _check_if_message_is_coinbase_listing(self, message: str):
        keywords = ['liste', 'Coinbase']
        return self._check_if_message_contains_all_keywords(message, keywords)
    
    def _find_symbols_in_message(self, message: str):
        lines = message.split('\n')
        record_symbol = False
        symbol_list = []
        symbol_str = ""
        for line in lines:
            if self._check_if_message_is_coinbase_listing(line):
                for i in range(0, len(line)):
                    if record_symbol:
                        if line[i] == ' ' or line[i] == '\'' or line[i] == '’':
                            record_symbol = False
                            symbol_list.append(symbol_str)
                            symbol_str = ""
                        else:
                            symbol_str += line[i]
                        if i == len(line) - 1:
                            record_symbol = False

                    if line[i] == '$':
                        record_symbol = True
        if len(symbol_list) > 0:
            self._set_retrieved_symbols(symbol_list)
        return symbol_list
    
    '''
    def _find_symbols_in_message(self, message: str):
        record_symbol = False
        symbol_list = []
        symbol_str = ""
        for i in range(0, len(message)):
            if record_symbol:
                if message[i] == ' ' or message[i] == '\'' or message[i] == '’':
                    record_symbol = False
                    symbol_list.append(symbol_str)
                    symbol_str = ""
                else:
                    symbol_str += message[i]

            if message[i] == '$':
                record_symbol = True
        if len(symbol_list) > 0:
            self._set_retrieved_symbols(symbol_list)
        return symbol_list
    '''
    async def _message_handler(self, event: events.NewMessage.Event):
        self.retrieved_event = event
        message = event.message.message

        chat = await event.get_chat()

        self.message_chat = chat
        username = getattr(chat, 'username', None)

        if username is not None:
            print (f'Username: {username}')
        else:
            print ('No Username Found')
        '''
        symbol_list = self._find_symbols_in_message(message)
        print (symbol_list)
        '''
        self._set_retrieved_message(message)
        self.message_retrieved_event.set()
        '''
        if self._check_if_message_is_coinbase_listing(message):
            # prints the message in Green Colors Using ANSI Escape Codes
            print(f'\033[92m{message}\033[0m')
            symbol_list = self._find_symbols_in_message(message)
            # prints the symbol list in Cyan Colors Using ANSI Escape Codes
            print(f'\033[96m{symbol_list}\033[0m')
        '''
        return
    
    async def _fetch_channel_entities(self):
        self.chat_lock.acquire()
        for chat in self.chats:
            entity = await self.client.get_entity(chat)
            self.chat_entities.append(entity)
        self.chat_lock.release()
        return
    
    def _run_client(self, loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._fetch_channel_entities())
        self.client.add_event_handler(self._message_handler, events.NewMessage(chats=self.chat_entities))
        loop.run_forever()
        #loop.run_until_complete(self.client.run_until_disconnected())
        return
