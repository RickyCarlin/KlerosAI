from openai import OpenAI
from src.utils.logger import SingletonLogger

class AskQuestionFailedException(Exception):
    pass

class AskKeywordsAndLawsFailedException(Exception):
    pass

class ChatGPTConnectionService:

    def __init__(self):
        self.client = OpenAI()
        self.logger = SingletonLogger.getInstance()
        
    def ask_question_to_gpt(self,
                            question: str):
        prompt = "The messages you will be seeing will be related to the cryptocurrency world, I want you to create a new version of the message in a simplified way and I want you to assess if the message is a bullish news or a bearish news for the cryptocurrency world. Depending on your assessment write either BEARISH or BULLISH to the crypto world at the start of the message. You can use emojis, exclamation marks, and other tools to make the message more exciting. The message you create has to be in English. If the message you receive has indications that it references a photo or video remove those lines from the message and focus on only the news part."
        try:
            chat_completion = self.client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question},
                ]
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            self.logger.log_exception(str(e))
            raise AskQuestionFailedException("Asking question to GPT failed with error: " + str(e))
        