from telebot import TeleBot, types
import os
from PIL import Image, ImageDraw, ImageFont

TOKEN = "7820975749:AAGu-uu2rDtiXJLDPzTpAU7GMUyqkyeD_Xo"
bot = TeleBot(TOKEN)

MENU_IMAGES = {
    "Basketlar": "1.jpg",
    "Fast-food": "2.jpg",
    "Combo-Chiken": "3.jpg"
}

user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"Привет, {user.first_name}! Пожалуйста, отправьте свой номер телефона!\n"
        "Например: +998xxxxxxxxx"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("Отправить контакт", request_contact=True)
    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Или нажмите на кнопку ниже, чтобы отправить контакт:",
        reply_markup=markup
    )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    bot.send_message(message.chat.id, f"Raqamingiz qabul qilindi: {phone_number}")
    show_main_menu(message.chat.id)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('/'):
        return
        
    if message.text.startswith('+') and len(message.text) > 5:
        bot.send_message(message.chat.id, f"Raqamingiz qabul qilindi: {message.text}")
        show_main_menu(message.chat.id)
    else:
        handle_menu_selection(message)

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Basketlar")
    btn2 = types.KeyboardButton("Fast-food")
    btn3 = types.KeyboardButton("Combo-Chiken")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(chat_id, "Quyidagi menyulardan birini tanlang:", reply_markup=markup)

def handle_menu_selection(message):
    if message.text in MENU_IMAGES:
        image_path = MENU_IMAGES[message.text]
        
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
             
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Buyurtma qilish", callback_data=f"order_{message.text}"))
            bot.send_message(message.chat.id, "Buyurtma qilish uchun tugmani bosing:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Kechirasiz, menyu rasmi topilmadi")

@bot.callback_query_handler(func=lambda call: call.data.startswith('order_'))
def handle_order(call):
    menu_item = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, f"""Siz {menu_item} menyusini tanladingiz! Buyurtmangiz qabul qilindi.
Buyurtma 30 daqiqa ichida yetkazilmasa buyurtmangiz be pul bo'ladi""")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "Rasmga qanday matn yozmoqchisiz?")
    bot.register_next_step_handler(message, process_text_for_photo, message.photo[-1].file_id)

def process_text_for_photo(message, file_id):
    text = message.text
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("temp.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    
    try:
        img = Image.open("temp.jpg")
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        width, height = img.size
        position = ((width - text_width) // 2, (height - text_height) // 2)
        
        draw.text(position, text, fill="white", font=font, stroke_width=2, stroke_fill="black")
        
        output_path = "output.jpg"
        img.save(output_path)
        
        with open(output_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        
        os.remove("temp.jpg")
        os.remove(output_path)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {str(e)}")

def main():
    print("Bot ishga tushdi...")
    bot.remove_webhook()   
    bot.polling(none_stop=True)  
if __name__ == "__main__":
    main()
    bot.polling()