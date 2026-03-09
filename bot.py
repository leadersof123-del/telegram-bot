from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# توكن البوت ومعرفات القنوات
TOKEN = "8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE"
PUBLIC_CHANNEL = -1002099170335
VIP_CHANNEL = -1003887300068

def post_buttons() -> InlineKeyboardMarkup:
    """الأزرار التي تظهر أسفل المنشور المنشور"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 للتسجيل تواصل مع ابو محمد", url="https://t.me/THE_LEADER_Mahmoud")],
        [InlineKeyboardButton("📞 تواصل مع مشرف1", url="https://t.me/LEADERS_OF_TRADING_1")],
        [InlineKeyboardButton("📚 قناة التعليم", url="https://t.me/+UA5eg9wNyX8zNWRk")],
        [InlineKeyboardButton("⏱️ منصة التحليل الفني", url="https://leaders-of-trading.netlify.app")],
        [InlineKeyboardButton("🧑‍💻قنات المؤشرات المجانيه", url="https://t.me/+WWix9LgZXgU0NmFk")],
        [InlineKeyboardButton("💎جميع حسابتنا الرسمية", url="https://t.me/LEADERS_OF_TRADING/30724")],
    ])

def publish_choice_buttons() -> InlineKeyboardMarkup:
    """أزرار التحكم في المسودة (نشر، تعديل، إلغاء)"""
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
        "✅ **البوت جاهز للعمل.**\n\n"
        "أرسل الآن:\n"
        "• نص فقط\n"
        "• صورة مع نص\n"
        "• **فيديو مع نص**\n\n"
        "سأعرض لك معاينة ثم تختار مكان النشر."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🧹 تم مسح المسودة. يمكنك إرسال شيء جديد.")

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID الحالي هو: {update.effective_chat.id}")

async def receive_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استلام المسودة (نص، صورة، أو فيديو) وحفظها للمعاينة"""
    text = update.message.text or update.message.caption or ""
    photo_id = update.message.photo[-1].file_id if update.message.photo else None
    video_id = update.message.video.file_id if update.message.video else None

    # حفظ البيانات في ذاكرة المستخدم المؤقتة
    context.user_data["draft_text"] = text
    context.user_data["draft_photo"] = photo_id
    context.user_data["draft_video"] = video_id

    await update.message.reply_text("👀 **معاينة المنشور قبل النشر:**")

    # عرض المعاينة بناءً على النوع
    if video_id:
        await update.message.reply_video(
            video=video_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )
    elif photo_id:
        await update.message.reply_photo(
            photo=photo_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )
    else:
        await update.message.reply_text(
            text if text else "نص فارغ؟",
            reply_markup=post_buttons(),
            disable_web_page_preview=True
        )

    await update.message.reply_text("اين تريد نشر هذا المنشور؟", reply_markup=publish_choice_buttons())

async def on_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع ضغطات الأزرار (نشر، تعديل، إلغاء)"""
    q = update.callback_query
    await q.answer()

    action = q.data
    text = context.user_data.get("draft_text", "")
    photo_id = context.user_data.get("draft_photo")
    video_id = context.user_data.get("draft_video")

    if action == "cancel_post":
        context.user_data.clear()
        await q.edit_message_text("❌ تم الإلغاء. أرسل منشوراً جديداً في أي وقت.")
        return

    if action == "edit_post":
        context.user_data.clear()
        await q.edit_message_text("✏️ حسناً، أرسل المنشور الجديد الآن.")
        return

    # تحديد الوجهة
    target = PUBLIC_CHANNEL if action == "publish_public" else VIP_CHANNEL
    target_name = "القناة العامة" if action == "publish_public" else "قناة VIP"

    try:
        # عملية النشر الفعلي حسب النوع
        if video_id:
            await context.bot.send_video(
                chat_id=target,
                video=video_id,
                caption=text if text else None,
                reply_markup=post_buttons()
            )
        elif photo_id:
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
        await q.edit_message_text(f"✅ تم النشر بنجاح في {target_name}.")

    except Exception as e:
        await q.edit_message_text(f"❌ حدث خطأ أثناء النشر:\n{e}")

def main():
    app = Application.builder().token(TOKEN).build()

    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("chatid", chatid))

    # استقبال الرسائل (نص، صور، فيديوهات)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_draft))
    app.add_handler(MessageHandler(filters.PHOTO, receive_draft))
    app.add_handler(MessageHandler(filters.VIDEO, receive_draft)) # إضافة فلتر الفيديو

    # التفاعل مع الأزرار
    app.add_handler(CallbackQueryHandler(on_action))

    print("البوت يعمل الآن... اضغط Ctrl+C للإيقاف")
    app.run_polling()

if __name__ == "__main__":
    main()
