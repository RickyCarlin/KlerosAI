from src.utils.fileutils import FileUtils
from src.utils.paths import *

class AppDataService:

    @staticmethod
    def createAppDataFolderIfNotExists():
        if FileUtils.path_exists(APP_DATA_FOLDER_PATH):
            return
        FileUtils.create_directory_if_not_exists(APP_DATA_FOLDER_PATH)
        return

    @staticmethod
    def createKeysFolderIfNotExists():
        AppDataService.createAppDataFolderIfNotExists()
        if FileUtils.path_exists(KEYS_FOLDER_PATH):
            return
        FileUtils.create_directory_if_not_exists(KEYS_FOLDER_PATH)
        return
    
    @staticmethod
    def createTelegramBotTokenFileIfNotExists():
        if FileUtils.path_exists(TELEGRAM_BOT_TOKEN_FILE_PATH):
            return
        data = {
            "telegramBotToken": ""
        }
        FileUtils.write_json_to_file(TELEGRAM_BOT_TOKEN_FILE_PATH, data)
        return

    @staticmethod
    def getTelegramBotToken():
        AppDataService.createKeysFolderIfNotExists()
        AppDataService.createTelegramBotTokenFileIfNotExists()
        return FileUtils.read_json_from_file(TELEGRAM_BOT_TOKEN_FILE_PATH)
    
    @staticmethod
    def createTelegramSubscribedChatIDsFileIfNotExists():
        if FileUtils.path_exists(TELEGRAM_SUBSCRIBED_CHAT_IDS_FILE_PATH):
            return
        data = {
            "chatIDs": []
        }
        FileUtils.write_json_to_file(TELEGRAM_SUBSCRIBED_CHAT_IDS_FILE_PATH, data)
        return
    
    @staticmethod
    def getTelegramSubscribedChatIDs():
        AppDataService.createAppDataFolderIfNotExists()
        AppDataService.createTelegramSubscribedChatIDsFileIfNotExists()
        return FileUtils.read_json_from_file(TELEGRAM_SUBSCRIBED_CHAT_IDS_FILE_PATH)

    @staticmethod
    def createTelethonAPIInfoFileIfNotExists():
        if FileUtils.path_exists(TELETHON_API_INFO_FILE_PATH):
            return
        data = {
            "api_id": "",
            "api_hash": "",
            "phone_number": ""
        }
        FileUtils.write_json_to_file(TELETHON_API_INFO_FILE_PATH, data)
        return
    
    @staticmethod
    def getTelethonAPIInfo():
        AppDataService.createKeysFolderIfNotExists()
        AppDataService.createTelethonAPIInfoFileIfNotExists()
        return FileUtils.read_json_from_file(TELETHON_API_INFO_FILE_PATH)
    
    @staticmethod
    def createTelethonNewsChannelsInfoFileIfNotExists():
        if FileUtils.path_exists(TELETHON_NEWS_CHANNELS_INFO_FILE_PATH):
            return
        data = {
            "news_channels": []
        }
        FileUtils.write_json_to_file(TELETHON_NEWS_CHANNELS_INFO_FILE_PATH, data)
        return
    
    @staticmethod
    def getTelethonNewsChannelsInfo():
        AppDataService.createKeysFolderIfNotExists()
        AppDataService.createTelethonNewsChannelsInfoFileIfNotExists()
        return FileUtils.read_json_from_file(TELETHON_NEWS_CHANNELS_INFO_FILE_PATH)
    
    @staticmethod
    def createFollowedNewsGroup1FileIfNotExists():
        if FileUtils.path_exists(FOLLOWED_NEWS_GROUP_1_FILE_PATH):
            return
        data = {
            "new_group": []
        }
        FileUtils.write_json_to_file(FOLLOWED_NEWS_GROUP_1_FILE_PATH, data)
        return

    @staticmethod
    def getFollowedNewsGroup1():
        AppDataService.createAppDataFolderIfNotExists()
        AppDataService.createFollowedNewsGroup1FileIfNotExists()
        return FileUtils.read_json_from_file(FOLLOWED_NEWS_GROUP_1_FILE_PATH)
    