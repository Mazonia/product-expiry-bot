import ctypes\ntry:\n    ctypes.windll.kernel32.SetConsoleTitleW('Product-Expiry-Bot')\nexcept Exception:\n    pass\n"""
Telegram Bot Application for Instant Bill & Expiry Date Alert Bot.
"""

import os
import html
import asyncio
from datetime import datetime, date
from pathlib import Path
from loguru import logger

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    BotCommand,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
import database
from vision_extractor import VisionExtractor
from scheduler import start_scheduler, run_daily_check

pending_scans: dict[str, dict] = {}


def is_authorized(user_id: int) -> bool:
    if not config.AUTHORIZED_USER_IDS:
        return True
    return user_id in config.AUTHORIZED_USER_IDS


def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 View All Items", callback_data="cb_list_all"),
            InlineKeyboardButton("💳 Bills & Due Dates", callback_data="cb_list_bills"),
        ],
        [
            InlineKeyboardButton("💊 Medications", callback_data="cb_list_meds"),
            InlineKeyboardButton("🥦 Groceries & Food", callback_data="cb_list_food"),
        ],
        [
            InlineKeyboardButton("🔔 Check Expiries Now", callback_data="cb_check_now"),
        ]
    ])


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome and instructions."""
    text = (
        "💡 <b>INSTANT BILL & EXPIRY DATE ALERT BOT</b> 📦\n\n"
        "Never miss a bill due date or take expired medication again!\n\n"
        "<b>How to track an item:</b>\n"
        "📸 <b>Snap & Send a photo</b> of any utility bill, receipt, medicine package, or food label.\n"
        "AI Vision reads the expiry/due date automatically!\n\n"
        "Or add manually via text:\n"
        "<code>/add Electricity Bill 2026-10-25 Bill 45.50</code>"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive photo, run Vision AI extraction, and show confirmation card."""
    user = update.effective_user
    if not is_authorized(user.id):
        return

    photo = update.message.photo[-1]
    msg = await update.message.reply_text("🔍 <i>Scanning image with Gemini Vision AI...</i>", parse_mode="HTML")

    file_obj = await context.bot.get_file(photo.file_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_path = config.UPLOADS_DIR / f"scan_{user.id}_{timestamp}.jpg"
    await file_obj.download_to_drive(local_path)

    data = VisionExtractor.extract_from_image(local_path)

    import uuid
    scan_id = uuid.uuid4().hex[:8]
    data["user_id"] = user.id
    pending_scans[scan_id] = data

    amt_str = f"\n💰 <b>Amount:</b> <code>${data['amount']:.2f}</code>" if data['amount'] > 0 else ""
    notes_str = f"\n📝 <b>Notes:</b> {html.escape(data['notes'])}" if data['notes'] else ""

    card_text = (
        f"✅ <b>AI VISION SCAN COMPLETE</b>\n"
        f"{'━' * 28}\n\n"
        f"🏷️ <b>Item:</b> <b>{html.escape(data['title'])}</b>\n"
        f"📂 <b>Category:</b> <code>{data['category']}</code>\n"
        f"📅 <b>Expiry / Due Date:</b> <code>{data['expiry_date']}</code>"
        f"{amt_str}"
        f"{notes_str}\n\n"
        f"<i>Confirm to save this into your tracking schedule:</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💾 Save to Tracker", callback_data=f"save_{scan_id}"),
            InlineKeyboardButton("❌ Discard", callback_data=f"discard_{scan_id}"),
        ]
    ])

    await msg.edit_text(card_text, reply_markup=keyboard, parse_mode="HTML")


