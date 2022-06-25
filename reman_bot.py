# Remote manager Telegram bot
# by Leonty Kopytov @leontyko

import telebot, requests, json
from telebot import types

options = {
	'clients': {
		'Ноутбук': { # имя клиента (для отображения)
			'ip': '127.0.0.1', # ip-адрес клиента
			'port': '8000' # порт клиента
		},
	},
	'token': '', # токен API telegram-бота
	'allowed_chats': [ # чаты с которыми будет общаться бот
		'' # здесь перечисляем id чатов через запятую
	]
}

bot = telebot.TeleBot(options['token'])
context = {}

back_button = '« Назад'
client_prefix = 'Клиент - '
oops = 'Упс.'
success_text = 'Успешно!'
url_prefix = 'url_'
app_prefix = 'app_'

def cat_keyboard(chatId):
	key = types.InlineKeyboardMarkup()
	but_power = types.InlineKeyboardButton(text="Питание", callback_data="Power")
	but_vol = types.InlineKeyboardButton(text="Звук", callback_data="Volume")
	but_url = types.InlineKeyboardButton(text="Ссылка", callback_data="Url")
	but_exec = types.InlineKeyboardButton(text="Приложение", callback_data="Exec")
	but_cancel_power = types.InlineKeyboardButton(text="Отмена задач", callback_data="CancelPower")
	but_return = types.InlineKeyboardButton(text=back_button, callback_data="ClientMenu")
	key.add(but_power, but_vol, but_url, but_exec, but_cancel_power, but_return)
	return key

def pwr_keyboard(chatId):
	key = types.InlineKeyboardMarkup()
	but_shutdown = types.InlineKeyboardButton(text="Выключение", callback_data="shutdown")
	but_reboot = types.InlineKeyboardButton(text="Перезагрузка", callback_data="reboot")
	but_sleep = types.InlineKeyboardButton(text="Сон", callback_data="sleep")
	but_cancel = types.InlineKeyboardButton(text=back_button, callback_data=context[chatId]['client'])
	key.add(but_shutdown, but_reboot, but_sleep, but_cancel)
	return key

def vol_keyboard(chatId):
	key = types.InlineKeyboardMarkup()
	but_up3 = types.InlineKeyboardButton(text="Громче", callback_data="Up3")
	but_down3 = types.InlineKeyboardButton(text="Тише", callback_data="Down3")
	but_up1 = types.InlineKeyboardButton(text="Немного громче", callback_data="Up1")
	but_down1 = types.InlineKeyboardButton(text="Немного тише", callback_data="Down1")
	but_toggle_mute = types.InlineKeyboardButton(text="Звук выкл/вкл", callback_data="Mute")
	but_cancel = types.InlineKeyboardButton(text=back_button, callback_data=context[chatId]['client'])
	key.add(but_up1, but_down1, but_up3, but_down3, but_toggle_mute, but_cancel)
	return key
	
def delay_keyboard():
	key = types.InlineKeyboardMarkup()
	but_now = types.InlineKeyboardButton(text="Сейчас", callback_data="Now")
	but_quorter = types.InlineKeyboardButton(text="Через 15 минут", callback_data="Quorter")
	but_half = types.InlineKeyboardButton(text="Через полчаса", callback_data="Half")
	but_hour = types.InlineKeyboardButton(text="Через час", callback_data="Hour")
	but_one_and_half = types.InlineKeyboardButton(text="Через полтора часа", callback_data="OneAndHalf")
	but_cancel = types.InlineKeyboardButton(text=back_button, callback_data="Power")
	key.add(but_now, but_quorter, but_half, but_hour, but_one_and_half, but_cancel)
	return key

def get_clients(chat_id):
	global context
	context[chat_id] = {}
	key = types.InlineKeyboardMarkup()
	for client in options['clients']:
		key.add(types.InlineKeyboardButton(text=client, callback_data=client))
	return key

def init_chat(chat_id):
	if len(options['clients']) > 0:
		key = get_clients(chat_id)
		bot.send_message(chat_id, "Выберите клиент:", reply_markup=key)
	else:
		bot.send_message(chat_id, "Клиенты не заданы настройках")
	
