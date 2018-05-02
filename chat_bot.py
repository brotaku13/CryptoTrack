from fbchat import log, Client
from fbchat.models import *
import secret
import crypto_analysis as ca
# Subclass fbchat.Client and override required methods
class EchoBot(Client):
    """
    the chat client that listens in to the user's incoming messages and responds to any that match a certain profile
    """

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        """
        This function is run anytime a new message is recieved in the facebook chat
        :param: author_id [str?] -- the author id of the incoming message
        :param: message_object [fbchat.models.message] -- fb message object
        :param: thread_id [str?] -- the id of the thread. 
        :param: thread_type [?] -- 
        :param: **kwargs [?] -- required for API
        """
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        # If you're not the author, echo
        #self.send(message_object, thread_id=thread_id, thread_type=thread_type)
        text = message_object.text.lower().split(' ')
        program_start = text[0]


        if program_start == 'cryptotrack':
            ca.get_data('BTC', '1DAY', 1000)
            print(message_object.text)
            snapshot = ca.create_snapshot()

            ca.print_info(snapshot)

            message = ca.create_message(snapshot, 'BTC')

            if message != '':
                message = 'Greetings from CryptoTrack!\n' + message
                self.send(Message(text=message), thread_id=thread_id, thread_type=thread_type)
            else:
                message = 'Sorry, it appears as if nothing special is happening right now...'
                self.send(Message(text=message), thread_id=thread_id, thread_type=thread_type)

        
        
