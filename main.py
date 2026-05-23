import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)


load_dotenv()

BOT_TOKEN = os.getenv("8731864768:AAHHqy_15VtRfEYpKji782Bnc9XkoRo_vG8", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "6800590030"))

GROUP_IDS = [
    -1001234567890,   # 1-guruh nomi
    -1009876543210,   # 2-guruh nomi
    -1001122334455,   # 3-guruh nomi
]

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  /start BUYRUG'I
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz.")
        return

    await update.message.reply_text(
        "✅ <b>Salom, Admin!</b>\n\n"
        "Menga xabar yuboring — men uni barcha guruhlarga yuboraman.\n\n"
        f"📋 <b>Ulangan guruhlar:</b> {len(GROUP_IDS)} ta\n\n"
        "📌 <b>Qo'llab-quvvatlanadigan xabar turlari:</b>\n"
        "• Matn\n"
        "• Rasm (caption bilan)\n"
        "• Video (caption bilan)\n"
        "• Fayl/Hujjat\n"
        "• Ovozli xabar\n",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
#  /guruhlar BUYRUG'I — guruh ID larini ko'rish
# ─────────────────────────────────────────────
async def show_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return

    if not GROUP_IDS:
        await update.message.reply_text("⚠️ Hech qanday guruh qo'shilmagan.")
        return

    text = "📋 <b>Guruhlar ro'yxati:</b>\n\n"
    for i, gid in enumerate(GROUP_IDS, 1):
        text += f"{i}. <code>{gid}</code>\n"

    await update.message.reply_text(text, parse_mode="HTML")


# ─────────────────────────────────────────────
#  ASOSIY BROADCAST FUNKSIYASI
# ─────────────────────────────────────────────
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Faqat admin yuborishi mumkin
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Sizda ruxsat yo'q.")
        return

    if not GROUP_IDS:
        await update.message.reply_text("⚠️ Guruhlar ro'yxati bo'sh. config.py ni tekshiring.")
        return

    message      = update.message
    success      = 0
    fail         = 0
    failed_ids   = []

    status_msg = await message.reply_text("⏳ Xabar yuborilmoqda...")

    for group_id in GROUP_IDS:
        try:
            if message.text:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=message.text,
                    parse_mode="HTML"
                )
            elif message.photo:
                await context.bot.send_photo(
                    chat_id=group_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "",
                    parse_mode="HTML"
                )
            elif message.video:
                await context.bot.send_video(
                    chat_id=group_id,
                    video=message.video.file_id,
                    caption=message.caption or "",
                    parse_mode="HTML"
                )
            elif message.document:
                await context.bot.send_document(
                    chat_id=group_id,
                    document=message.document.file_id,
                    caption=message.caption or "",
                    parse_mode="HTML"
                )
            elif message.voice:
                await context.bot.send_voice(
                    chat_id=group_id,
                    voice=message.voice.file_id
                )
            elif message.sticker:
                await context.bot.send_sticker(
                    chat_id=group_id,
                    sticker=message.sticker.file_id
                )
            else:
                await status_msg.edit_text("⚠️ Bu turdagi xabar qo'llab-quvvatlanmaydi.")
                return

            success += 1
            logger.info(f"✅ Yuborildi → {group_id}")

        except Exception as e:
            fail += 1
            failed_ids.append(group_id)
            logger.error(f"❌ Xato ({group_id}): {e}")

    # ── Natija xabari ──
    result = (
        f"📊 <b>Natija:</b>\n"
        f"✅ Muvaffaqiyatli: <b>{success}</b> ta\n"
        f"❌ Xato:           <b>{fail}</b> ta"
    )
    if failed_ids:
        ids_str = "\n".join(f"  • <code>{i}</code>" for i in failed_ids)
        result += f"\n\n⚠️ <b>Xato guruhlar:</b>\n{ids_str}"

    await status_msg.edit_text(result, parse_mode="HTML")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN o'rnatilmagan! .env faylini tekshiring.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("guruhlar", show_groups))

    # Barcha xabar turlarini tinglash
    app.add_handler(MessageHandler(
        filters.TEXT       |
        filters.PHOTO      |
        filters.VIDEO      |
        filters.Document.ALL |
        filters.VOICE      |
        filters.Sticker.ALL,
        broadcast
    ))

    logger.info("🤖 Bot ishga tushdi. To'xtatish uchun Ctrl+C bosing.")
    app.run_polling()


if __name__ == "__main__":
    main()
