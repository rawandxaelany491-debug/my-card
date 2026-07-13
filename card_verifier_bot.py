# ئەم بەشە تەنها بۆ وەشانی 20.6ی python-telegram-botە
from telegram.ext import Application  # ← گۆڕانکاری لە وەشانی نوێ

def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        print("🚫 هەڵە! توکنی بۆت لە فایلی .env دانەنراوە.")
        exit(1)
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify_card))

    print("✅ بۆت چالاک بوو! لە تلیگرام بڕۆ و /start بنووسە.")
    application.run_polling()

if __name__ == '__main__':
    main()