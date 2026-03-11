from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE"
PUBLIC_CHANNEL = -1002099170335
VIP_CHANNEL = -1003887300068

MAX_PHOTOS = 10
PREVIEW_DELAY = 2.0  # عدد الثواني بعد آخر صورة لعرض المعاينة


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


def clear_draft(context: ContextTypes.DEFAULT_TYPE):
    for key in [
        "draft_type",
        "draft_text",
        "draft_photo",
        "draft_video",
        "draft_photos",
        "preview_job_name",
    ]:
        context.user_data.pop(key, None)


async def show_preview(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    user_id = job.data["user_id"]

    user_data = context.application.user_data[user_id]

    draft_type = user_data.get("draft_type")
    text = user_data.get("draft_text", "")
    photo_id = user_data.get("draft_photo")
    video_id = user_data.get("draft_video")
    photos = user_data.get("draft_photos", [])

    if not draft_type:
        return

    await context.bot.send_message(chat_id=chat_id, text="👀 معاينة المنشور قبل النشر:")

    if draft_type == "video" and video_id:
        await context.bot.send_video(
            chat_id=chat_id,
            video=video_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    elif draft_type == "multi_photo" and photos:
        media = []
        for i, pid in enumerate(photos[:MAX_PHOTOS]):
            if i == 0 and text:
                media.append(InputMediaPhoto(media=pid, caption=text))
            else:
                media.append(InputMediaPhoto(media=pid))

        await context.bot.send_media_group(chat_id=chat_id, media=media)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔘 أزرار المنشور:",
            reply_markup=post_buttons()
        )

    elif draft_type == "photo" and photo_id:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text if text else "نص فارغ؟",
            reply_markup=post_buttons(),
            disable_web_page_preview=True
        )

    await context.bot.send_message(
        chat_id=chat_id,
        text="اين تريد نشر هذا المنشور؟",
        reply_markup=publish_choice_buttons()
    )


def reschedule_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    old_job_name = context.user_data.get("preview_job_name")
    if old_job_name:
        for job in context.job_queue.get_jobs_by_name(old_job_name):
            job.schedule_removal()

    job_name = f"preview_{update.effective_user.id}"
    context.user_data["preview_job_name"] = job_name

    context.job_queue.run_once(
        show_preview,
        when=PREVIEW_DELAY,
        name=job_name,
        data={
            "chat_id": update.effective_chat.id,
            "user_id": update.effective_user.id,
        },
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft(context)
    await update.message.reply_text(
        "✅ البوت جاهز للعمل.\n\n"
        "أرسل الآن:\n"
        "• نص فقط\n"
        "• صورة مع نص\n"
        "• فيديو مع نص\n"
        "• عدة صور حتى 10 صور\n\n"
        "وسأعرض لك المعاينة تلقائيًا ثم تختار مكان النشر."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft(context)
    await update.message.reply_text("🧹 تم مسح المسودة. يمكنك إرسال شيء جديد.")


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID الحالي هو: {update.effective_chat.id}")


async def receive_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    text = message.text or message.caption or ""
    photo_id = message.photo[-1].file_id if message.photo else None
    video_id = message.video.file_id if message.video else None

    # فيديو
    if video_id:
        clear_draft(context)
        context.user_data["draft_type"] = "video"
        context.user_data["draft_video"] = video_id
        context.user_data["draft_text"] = text

        await message.reply_text("🎬 تم استلام الفيديو، جاري تجهيز المعاينة...")
        reschedule_preview(update, context)
        return

    # صور متعددة أو صورة واحدة
    if photo_id:
        current_type = context.user_data.get("draft_type")

        if current_type not in [None, "photo", "multi_photo"]:
            clear_draft(context)

        photos = context.user_data.get("draft_photos", [])

        # إذا أول صورة
        if not photos:
            context.user_data["draft_photos"] = [photo_id]
            context.user_data["draft_photo"] = photo_id
            context.user_data["draft_type"] = "photo"
        else:
            if photo_id not in photos:
                if len(photos) >= MAX_PHOTOS:
                    await message.reply_text(f"⚠️ الحد الأقصى {MAX_PHOTOS} صور فقط.")
                    return

                photos.append(photo_id)
                context.user_data["draft_photos"] = photos
                context.user_data["draft_type"] = "multi_photo"

        if text:
            context.user_data["draft_text"] = text

        count = len(context.user_data.get("draft_photos", []))
        await message.reply_text(f"📷 تم استلام {count} صورة، انتظر قليلاً لعرض المعاينة...")
        reschedule_preview(update, context)
        return

    # نص فقط
    clear_draft(context)
    context.user_data["draft_type"] = "text"
    context.user_data["draft_text"] = text

    await message.reply_text("📝 تم استلام النص، جاري تجهيز المعاينة...")
    reschedule_preview(update, context)


async def on_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action = q.data
    draft_type = context.user_data.get("draft_type")
    text = context.user_data.get("draft_text", "")
    photo_id = context.user_data.get("draft_photo")
    video_id = context.user_data.get("draft_video")
    photos = context.user_data.get("draft_photos", [])

    if action == "cancel_post":
        clear_draft(context)
        await q.edit_message_text("❌ تم الإلغاء. أرسل منشورًا جديدًا في أي وقت.")
        return

    if action == "edit_post":
        clear_draft(context)
        await q.edit_message_text("✏️ حسناً، أرسل المنشور الجديد الآن.")
        return

    target = PUBLIC_CHANNEL if action == "publish_public" else VIP_CHANNEL
    target_name = "القناة العامة" if action == "publish_public" else "قناة VIP"

    try:
        if draft_type == "video" and video_id:
            await context.bot.send_video(
                chat_id=target,
                video=video_id,
                caption=text if text else None,
                reply_markup=post_buttons()
            )

        elif draft_type == "multi_photo" and photos:
            media = []
            for i, pid in enumerate(photos[:MAX_PHOTOS]):
                if i == 0 and text:
                    media.append(InputMediaPhoto(media=pid, caption=text))
                else:
                    media.append(InputMediaPhoto(media=pid))

            await context.bot.send_media_group(chat_id=target, media=media)
            await context.bot.send_message(
                chat_id=target,
                text="🔘 الروابط الرسمية:",
                reply_markup=post_buttons()
            )

        elif draft_type == "photo" and photo_id:
            await context.bot.send_photo(
                chat_id=target,
                photo=photo_id,
                caption=text if text else None,
                reply_markup=post_buttons()
            )

        else:
            await context.bot.send_message(
                chat_id=target,
                text=text if text else " ",
                reply_markup=post_buttons(),
                disable_web_page_preview=True
            )

        clear_draft(context)
        await q.edit_message_text(f"✅ تم النشر بنجاح في {target_name}.")

    except Exception as e:
        await q.edit_message_text(f"❌ حدث خطأ أثناء النشر:\n{e}")


def main():
    if TOKEN == "PUT_NEW_TOKEN_HERE":
        raise ValueError("ضع توكن البوت الصحيح مكان TOKEN")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("chatid", chatid))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_draft))
    app.add_handler(MessageHandler(filters.PHOTO, receive_draft))
    app.add_handler(MessageHandler(filters.VIDEO, receive_draft))

    app.add_handler(CallbackQueryHandler(on_action))

    print("البوت يعمل الآن... اضغط Ctrl+C للإيقاف")
    app.run_polling()


if __name__ == "__main__":
    main()
