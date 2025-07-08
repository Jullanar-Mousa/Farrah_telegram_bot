from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters
)

# إعداداتك الشخصية
TOKEN = "8115111810:AAEC0pH6LazAXAohWiOR_9X5AVk6sRMFxNA"
OWNER_ID =2073142980

# تخزين الأشخاص يلي عم ترد عليهم
pending_replies = {}

# استقبال رسائل من أي شخص
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text
    username = user.username or "بدون_يوزر"

    # زر الرد
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 رد", callback_data=f"reply:{user_id}")]
    ])

    # إرسال الرسالة لصاحب البوت
    msg = f"💌 رسالة مجهولة من @{username} (ID: {user_id}):\n\n{text}"
    await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=keyboard)

    # إعلام الشخص إنو تم الإرسال
    await update.message.reply_text("✅ تم إرسال رسالتك للمشرف بشكل مجهول.")

# الضغط على زر "رد"
async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.message.reply_text("❌ هذا الزر مخصص للمشرف فقط.")
        return

    data = query.data
    if data.startswith("reply:"):
        target_id = int(data.split(":")[1])
        pending_replies[OWNER_ID] = target_id
        await query.message.reply_text(f"✍️ اكتب الآن الرسالة يلي بدك تبعتها للشخص ID: {target_id}")

# لما المشرف يكتب الرد
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return

    if OWNER_ID not in pending_replies:
        await update.message.reply_text("❗ ما في حدا محدد للرد عليه، اضغط زر (رد) بالأول.")
        return

    target_id = pending_replies.pop(OWNER_ID)
    reply_text = update.message.text

    try:
        await context.bot.send_message(chat_id=target_id, text=f"💬 رد من المشرف:\n{reply_text}")
        await update.message.reply_text("✅ تم إرسال الرد.")
    except Exception as e:
        await update.message.reply_text("❌ فشل الإرسال، يمكن الشخص حظر البوت.")

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً فيك! أرسل أي رسالة وبتوصل للمشرف بشكل مجهول.")

# ربط المعالجات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_reply_button))
app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), handle_admin_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تشغيل البوت
app.run_polling()