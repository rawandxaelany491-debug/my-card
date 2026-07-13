import os
import datetime
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# ✅ پشکنینی ئەلگۆریتمی لون (Luhn)
def is_luhn_valid(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

# ✅ پشکنینی جۆری کارت (ڤیزە/ماستەرکارت)
def get_card_type(card_number):
    if card_number.startswith('4'):
        return "ڤیزە"
    elif (51 <= int(card_number[:2]) <= 55) or (2221 <= int(card_number[:4]) <= 2720):
        return "ماستەرکارت"
    else:
        return "نەناسراو"

# ✅ پشکنینی مانگی بەسەرچوون
def is_expiry_valid(expiry):
    try:
        if len(expiry) == 4:  # فرمانی MMYY
            month = int(expiry[:2])
            year = 2000 + int(expiry[2:])
        elif len(expiry) == 5 and expiry[2] == '/':  # فرمانی MM/YY
            month = int(expiry[:2])
            year = 2000 + int(expiry[3:])
        else:
            return False
        if month < 1 or month > 12:
            return False
        expiry_date = datetime.datetime(year, month, 1)
        return expiry_date > datetime.datetime.now()
    except:
        return False

# ✅ پشکنینی CVV (٣ ژمارە)
def is_cvv_valid(cvv):
    return len(cvv) == 3 and cvv.isdigit()

# 🤖 فەرمانی سەرەکی بۆ پشکنین (گۆڕدراوە بۆ async)
async def verify_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = update.message.text.split()[1:]
        if len(data) != 3:
            await update.message.reply_text("❌ فەرمان هەڵەیە! وەکوو /verify 4111111111111111 05/25 123 بنووسە.")
            return
        
        card_number, expiry, cvv = data

        # پشکنینی ژمارەی کارت
        if not card_number.isdigit() or len(card_number) != 16:
            await update.message.reply_text("❌ ژمارەی کارت هەڵەیە! تەنها ١٦ ژمارە بنووسە.")
            return
        if not is_luhn_valid(card_number):
            await update.message.reply_text("❌ ژمارەی کارت ڕاست نییە (ئەلگۆریتمی لون هەڵە).")
            return
        card_type = get_card_type(card_number)
        if card_type not in ["ڤیزە", "ماستەرکارت"]:
            await update.message.reply_text("❌ تەنها ڤیزە و ماستەرکارت قبوڵ دەکرێت!")
            return

        # پشکنینی مانگی بەسەرچوون
        if not is_expiry_valid(expiry):
            await update.message.reply_text("❌ مانگی بەسەرچوون هەڵەیە! فرمانی دروست: MM/YY (وەکوو 05/25).")
            return

        # پشکنینی CVV
        if not is_cvv_valid(cvv):
            await update.message.reply_text("❌ CVV هەڵەیە! تەنها ٣ ژمارە بنووسە (وەکوو 123).")
            return

        # سەرکەوتن!
        await update.message.reply_text(
            f"✅ فرمانەکانی زیرەکن! \n"
            f"جۆر: {card_type}\n"
            f"مانگی بەسەرچوون: {expiry}\n"
            f"CVV: {cvv} (تەنها درێژی پشکنراوە)"
        )
    except Exception as e:
        await update.message.reply_text("❌ هەڵە! فەرمانەکەت وەکوو /verify 4111111111111111 05/25 123 بنووسە.")

# 🚀 فەرمانی دەستپێکردن (گۆڕدراوە بۆ async)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ سڵاو! بۆ پشکنینی کارت، فەرمانی زیرەک بکە:\n"
        "/verify [ژمارەی کارت] [مانگی بەسەرچوون] [CVV]\n\n"
        "📌 نموونە:\n"
        "/verify 4111111111111111 05/25 123\n\n"
        "⚠️ بیرەوە: ئەم بۆتە تەنها فرمانەکانی زیرەک دەپشکنێت، "
        "هیچ زانیارییەکی ڕاستەقینەی کارت ناچڕدێت!"
    )

# 🔐 چالاککردنی بۆت
def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        print("🚫 هەڵە! توکنی بۆت لە فایلی .env دانەنراوە.")
        print("1. فایلی .env دروست بکە و توکنەکەت لێرە دابنێ:")
        print("   TELEGRAM_TOKEN=توکنی_بۆت_تۆ")
        print("2. پاشان دووبارە بەکاربهێنە.")
        exit(1)
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify_card))

    print("✅ بۆت چالاک بوو! لە تلیگرام بڕۆ و /start بنووسە.")
    application.run_polling()

if __name__ == '__main__':
    main()