import telebot
from telebot import types
import requests
import uuid
import time
import random
import threading

# --- Configuration ---
API_TOKEN = '8480481449:AAFJTqUbIRF4hg2aPKzJtkXKa0NIAZzWiJc' # BotFather ဆီကရတဲ့ Token ထည့်ပါ
bot = telebot.TeleBot(API_TOKEN)

class TikTokUnlimitedBooster:
    def __init__(self):
        self.base_url = 'https://zefame-free.com/api_free.php'
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        self.device_ids = [str(uuid.uuid4()) for _ in range(15)]
        self.current_idx = 0

    def get_headers(self):
        return {
            'user-agent': random.choice(self.user_agents),
            'accept': 'application/json',
            'origin': 'https://zefame.com',
            'referer': 'https://zefame.com/'
        }

    def get_video_id(self, url):
        try:
            res = self.session.post(self.base_url, headers=self.get_headers(), data={'action': 'checkVideoId', 'link': url}, timeout=10)
            return res.json().get('data', {}).get('videoId') or res.json().get('videoId')
        except: return None

    def place_order(self, url, video_id, service_id):
        try:
            dev_id = self.device_ids[self.current_idx]
            self.current_idx = (self.current_idx + 1) % len(self.device_ids)
            
            data = {
                'action': 'order', 'service': service_id, 'link': url,
                'uuid': dev_id, 'videoId': video_id, 'timestamp': str(int(time.time() * 1000))
            }
            res = self.session.post(f"{self.base_url}?action=order", headers=self.get_headers(), data=data, timeout=10)
            json_res = res.json()
            if json_res.get('success'):
                return True, json_res.get('data', {}).get('orderId', 'N/A')
            return False, json_res.get('message', 'Rate Limit')
        except: return False, "Connection Error"

booster = TikTokUnlimitedBooster()
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('❤️ Like Only', '👁️ View Only', '⚡ Like + View')
    bot.send_message(message.chat.id, "✨ **TikTok Booster Studio** ✨\nအောက်က ခလုတ်တစ်ခုကို ရွေးချယ်ပါ -", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ['❤️ Like Only', '👁️ View Only', '⚡ Like + View'])
def handle_mode(message):
    user_data[message.chat.id] = {'mode': message.text}
    bot.send_message(message.chat.id, "🔢 **Boost လုပ်မယ့် အကြိမ်ရေကို ရိုက်ပါ**\n(ဥပမာ- 100 သို့မဟုတ် 10000 ထိ ရနိုင်သည်)")
    bot.register_next_step_handler(message, handle_amount)

def handle_amount(message):
    try:
        amount = int(message.text)
        if 1 <= amount <= 10000:
            user_data[message.chat.id]['amount'] = amount
            bot.send_message(message.chat.id, "🔗 **TikTok Video Link ကို ပို့ပေးပါ**")
            bot.register_next_step_handler(message, handle_process)
        else: bot.send_message(message.chat.id, "❌ ၁ မှ ၁၀၀၀၀ ကြားပဲ ရိုက်ပေးပါ။")
    except: bot.send_message(message.chat.id, "❌ ဂဏန်းပဲ ရိုက်ပေးပါဗျ။")

def handle_process(message):
    chat_id = message.chat.id
    url = message.text
    if 'tiktok.com' not in url:
        bot.send_message(chat_id, "❌ URL မမှန်ပါ။ /start ကို ပြန်နှိပ်ပါ။")
        return

    user_data[chat_id]['url'] = url
    user_data[chat_id]['running'] = True

    # Stop Button
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛑 STOP BOOSTING", callback_data="stop_task"))
    
    bot.send_message(chat_id, f"🚀 **Boosting စတင်နေပါပြီ...**\n━━━━━━━━━━━━━━\n📌 Mode: {user_data[chat_id]['mode']}\n🔢 Amount: {user_data[chat_id]['amount']}\n━━━━━━━━━━━━━━", reply_markup=markup, parse_mode="Markdown")
    
    threading.Thread(target=core_engine, args=(chat_id,)).start()

def core_engine(chat_id):
    data = user_data[chat_id]
    video_id = booster.get_video_id(data['url'])
    
    if not video_id:
        bot.send_message(chat_id, "❌ Video ID ရှာမတွေ့ပါ။ Link ကို ပြန်စစ်ပေးပါ။")
        return

    # Service IDs: 229 = Views, 232 = Likes
    modes = {
        '❤️ Like Only': [232],
        '👁️ View Only': [229],
        '⚡ Like + View': [229, 232]
    }
    services = modes[data['mode']]

    for i in range(1, data['amount'] + 1):
        if not user_data[chat_id].get('running'):
            bot.send_message(chat_id, "🛑 **လုပ်ငန်းစဉ်ကို ရပ်တန့်လိုက်ပါပြီ။**")
            return

        for s_id in services:
            success, result = booster.place_order(data['url'], video_id, s_id)
            type_label = "View" if s_id == 229 else "Like"
            
            if success:
                bot.send_message(chat_id, f"✅ Process {i}: {type_label} Successful!")
            else:
                bot.send_message(chat_id, f"⚠️ Process {i}: {type_label} Skipped ({result})")
            
            time.sleep(random.uniform(3, 7)) # API Safe Delay

    bot.send_message(chat_id, "🎯 **သတ်မှတ်ထားသော အကြိမ်ရေ အားလုံး ပြီးဆုံးပါပြီ။**")

@bot.callback_query_handler(func=lambda call: call.data == "stop_task")
def stop_callback(call):
    if call.message.chat.id in user_data:
        user_data[call.message.chat.id]['running'] = False
        bot.answer_callback_query(call.id, "ရပ်တန့်ရန် လုပ်ဆောင်နေပါသည်...")

bot.infinity_polling()
