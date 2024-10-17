import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    JobQueue,
)
from datetime import time
import pytz
from config import TELEGRAM_BOT_TOKEN, WEATHER_API_KEY

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Чат ID вашего канала или его @username
CHANNEL_CHAT_ID = '@Avramen.pub'  # Или '-1001234567890'

def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'current' in data:
            temp = data['current']['temp_c']
            condition = data['current']['condition']['text']
            wind = data['current']['wind_kph']
            humidity = data['current']['humidity']
            
            return (f"🌤 Погода в *{city.capitalize()}*:\n"
                    f"Температура: *{temp}°C*\n"
                    f"Условия: *{condition}*\n"
                    f"Ветер: *{wind} км/ч*\n"
                    f"Влажность: *{humidity}%*")
        else:
            return "❌ Ошибка: Невозможно получить данные о погоде. Проверьте название города."
    
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка при запросе: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот погоды. Введите название города, и я пришлю вам текущую погоду.\n\n"
        "Например: /weather Калуга"
    )

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        city = ' '.join(context.args)
        weather_info = get_weather(city)
        await update.message.reply_text(weather_info, parse_mode='Markdown')
    else:
        await update.message.reply_text("❗️ Пожалуйста, укажите название города.\n\nНапример: /weather Калуга")

async def send_daily_weather(context: ContextTypes.DEFAULT_TYPE):
    try:
        city = "Калуга"
        weather_info = get_weather(city)
        await context.bot.send_message(chat_id=CHANNEL_CHAT_ID, text=weather_info, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Ошибка при отправке ежедневной погоды: {e}")

def main():
        # Создание приложения бота
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather_command))

    # Настройка ежедневной задачи
    job_queue = application.job_queue

    # Укажите ваш часовой пояс, например, 'Europe/Moscow'
    timezone = pytz.timezone('Europe/Moscow')

    # Время запуска: 9:00 утра
    job_queue.run_daily(
        send_daily_weather,
        time=time(hour=10, minute=19, second=0, tzinfo=timezone),
        name="daily_weather",
    )

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()