async def handle_add_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add manual item: /add <title> <YYYY-MM-DD> [category] [amount]."""
    if not is_authorized(update.effective_user.id):
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: <code>/add Electricity 2026-10-25 Bill 45.00</code>", parse_mode="HTML")
        return

    title = args[0]
    exp_date = args[1]
    cat = args[2] if len(args) > 2 else "General"
    amt = float(args[3]) if len(args) > 3 and args[3].replace('.','',1).isdigit() else 0.0

    item_id = database.add_item(update.effective_user.id, title, cat, exp_date, amt)
    await update.message.reply_text(f"✅ Saved <b>{title}</b> (ID #{item_id}) due on <code>{exp_date}</code>!", parse_mode="HTML")


async def render_items_list(update: Update, category: str = None):
    """Render items list with status colors."""
    uid = update.effective_user.id
    items = database.get_active_items(uid, category)
    today = date.today()

    cat_name = category.title() if category else "All Tracked Items"
    if not items:
        text = f"📂 <b>{cat_name}:</b>\n\nNo items active. Send a photo to add!"
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        else:
            await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        return

    lines = [f"📋 <b>{cat_name.upper()}</b>\n" + ("━" * 28)]
    total_bill_amount = 0.0

    for item in items:
        try:
            exp = date.fromisoformat(item["expiry_date"])
            days_left = (exp - today).days
            if days_left < 0:
                badge = f"🔴 Expired ({abs(days_left)}d ago)"
            elif days_left == 0:
                badge = "🚨 Due TODAY!"
            elif days_left <= 3:
                badge = f"⚠️ {days_left}d left"
            elif days_left <= 7:
                badge = f"🟡 {days_left}d left"
            else:
                badge = f"🟢 in {days_left}d"
        except Exception:
            badge = "📅 " + item["expiry_date"]

        amt_str = f" | <code>${item['amount']:.2f}</code>" if item['amount'] > 0 else ""
        if item['amount'] > 0:
            total_bill_amount += item['amount']

        lines.append(f"• [ID:{item['id']}] <b>{html.escape(item['title'])}</b>{amt_str}\n   📅 {item['expiry_date']} — {badge}")

    if total_bill_amount > 0:
        lines.append(f"\n💳 <b>Total Pending Sum:</b> <code>${total_bill_amount:,.2f}</code>")

    lines.append("\n<i>To delete or mark paid:</i> <code>/done <id></code>")
    text = "\n".join(lines)

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark item resolved / deleted: /done <id>."""
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: <code>/done <item_id></code>", parse_mode="HTML")
        return
    item_id = int(context.args[0])
    if database.delete_item(item_id):
        await update.message.reply_text(f"✅ Removed item #{item_id} from tracker.", parse_mode="HTML")
    else:
        await update.message.reply_text(f"❌ Item #{item_id} not found.", parse_mode="HTML")


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interactive button clicks."""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    data = query.data
    if data.startswith("save_"):
        scan_id = data.replace("save_", "")
        item = pending_scans.get(scan_id)
        if item:
            item_id = database.add_item(
                item["user_id"], item["title"], item["category"], item["expiry_date"], item["amount"], item["notes"]
            )
            del pending_scans[scan_id]
            await query.edit_message_text(
                f"🎉 <b>Saved to Tracker!</b>\n\n"
                f"<b>Item:</b> {item['title']}\n"
                f"<b>Due Date:</b> <code>{item['expiry_date']}</code> (ID #{item_id})\n\n"
                f"<i>You will receive automatic alerts before it expires!</i>",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
    elif data.startswith("discard_"):
        scan_id = data.replace("discard_", "")
        if scan_id in pending_scans:
            del pending_scans[scan_id]
        await query.edit_message_text("❌ Discarded.", reply_markup=get_main_keyboard())
    elif data == "cb_list_all":
        await render_items_list(update)
    elif data == "cb_list_bills":
        await render_items_list(update, category="bill")
    elif data == "cb_list_meds":
        await render_items_list(update, category="medication")
    elif data == "cb_list_food":
        await render_items_list(update, category="food")
    elif data == "cb_check_now":
        await query.edit_message_text("🔔 <i>Checking all expiries right now...</i>", parse_mode="HTML")
        await run_daily_check(context.bot)


def main():
    if not config.BOT_TOKEN:
        print("\n⚠️ Error: TELEGRAM_BOT_TOKEN is not set in .env file!")
        print("Please edit C:\\Users\\Mazonia\\Desktop\\Bill-Expiry-Alert-Bot\\.env and add your bot token.\n")
        return

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler(["start", "menu"], handle_start))
    app.add_handler(CommandHandler("add", handle_add_manual))
    app.add_handler(CommandHandler(["done", "delete", "paid"], handle_done))
    app.add_handler(CommandHandler("check", lambda u, c: run_daily_check(c.bot)))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(callback_router))

    async def post_init(application):
        start_scheduler(application.bot)
        try:
            await application.bot.set_my_commands([
                BotCommand("start", "Command Center & Dashboard"),
                BotCommand("add", "Add manual item (e.g. /add Milk 2026-10-25)"),
                BotCommand("done", "Mark item paid/resolved (e.g. /done 1)"),
                BotCommand("check", "Run immediate expiry check"),
            ])
        except Exception:
            pass

    app.post_init = post_init
    logger.info("💡 Bill & Expiry Date Alert Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
