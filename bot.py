import os
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

TOKEN = os.getenv("BOT_TOKEN") or "8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE"
PUBLIC_CHANNEL = -1002099170335
VIP_CHANNEL = -1003887300068
MAX_ALBUM_PHOTOS = 10


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


def clear_draft_data(context: ContextTypes.DEFAULT_TYPE):
    for key in [
        "draft_type",
        "draft_text",
        "draft_photo",
        "draft_video",
        "draft_album",
        "album_group_id",
        "album_job_name",
    ]:
        context.user_data.pop(key, None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft_data(context)
    await update.message.reply_text(
        "✅ البوت جاهز للعمل.\n\n"
        "أرسل الآن:\n"
        "• نص فقط\n"
        "• صورة مع نص\n"
        "• فيديو مع نص\n"
        "• ألبوم صور حتى 10 صور\n\n"
        "سأعرض لك معاينة ثم تختار مكان النشر."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft_data(context)
    await update.message.reply_text("🧹 تم مسح المسودة. يمكنك إرسال شيء جديد.")


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID الحالي هو: {update.effective_chat.id}")


async def finalize_album(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    user_id = job.data["user_id"]

    user_data = context.application.user_data[user_id]
    album = user_data.get("draft_album", [])
    text = user_data.get("draft_text", "")

    if not album:
        return

    album = album[:MAX_ALBUM_PHOTOS]
    user_data["draft_album"] = album

    media = []
    for i, photo_id in enumerate(album):
        if i == 0 and text:
            media.append(InputMediaPhoto(media=photo_id, caption=text))
        else:
            media.append(InputMediaPhoto(media=photo_id))

    await context.bot.send_message(chat_id=chat_id, text="👀 معاينة الألبوم قبل النشر:")
    await context.bot.send_media_group(chat_id=chat_id, media=media)
    await context.bot.send_message(
        chat_id=chat_id,
        text="🔘 أزرار المنشور:",
        reply_markup=post_buttons()
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text="أين تريد نشر هذا المنشور؟",
        reply_markup=publish_choice_buttons()
    )


async def receive_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # استقبال ألبوم صور
    if message.media_group_id and message.photo:
        media_group_id = message.media_group_id
        photo_id = message.photo[-1].file_id
        text = message.caption or ""

        if context.user_data.get("album_group_id") != media_group_id:
            clear_draft_data(context)
            context.user_data["draft_type"] = "album"
            context.user_data["draft_album"] = []
            context.user_data["album_group_id"] = media_group_id
            context.user_data["draft_text"] = text

        album = context.user_data.get("draft_album", [])

        if photo_id not in album and len(album) < MAX_ALBUM_PHOTOS:
            album.append(photo_id)

        context.user_data["draft_album"] = album

        if text:
            context.user_data["draft_text"] = text

        old_job_name = context.user_data.get("album_job_name")
        if old_job_name:
            for job in context.job_queue.get_jobs_by_name(old_job_name):
                job.schedule_removal()

        job_name = f"album_{message.from_user.id}_{media_group_id}"
        context.user_data["album_job_name"] = job_name

        context.job_queue.run_once(
            finalize_album,
            when=1.5,
            name=job_name,
            data={
                "chat_id": message.chat_id,
                "user_id": message.from_user.id,
            },
        )
        return

    # إذا الرسالة ليست ألبوم، نمسح المسودة القديمة
    clear_draft_data(context)

    text = message.text or message.caption or ""
    photo_id = message.photo[-1].file_id if message.photo else None
    video_id = message.video.file_id if message.video else None

    if video_id:
        context.user_data["draft_type"] = "video"
        context.user_data["draft_video"] = video_id
        context.user_data["draft_text"] = text

        await message.reply_text("👀 معاينة المنشور قبل النشر:")
        await message.reply_video(
            video=video_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    elif photo_id:
        context.user_data["draft_type"] = "photo"
        context.user_data["draft_photo"] = photo_id
        context.user_data["draft_text"] = text

        await message.reply_text("👀 معاينة المنشور قبل النشر:")
        await message.reply_photo(
            photo=photo_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    else:
        context.user_data["draft_type"] = "text"
        context.user_data["draft_text"] = text

        await message.reply_text("👀 معاينة المنشور قبل النشر:")
        await message.reply_text(
            text if text else "نص فارغ؟",
            reply_markup=post_buttons(),
            disable_web_page_preview=True
        )

    await message.reply_text(
        "أين تريد نشر هذا المنشور؟",
        reply_markup=publish_choice_buttons()
    )


async def on_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action = q.data
    draft_type = context.user_data.get("draft_type")
    text = context.user_data.get("draft_text", "")
    photo_id = context.user_data.get("draft_photo")
    video_id = context.user_data.get("draft_video")
    album = context.user_data.get("draft_album", [])

    if action == "cancel_post":
        clear_draft_data(context)
        await q.edit_message_text("❌ تم الإلغاء. أرسل منشوراً جديداً في أي وقت.")
        return

    if action == "edit_post":
        clear_draft_data(context)
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

        elif draft_type == "photo" and photo_id:
            await context.bot.send_photo(
                chat_id=target,
                photo=photo_id,
                caption=text if text else None,
                reply_markup=post_buttons()
            )

        elif draft_type == "album" and album:
            media = []
            for i, pid in enumerate(album[:MAX_ALBUM_PHOTOS]):
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

        else:
            await context.bot.send_message(
                chat_id=target,
                text=text if text else " ",
                reply_markup=post_buttons(),
                disable_web_page_preview=True
            )

        clear_draft_data(context)
        await q.edit_message_text(f"✅ تم النشر بنجاح في {target_name}.")

    except Exception as e:
        await q.edit_message_text(f"❌ حدث خطأ أثناء النشر:\n{e}")


def main():
    if not TOKEN or TOKEN == "PUT_YOUR_NEW_TOKEN_HERE":
        raise ValueError("ضع توكن البوت الصحيح في BOT_TOKEN أو داخل المتغير TOKEN")

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
