from chat_bot import EchoBot
import crypto_analysis as ca
import secret

def main():
    client = EchoBot(secret.EMAIL, secret.PASSWORD)
    client.listen()

if __name__ == '__main__':
    main()