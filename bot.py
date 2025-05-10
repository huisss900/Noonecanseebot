from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, Filters, CallbackContext
from pymongo import MongoClient
import os

# 配置：替換為你的值
TOKEN = "7864104470:AAHGkduRhO732c5aCp-pUQBBC9vJiIsOHgU"  # 例如 "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
GROUP_CHAT_ID = "-4720741317"  # 例如 "-1000987654321"
ADMIN_CHANNEL_ID = "-4775110798"  # 例如 "-1001234567890"
MONGO_URI = ""  # 例如 "mongodb+srv://admin:yourpassword@cluster0.mongodb.net"，若不用 MongoDB 可留空 ""

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("歡迎使用匿名發言機器人！請發送消息，我會匿名轉發到群組。")

async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    message_text = update.message.text
    message_id = update.message.message_id

    # 記錄發送者信息到 MongoDB（若不用 MongoDB，依賴管理員頻道）
    if messages:
        messages.insert_one({
            "message_id": message_id,
            "user_id": user.id,
            "username": user.username or "無用戶名",
            "message": message_text
        })

    # 匿名轉發到群組
    sent_message = await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"匿名消息: {message_text}")

    # 發送身份到管理員頻道
    await context.bot.send_message(
        chat_id=ADMIN_CHANNEL_ID,
        text=f"匿名消息 (群組消息ID: {sent_message.message_id})\n發送者: @{user.username or '無用戶名'} (ID: {user.id})\n內容: {message_text}"
    )

async def check_sender(update: Update, context: CallbackContext):
    if update.message.chat_id == int(ADMIN_CHANNEL_ID):
        try:
            message_id = int(context.args[0])
            if messages:
                result = messages.find_one({"message_id": message_id})
                if result:
                    await update.message.reply_text(f"消息ID: {message_id}\n發送者: @{result['username']} (ID: {result['user_id']})\n內容: {result['message']}")
                else:
                    await update.message.reply_text("未找到該消息！")
            else:
                await update.message.reply_text("請檢查管理員頻道記錄，MongoDB 未啟用！")
        except (IndexError, ValueError):
            await update.message.reply_text("請提供有效的消息ID！例如：/checksender 123")
    else:
        await update.message.reply_text("此指令僅限管理員使用！")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, handle_message))
    app.add_handler(CommandHandler("checksender", check_sender))
    app.run_polling()

if __name__ == "__main__":
    main()