def reinit_chat(message):
	key = get_clients(message.chat.id)
	bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выберите клиент:", reply_markup=key)

def base_url(client_name):
	client = options['clients'][client_name]
	url = 'http://' + client['ip'] + ':' + client['port'] + '/'
	return url

def pwr_query(message, text):
	global context
	url = base_url(context[message.chat.id]['client'])
	url += 'power'
	delay = 0
	if text == 'Now': delay = 0
	elif text == 'Quorter': delay = 15
	elif text == 'Half': delay = 30
	elif delay == 'Hour': delay = 60
	elif delay == 'OneAndHalf': delay = 90
	else: delay = int(text)
	parameters = dict(cmd=context[message.chat.id]['cmd'], delay=delay)
	try:
		r = requests.get(url, parameters)
		context[message.chat.id].pop('cmd')
		return r
	except Exception as e:
		return

def vol_query(context, data):
	url = base_url(context['client'])
	url += 'volume'
	point = 0
	if data == 'Up3':
		parameters = dict(cmd='up',points=3)
	elif data == 'Down3':
		parameters = dict(cmd='down',points=3)
	elif data == 'Up1':
		parameters = dict(cmd='up',points=1)
	elif data == 'Down1':
		parameters = dict(cmd='down',points=1)
	elif data == 'Mute':
		parameters = dict(cmd='mute')
	try:
		r = requests.get(url, parameters)
		return r
	except Exception as e:
		return

def media_query(context, data):
	url = base_url(context['client'])
	if data.startswith(app_prefix):
		url += 'application'
		data = data.lstrip(app_prefix)
	else:
		url += 'browser'
		data = data.lstrip(url_prefix)
	parameters = dict(cmd=data)
	try:
		r = requests.get(url, parameters)
		return r
	except Exception as e:
		return

def cancel_query(message):
	url = base_url(context['client'])
	url += 'cancel'
	try:
		r = requests.get(url)
		return r
	except:
		return

def test_client(client_name):
	url = base_url(client_name)
	try:
		r = requests.get(url)
		json_str = r.json()
		aDict = json.loads(json_str)
		if aDict['result'] == "ok":
			return True
	except Exception as e:
		return False
	return False

def client_applications(client_name):
	url = base_url(client_name)
	url += 'applications'
	try:
		r = requests.get(url)
		json_str = r.json()
		data = json.loads(json_str)
		if data['result'] == "ok":
			return data['applications']
	except Exception as e:
		return
	return

def client_links(client_name):
	url = base_url(client_name)
	url += 'links'
	try:
		r = requests.get(url)
		json_str = r.json()
		data = json.loads(json_str)
		if data['result'] == "ok":
			return data['links']
	except Exception as e:
		return
	return

def ok_or_fail(cid, result):
	if result['status'] == 'ok':
		bot.answer_callback_query(callback_query_id=cid, text=success_text, show_alert=True)
	else:
		bot.answer_callback_query(callback_query_id=cid, text='Ошибка: ' + result['detail'], show_alert=True)

@bot.message_handler(commands=["start"])
def inline(message):
	chat_id = str(message.chat.id)
	if chat_id in options['allowed_chats']:
		init_chat(message.chat.id)

def openLink(message):
	data = url_prefix + message.text
	try:
		result = media_query(context[message.chat.id], data)
		if result:
			ok_or_fail(c.id, result)
	except Exception as e:
		bot.send_message(message.chat.id, "Произошла ошибка: " + str(e))
	init_chat(message.chat.id)
	
def powerCommand(message):
	if not message.text.isdigit():
		key = delay_keyboard()
		msg = bot.reply_to(message, 'Количество минут должно быть указано в числовом формате. Когда выполнить действие?', reply_markup=key)
		bot.register_next_step_handler(msg, powerCommand)
		return
	try:
		result = pwr_query(message, message.text)
		if result:
			ok_or_fail(c.id, result)
	except Exception as e:
		bot.send_message(message.chat.id, "Произошла ошибка: " + str(e))
	init_chat(message.chat.id)

