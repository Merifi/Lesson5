# Телеграм-бот v.004
import json
from gettext import find
from io import BytesIO

import telebot  # pyTelegramBotAPI 4.3.1
from telebot import types
import requests
import bs4
import botGames  # бот-игры, файл botGames.py
from menuBot import Menu  # в этом модуле есть код, создающий экземпляры классов описывающих моё меню


bot = telebot.TeleBot('5198055936:AAEL0Fxv1OTIiW5jCmPfyrea14AfiPCUvUg')  # Создаем экземпляр бота


# -----------------------------------------------------------------------
# Функция, обрабатывающая команды
@bot.message_handler(commands="start")
def command(message, res=False):
    chat_id = message.chat.id
    txt_message = f"Привет, {message.from_user.first_name}! Я тестовый бот для курса программирования на языке Python"
    bot.send_message(chat_id, text=txt_message, reply_markup=Menu.getMenu(chat_id, "Главное меню").markup)


# -----------------------------------------------------------------------
# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    chat_id = message.chat.id
    ms_text = message.text

    result = goto_menu(chat_id, ms_text)  # попытаемся использовать текст как команду меню, и войти в него
    if result == True:
        return  # мы вошли в подменю, и дальнейшая обработка не требуется

    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu != None and ms_text in cur_menu.buttons:  # проверим, что команда относится к текущему меню

        if ms_text == "Помощь":
            send_help(chat_id)

        elif ms_text == "Прислать собаку":
            bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

        elif ms_text == "Прислать анекдот":
            bot.send_message(chat_id, text=get_anekdot())

        elif ms_text == "Прислать фильм":
            send_film(chat_id)

        elif ms_text == "Угадай кто?":
            get_ManOrNot(chat_id)

        elif ms_text == "Карту!":
            game21 = botGames.getGame(chat_id)
            if game21 == None:  # если мы случайно попали в это меню, а объекта с игрой нет
                goto_menu(chat_id, "Выход")
                return

            text_game = game21.get_cards(1)
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

            if game21.status != None:  # выход, если игра закончена
                botGames.stopGame(chat_id)
                goto_menu(chat_id, "Выход")
                return

        elif ms_text == "Стоп!":
            botGames.stopGame(chat_id)
            goto_menu(chat_id, "Выход")
            return


# -----------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # если требуется передать параметр или несколько параметров в обработчик кнопки, использовать методы Menu.getExtPar() и Menu.setExtPar()
    pass
    # if call.data == "ManOrNot_GoToSite": #call.data это callback_data, которую мы указали при объявлении InLine-кнопки
    #
    #     # После обработки каждого запроса нужно вызвать метод answer_callback_query, чтобы Telegram понял, что запрос обработан.
    #     bot.answer_callback_query(call.id)

# -----------------------------------------------------------------------
def goto_menu(chat_id, name_menu):
    # получение нужного элемента меню
    cur_menu = Menu.getCurMenu(chat_id)
    if name_menu == "Выход" and cur_menu != None and cur_menu.parent != None:
        target_menu = Menu.getMenu(chat_id, cur_menu.parent.name)
    else:
        target_menu = Menu.getMenu(chat_id, name_menu)

    if target_menu != None:
        bot.send_message(chat_id, text=target_menu.name, reply_markup=target_menu.markup)

        # Проверим, нет ли обработчика для самого меню. Если есть - выполним нужные команды
        if target_menu.name == "Игра в 21":
            game21 = botGames.newGame(chat_id, botGames.Game21(jokers_enabled=True))  # создаём новый экземпляр игры
            text_game = game21.get_cards(2)  # просим 2 карты в начале игры
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

        return True
    else:
        return False


# -----------------------------------------------------------------------
def getMediaCards(game21):
    medias = []
    for url in game21.arr_cards_URL:
        medias.append(types.InputMediaPhoto(url))
    return medias


# -----------------------------------------------------------------------
def send_help(chat_id):
    global bot
    bot.send_message(chat_id, "Автор: Богатырева Маргарита")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Напишите автору", url="https://t.me/marcyko")
    markup.add(btn1)
    img = open('iam.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=markup)

# -----------------------------------------------------------------------
def send_film(chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n" \
               f"Год: {film['Год']}\n" \
               f"Страна: {film['Страна']}\n" \
               f"Жанр: {film['Жанр']}\n" \
               f"Продолжительность: {film['Продолжительность']}"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="СМОТРЕТЬ онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML', reply_markup=markup)


# -----------------------------------------------------------------------
def get_anekdot():
    array_anekdots = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""

# -----------------------------------------------------------------------
def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
        # url.split("/")[-1]
    return url
# -----------------------------------------------------------------------
def get_ManOrNot(chat_id):
    global bot

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Проверить", url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")
    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")

# ---------------------------------------------------------------------
def get_randomFilm():
    url = 'https://randomfilm.ru/'
    infoFilm = {}
    req_film = requests.get(url)
    soup = bs4.BeautifulSoup(req_film.text, "html.parser")
    result_find = soup.find('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]

    details = result_find.findAll('td')
    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm
# ---------------------------------------------------------------------


bot.polling(none_stop=True, interval=0)  # Запускаем бота

print()
