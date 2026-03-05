from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE"

# ضع chat_id الحقيقي هنا (بدون "")
PUBLIC_CHANNEL = -1002099170335
VIP_CHANNEL = -1003887300068

def post_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 للتسجيل تواصل مع ابو محمد", url="https://t.me/THE_LEADER_Mahmoud")],
        [InlineKeyboardButton("📞 تواصل مع مشرف1", url="https://t.me/LEADERS_OF_TRADING_1")],
        [InlineKeyboardButton("📚 قناة التعليم", url="https://t.me/+UA5eg9wNyX8zNWRk")],
        [InlineKeyboardButton("⏱️ منصة التحليل الفني", url="https://leaders-of-trading.netlify.app")],
        [InlineKeyboardButton("🧑‍💻قنات المؤشرات المجانيه", url="https://t.me/+WWix9LgZXgU0NmFk")],
        [InlineKeyboardButton("💎جميع حسابتنا الرسمية", url="https://t.me/LEADERS_OF_TRADING/30724")],
    ])
def publish_choice_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 نشر بالقناة العامة", callback_data="publish_public"),
            InlineKeyboardButton("💎 نشر بقناة VIP", callback_data="publish_vip"),
        ],
        [
            InlineKeyboardButton("✏️ تعديل/إعادة إرسال", callback_data="edit_post"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post"),
        ],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "✅ جاهز.\n\n"
        "ارسل الآن:\n"
        "• نص فقط\n"
        "أو\n"
        "• صورة مع نص (Caption)\n\n"
        "وسأعرض لك المعاينة ثم تختار (عامة / VIP)."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🧹 تم مسح المسودة. أرسل منشور جديد.")

# أمر مفيد للتأكد من chat_id للشات الحالي
async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

async def receive_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption or ""
    photo_id = update.message.photo[-1].file_id if update.message.photo else None

    if not text and not photo_id:
        await update.message.reply_text("ارسل نص أو صورة (مع كابشن).")
        return

    context.user_data["draft_text"] = text
    context.user_data["draft_photo"] = photo_id

    await update.message.reply_text("👀 معاينة قبل النشر:")

    if photo_id:
        await update.message.reply_photo(
            photo=photo_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=post_buttons(),
            disable_web_page_preview=True
        )

    await update.message.reply_text("اختر أين تريد نشر المنشور:", reply_markup=publish_choice_buttons())

async def on_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action = q.data
    text = context.user_data.get("draft_text", "")
    photo_id = context.user_data.get("draft_photo")

    if action == "cancel_post":
        context.user_data.clear()
        await q.edit_message_text("❌ تم الإلغاء. أرسل منشور جديد.")
        return

    if action == "edit_post":
        context.user_data.clear()
        await q.edit_message_text("✏️ تمام، أرسل المنشور من جديد (نص أو صورة).")
        return

    if action == "publish_public":
        target = PUBLIC_CHANNEL
        target_name = "القناة العامة"
    elif action == "publish_vip":
        target = VIP_CHANNEL
        target_name = "قناة VIP"
    else:
        return

    try:
        if photo_id:
            await context.bot.send_photo(
                chat_id=target,
                photo=photo_id,
                caption=text if text else None,
                reply_markup=post_buttons()
            )
        else:
            await context.bot.send_message(
                chat_id=target,
                text=text,
                reply_markup=post_buttons(),
                disable_web_page_preview=True
            )

        context.user_data.clear()
        await q.edit_message_text(f"✅ تم النشر في {target_name} بنجاح.")

    except Exception as e:
        await q.edit_message_text(f"❌ فشل النشر في {target_name}:\n{type(e).__name__}: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("chatid", chatid))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_draft))
    app.add_handler(MessageHandler(filters.PHOTO, receive_draft))

    app.add_handler(CallbackQueryHandler(on_action))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":

    main()
