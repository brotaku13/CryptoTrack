from chat_bot import EchoBot
import crypto_analysis as ca

import getpass

def main():
    email = input('Facebook login: ')
    password = getpass.getpass('Facebook Password: ')
    client = EchoBot(email, password)
    client.get_email_credentials()
    client.listen()

if __name__ == '__main__':
    main()