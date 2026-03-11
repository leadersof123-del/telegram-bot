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

TOKEN = os.getenv("8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE") or "8644761686:AAGqPX7EjFY6NLQ-ib9zqKqRCv8zj6lXlrE"
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
            InlineKeyboardButton("✏️ متابعة الإضافة", callback_data="continue_edit"),
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
        "draft_texts",
        "awaiting_more",
    ]:
        context.user_data.pop(key, None)


def build_combined_text(context: ContextTypes.DEFAULT_TYPE) -> str:
    texts = context.user_data.get("draft_texts", [])
    texts = [t.strip() for t in texts if t and t.strip()]
    return "\n\n".join(texts)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft_data(context)
    await update.message.reply_text(
        "✅ البوت جاهز.\n\n"
        "أرسل:\n"
        "• عدة صفقات كنصوص متعددة\n"
        "• عدة صور واحدة وراء الثانية حتى 10 صور\n"
        "• فيديو واحد مع نص\n\n"
        "بعد ما تخلص أرسل /done\n"
        "وأنا أجمعهم وأعرض لك المعاينة قبل النشر."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft_data(context)
    await update.message.reply_text("🧹 تم مسح المسودة.")


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID الحالي هو: {update.effective_chat.id}")


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    draft_type = context.user_data.get("draft_type")
    text = build_combined_text(context)
    album = context.user_data.get("draft_album", [])
    photo_id = context.user_data.get("draft_photo")
    video_id = context.user_data.get("draft_video")

    if not draft_type:
        await update.message.reply_text("ما في مسودة حالياً. أرسل المحتوى أولاً.")
        return

    await update.message.reply_text("👀 معاينة المنشور قبل النشر:")

    if draft_type == "album" and album:
        media = []
        for i, pid in enumerate(album[:MAX_ALBUM_PHOTOS]):
            if i == 0 and text:
                media.append(InputMediaPhoto(media=pid, caption=text))
            else:
                media.append(InputMediaPhoto(media=pid))
        await update.message.reply_media_group(media=media)
        await update.message.reply_text("🔘 أزرار المنشور:", reply_markup=post_buttons())

    elif draft_type == "photo" and photo_id:
        await update.message.reply_photo(
            photo=photo_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    elif draft_type == "video" and video_id:
        await update.message.reply_video(
            video=video_id,
            caption=text if text else None,
            reply_markup=post_buttons()
        )

    else:
        await update.message.reply_text(
            text if text else "نص فارغ؟",
            reply_markup=post_buttons(),
            disable_web_page_preview=True
        )

    await update.message.reply_text(
        "أين تريد نشر هذا المنشور؟",
        reply_markup=publish_choice_buttons()
    )


async def receive_draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    text = message.text or message.caption or ""
    photo_id = message.photo[-1].file_id if message.photo else None
    video_id = message.video.file_id if message.video else None

    # لو فيديو
    if video_id:
        # الفيديو يكون منفرد
        clear_draft_data(context)
        context.user_data["draft_type"] = "video"
        context.user_data["draft_video"] = video_id
        context.user_data["draft_texts"] = [text] if text else []
        await message.reply_text("✅ تم حفظ الفيديو في المسودة. أرسل /done للمعاينة والنشر.")
        return

    # لو صورة
    if photo_id:
        current_type = context.user_data.get("draft_type")

        if current_type in [None, "album", "photo"]:
            album = context.user_data.get("draft_album", [])

            if not album:
                context.user_data["draft_type"] = "album"

            if len(album) >= MAX_ALBUM_PHOTOS:
                await message.reply_text(f"⚠️ الحد الأقصى {MAX_ALBUM_PHOTOS} صور فقط.")
                return

            album.append(photo_id)
            context.user_data["draft_album"] = album

            texts = context.user_data.get("draft_texts", [])
            if text:
                texts.append(text)
            context.user_data["draft_texts"] = texts

            await message.reply_text(
                f"✅ تم إضافة الصورة رقم {len(album)} إلى المسودة.\n"
                "أرسل المزيد أو أرسل /done."
            )
            return
        else:
            await message.reply_text("⚠️ عندك مسودة من نوع آخر. أرسل /clear أولاً أو /done.")
            return

    # لو نص
    if text:
        current_type = context.user_data.get("draft_type")

        if current_type in [None, "text", "album"]:
            if current_type is None:
                context.user_data["draft_type"] = "text"

            texts = context.user_data.get("draft_texts", [])
            texts.append(text)
            context.user_data["draft_texts"] = texts

            await message.reply_text("✅ تم إضافة النص إلى المسودة. أرسل المزيد أو /done.")
            return

        await message.reply_text("⚠️ عندك مسودة فيديو. أرسل /done أو /clear أولاً.")


async def on_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    action = q.data
    draft_type = context.user_data.get("draft_type")
    text = build_combined_text(context)
    photo_id = context.user_data.get("draft_photo")
    video_id = context.user_data.get("draft_video")
    album = context.user_data.get("draft_album", [])

    if action == "cancel_post":
        clear_draft_data(context)
        await q.edit_message_text("❌ تم الإلغاء.")
        return

    if action == "continue_edit":
        await q.edit_message_text("✏️ أكمل إرسال الصفقات، وبعد الانتهاء أرسل /done")
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

        elif draft_type in ["text", "photo"]:
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
                    text=text if text else " ",
                    reply_markup=post_buttons(),
                    disable_web_page_preview=True
                )
        else:
            await q.edit_message_text("⚠️ لا توجد مسودة صالحة للنشر.")
            return

        clear_draft_data(context)
        await q.edit_message_text(f"✅ تم النشر بنجاح في {target_name}.")

    except Exception as e:
        await q.edit_message_text(f"❌ حدث خطأ أثناء النشر:\n{e}")


def main():
    if not TOKEN or TOKEN == "PUT_YOUR_NEW_TOKEN_HERE":
        raise ValueError("ضع التوكن الصحيح في BOT_TOKEN أو داخل المتغير TOKEN")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler("done", done))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_draft))
    app.add_handler(MessageHandler(filters.PHOTO, receive_draft))
    app.add_handler(MessageHandler(filters.VIDEO, receive_draft))

    app.add_handler(CallbackQueryHandler(on_action))

    print("البوت يعمل الآن... اضغط Ctrl+C للإيقاف")
    app.run_polling()


if __name__ == "__main__":
    main()
