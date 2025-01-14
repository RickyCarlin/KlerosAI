from openai import OpenAI
from src.utils.logger import SingletonLogger
from src.services.AppDataService import AppDataService

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
        prompt = AppDataService.getGPTPrompt()["prompt"]
        print (str(prompt))
        try:
            chat_completion = self.client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role": "system", "content": str(prompt)},
                    {"role": "user", "content": question},
                ]
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            self.logger.log_exception(str(e))
            raise AskQuestionFailedException("Asking question to GPT failed with error: " + str(e))
        