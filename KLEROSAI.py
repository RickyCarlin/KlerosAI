from src.services.TelethonService import TelethonService
from src.services.TelegramConnectionService import TelegramConnectionService
from src.logic.NewScout import NewScout
from src.services.AppDataService import AppDataService
from src.logic.ArbiSense import SingletonArbiSense

telethon_info = AppDataService.getTelethonAPIInfo()
news_channels = AppDataService.getTelethonNewsChannelsInfo()

telegram_api_id = telethon_info['api_id']
telegram_api_hash = telethon_info['api_hash']
phone_number = telethon_info['phone_number']

ts = TelethonService(telegram_api_id, telegram_api_hash, phone_number)
for channel in news_channels['news_channels']:
    ts.add_chat(channel)

bot_token =  AppDataService.getTelegramBotToken()['telegramBotToken']
chat_ids = AppDataService.getTelegramSubscribedChatIDs()['chatIDs']
tcs = TelegramConnectionService(bot_token)

tcs.set_subscribed_user_ids(chat_ids)

arbisense = SingletonArbiSense.getInstance()
arbisense.set_telegram_connection_service(tcs)
arbisense.start()

ns = NewScout(ts, tcs)

ns.start()

while True:
    try:
        user_input = input("Enter 'q' to stop the program: ")
        if user_input == "q":
            arbisense.stop()
            ns.stop()
            tcs.stop()
            break
    except KeyboardInterrupt:
        arbisense.stop()
        ns.stop()
        tcs.stop()
        break
    except Exception as e:

        print("Error in main loop: " + str(e))
        arbisense.stop()
        ns.stop()
        tcs.stop()
        break
    