@bot.callback_query_handler(func=lambda c:True)
def inline(c):
	global context
	chatId = c.message.chat.id
	
	if context.get(chatId) is None:
		context[chatId] = {}
	
	if c.data not in options['clients'] and context.get(chatId) is None and str(chatId) in options['allowed_chats']:
		init_chat(chatId)
	elif c.data in options['clients']:
		available = test_client(c.data)
		if available:
			context[chatId]['client'] = c.data
			key = cat_keyboard(chatId)
			text = client_prefix + context[chatId]['client'] + ". Выберите категорию:"
			bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
		else:
			bot.answer_callback_query(callback_query_id=c.id, text='Клиент не отвечает', show_alert=True)
	elif c.data == 'Power':
		key = pwr_keyboard(chatId)
		text = client_prefix + context[chatId]['client'] + ". Выберите действие:"
		bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
	elif c.data == 'Volume':
		key = vol_keyboard(chatId)
		text = client_prefix + context[chatId]['client'] + ". Выберите действие:"
		bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
	elif c.data == 'Url':
		url_list = client_links(context[chatId]['client'])
		key = types.InlineKeyboardMarkup()
		if url_list and len(url_list)>0:
			for url in url_list:
				url_name = url_prefix + url
				key.add(types.InlineKeyboardButton(text=url, callback_data=url_name))
			text = client_prefix + context[chatId]['client'] + ". Выберите линк или отправьте ссылку сообщением ниже:"
		else:
			text = client_prefix + context[chatId]['client'] + ". Отправьте ссылку сообщением ниже:"
		but_cancel = types.InlineKeyboardButton(back_button, callback_data=context[chatId]['client'])
		key.add(but_cancel)
		bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
		bot.register_next_step_handler(c.message, openLink)
	elif c.data == 'Exec':
		app_list = client_applications(context[chatId]['client'])
		key = types.InlineKeyboardMarkup()
		if app_list and len(app_list)>0:
			for app in app_list:
				app_name = app_prefix + app
				key.add(types.InlineKeyboardButton(text=app, callback_data=app_name))
			text = client_prefix + context[chatId]['client'] + ". Выберите команду:"
		else:
			text = client_prefix + context[chatId]['client'] + ". Список команд пуст"
		but_cancel = types.InlineKeyboardButton(back_button, callback_data=context[chatId]['client'])
		key.add(but_cancel)
		bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
	elif c.data == 'CancelPower':
		try:
			result = cancel_query(c.message)
			if result:
				ok_or_fail(c.id, result)
		except Exception as e:
			bot.answer_callback_query(callback_query_id=c.id, text=oops, show_alert=True)
			return
	elif c.data in ['shutdown', 'reboot', 'sleep']:
		context[chatId]['cmd'] = c.data
		key = delay_keyboard()
		text = client_prefix + context[chatId]['client'] + ". Когда выполнить? Выберите или введите значение в минутах:"
		bot.edit_message_text(chat_id=chatId, message_id=c.message.message_id, text=text, reply_markup=key)
		bot.register_next_step_handler(c.message, powerCommand)
	elif c.data in ['Now', 'Quorter', 'Half', 'Hour', 'OneAndHalf']:
		try:
			result = pwr_query(c.message, c.data)
			if result:
				ok_or_fail(c.id, result)
		except Exception as e:
			bot.answer_callback_query(callback_query_id=c.id, text=oops, show_alert=True)
		reinit_chat(c.message)
	elif c.data in ['Up3', 'Down3', 'Up1', 'Down1', 'Mute']:
		try:
			result = vol_query(context[chatId], c.data)
		except Exception as e:
			bot.answer_callback_query(callback_query_id=c.id, text=oops, show_alert=True)
			reinit_chat(c.message)
	elif c.data.startswith((app_prefix, url_prefix)):
		try:
			result = media_query(context[chatId], c.data)
			if result:
				ok_or_fail(c.id, result)
		except Exception as e:
			bot.answer_callback_query(callback_query_id=c.id, text=oops, show_alert=True)
		reinit_chat(c.message)
	elif c.data == 'ClientMenu':
		reinit_chat(c.message)

bot.infinity_polling()