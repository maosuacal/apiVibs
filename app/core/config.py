import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USERNAME: str = os.getenv('USER_DB')
    DB_PASSWORD: str = os.getenv('PASSWORD_DB')
    DB_HOST: str = os.getenv('HOST_DB')
    DB_PORT: str = os.getenv('PORT_DB')
    DB_NAME: str = os.getenv('NAME_DB')
    TOKEN_GLUM: str = os.getenv('TOKEN_GLUM')
    TIME_EXP_WSGLUM: str = os.getenv('TIME_EXP_WSGLUM')
    ALGORITM: str = os.getenv('ALGORITM')
    USER_EMAIL_NOTIFICATIONS: str = os.getenv('USER_EMAIL_NOTIFICATIONS')
    PASSWORD_EMAIL_NOTIFICATIONS: str = os.getenv('PASSWORD_EMAIL_NOTIFICATIONS')
    MAIL_HOST: str = os.getenv('MAIL_HOST')
    MAIL_PORT: str = os.getenv('MAIL_PORT')

    @property
    def database_url(self):
        return f'postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

settings = Settings()
