import telegram

#Enter the bot token & chat_id and test the file.
my_token = '1111111111:asdfasdfjkl9asdfjkl55lkjfdsaasdfjkl'
chat_id=-9999999999
def send(msg, chat_id, token=my_token):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)

if __name__ == '__main__':
    send("Testing...", chat_id )
