import telebot
from telebot import types

TOKEN = '8963833302:AAF9GkegKkWgfCFtAFRonPYQR7-oQZDXBlI'
bot = telebot.TeleBot(TOKEN)

user_data = {}

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

def get_properties(val):
    if val in ['0', 0, '00']:
        return "🟢 Зеро", "Зеро", "Зеро", "Зеро", "Зеро"
    
    num = int(val)
    color = "🔴 Красное" if num in RED_NUMBERS else "⚫ Черное"
    parity = "🔢 Четное" if num % 2 == 0 else "🔀 Нечетное"
    size = "📉 Малое (1-18)" if 1 <= num <= 18 else "📈 Большое (19-36)"
    
    if 1 <= num <= 12: fraction = "📦 1-я Дюжина"
    elif 13 <= num <= 24: fraction = "📦 2-я Дюжина"
    else: fraction = "📦 3-я Дюжина"
        
    if num % 3 == 1: column = "📊 1-я Колонна"
    elif num % 3 == 2: column = "📊 2-я Колонна"
    else: column = "📊 3-я Колонна"

    return color, parity, size, fraction, column

def analyze_game(chat_id):
    data = user_data[chat_id]
    history = data['history']
    trigger = data['streak']
    base_bet = data['base_bet']
    
    if len(history) < trigger:
        return f"📊 Статистика: {len(history)}/{trigger} чисел для анализа шансов."

    last_elements = history[-trigger:]
    props = [get_properties(v) for v in last_elements]
    
    colors = [p[0] for p in props]
    parities = [p[1] for p in props]
    sizes = [p[2] for p in props]

    signals = []
    has_active_signal = False
    step = data['current_step']
    martingale_bet = base_bet * (2 ** step)

    if all(c == "🔴 Красное" for c in colors):
        signals.append(f"⚠️ СИГНАЛ: Красное X{trigger}!\n👉 СТАВЬ: на ЧЕРНОЕ ⚫\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True
    elif all(c == "⚫ Черное" for c in colors):
        signals.append(f"⚠️ СИГНАЛ: Черное X{trigger}!\n👉 СТАВЬ: на КРАСНОЕ 🔴\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True

    if all(p == "🔢 Четное" for p in parities):
        signals.append(f"⚠️ СИГНАЛ: Четное X{trigger}!\n👉 СТАВЬ: на НЕЧЕТНОЕ 🔀\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True
    elif all(p == "🔀 Нечетное" for p in parities):
        signals.append(f"⚠️ СИГНАЛ: Нечетное X{trigger}!\n👉 СТАВЬ: на ЧЕТНОЕ 🔢\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True

    if all(s == "📉 Малое (1-18)" for s in sizes):
        signals.append(f"⚠️ СИГНАЛ: Малые X{trigger}!\n👉 СТАВЬ: на БОЛЬШИЕ 📈\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True
    elif all(s == "📈 Большое (19-36)" for s in sizes):
        signals.append(f"⚠️ СИГНАЛ: Большие X{trigger}!\n👉 СТАВЬ: на МАЛЫЕ 📉\n💵 СУММА: {martingale_bet:,} $")
        has_active_signal = True

    if has_active_signal:
        data['current_step'] += 1
    else:
        data['current_step'] = 0

    if signals:
        return "\n\n" + "\n⚙️═\n".join(signals)
    else:
        l_color, l_par, _, _, _ = get_properties(history[-1])
        return f"Пока без сигналов.\nПоследний исход ({history[-1]}): {l_color} | {l_par}"

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
    btn_clear = types.KeyboardButton('🔄 Сброс')
    btn_zero = types.KeyboardButton('0')
    btn_dzero = types.KeyboardButton('00')
    btn_settings = types.KeyboardButton('⚙️ Настройки')
    markup.row(btn_clear, btn_zero, btn_dzero, btn_settings)
    
    row = []
    for i in range(1, 37):
        row.append(types.KeyboardButton(str(i)))
        if len(row) == 6:
            markup.row(*row)
            row = []
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_data[message.chat.id] = {'history': [], 'streak': 4, 'base_bet': 1000, 'current_step': 0}
    bot.reply_to(message, "⚙️ Бот рулетки RMRP успешно перезапущен!\nВключен автоматический менеджер догона.", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
def settings_menu(message):
    chat_id = message.chat.id
    if chat_id not in user_data: 
        user_data[chat_id] = {'history': [], 'streak': 4, 'base_bet': 1000, 'current_step': 0}
    
    markup = types.InlineKeyboardMarkup()
    btn_str4 = types.InlineKeyboardButton("Серия: 4 числа", callback_data="set_str_4")
    btn_str5 = types.InlineKeyboardButton("Серия: 5 чисел", callback_data="set_str_5")
    btn_bet1 = types.InlineKeyboardButton("Ставка: 1,000$", callback_data="set_bet_1000")
    btn_bet5 = types.InlineKeyboardButton("Ставка: 5,000$", callback_data="set_bet_5000")
    markup.row(btn_str4, btn_str5)
    markup.row(btn_bet1, btn_bet5)
    
    curr = user_data[chat_id]
    bot.send_message(chat_id, f"🛠 Настройки тактики:\n\n• Длина серии для сигнала: {curr['streak']}\n• Начальная ставка: {curr['base_bet']:,} $", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_'))
def save_settings(call):
    chat_id = call.message.chat.id
    if call.data == "set_str_4": user_data[chat_id]['streak'] = 4
    elif call.data == "set_str_5": user_data[chat_id]['streak'] = 5
    elif call.data == "set_bet_1000": user_data[chat_id]['base_bet'] = 1000
    elif call.data == "set_bet_5000": user_data[chat_id]['base_bet'] = 5000
    
    curr = user_data[chat_id]
    bot.answer_callback_query(call.id, "Настройки сохранены!")
    bot.edit_message_text(f"🛠 Настройки обновлены:\n\n• Длина серии для сигнала: {curr['streak']}\n• Начальная ставка: {curr['base_bet']:,} $", chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        user_data[chat_id] = {'history': [], 'streak': 4, 'base_bet': 1000, 'current_step': 0}

    if text == '🔄 Сброс':
        user_data[chat_id]['history'] = []
        user_data[chat_id]['current_step'] = 0
        bot.send_message(chat_id, "История очищена. Догон обнулен!", reply_markup=get_main_keyboard())
        return

    is_valid_num = text.isdigit() and 0 <= int(text) <= 36
    is_double_zero = (text == '00')

    if is_valid_num or is_double_zero:
        user_data[chat_id]['history'].append(text)
        if len(user_data[chat_id]['history']) > 20:
            user_data[chat_id]['history'].pop(0)
            
        analysis_result = analyze_game(chat_id)
        recent_numbers = " ➔ ".join(user_data[chat_id]['history'][-6:])
        response = f"📋 Лента: {recent_numbers}\n──────────────────{analysis_result}"
        bot.send_message(chat_id, response, reply_markup=get_main_keyboard())

if __name__ == '__main__':
    print("Запуск бота...")
    bot.infinity_polling()
