from chat_bot import EchoBot
import crypto_analysis as ca

import getpass

def main():
    email = input('Email login: ')
    password = getpass.getpass('Password: ')
    client = EchoBot(email, password)
    client.listen()

if __name__ == '__main__':
    main()