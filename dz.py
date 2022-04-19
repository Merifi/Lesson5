#1,2
def dz1(bot, chat_id):
    bot.send_message(chat_id, text='Марго')
def dz2(bot, chat_id):
    bot.send_message(chat_id, text='18')
def dz3(bot, chat_id):
    bot.send_message(chat_id, text='доделать')
def dz4(bot, chat_id):
    bot.send_message(chat_id, text='доделать')
def dz5(bot, chat_id):
    my_inputInt(bot, chat_id, "Сколько вам лет?",  dz5_ResponseHandler)
def dz5_ResponseHandler(bot, chat_id, age_int):
    bot.send_message(chat_id, text=f'О!тебе уже {age_int}!\nА через год будет уже {age_int+1}!!!')
def dz6(bot, chat_id):
    dz6_ResponseHandler=lambda message:bot.send_message(chat_id, f'Добро пожаловать{message.text}!У тебя красивое имя, в нем {len(message.text)}букв!')
    my_input(bot, chat_id, 'Как тебя зовут?', dz6_ResponseHandler)

def my_inputInt_SecondPart(message, botQuestion, txtQuestion, ResponseHandler):
    chat_id=message.chat.id
    try:
        var_int=int(message.text)
        #данные коректно преобразились в int, можно вызвать обработчик ответа, и передать туда наше число
        ResponseHandler(botQuestion, chat_id, var_int)
    except ValueError:
        botQuestion.send-message(chat_id, text=' Можно вводить только целое число в десятичной системе исчисления(символы от 0 до 9)!\nПопробуй еще раз...')
        my_inputInt(botQuestion, chat_id, txtQuestion, ResponseHandler) #это не рекурсия, но очень похоже
        # у нас пара процедур, которые вызывают друг-друга, пока пользователь не введет корректные данные, и
        # тогда этот цикл прервется, и управление перейдет "наружу" , в ResponseHandler

