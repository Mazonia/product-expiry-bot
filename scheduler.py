"""
Automated Daily Expiry & Due Date Alert Scheduler.
Runs background checks and alerts user when items are expiring today, in 3 days, or in 7 days.
"""

import asyncio
from datetime import date, datetime
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database
import config


async def run_daily_check(bot_instance):
    """Scan database and broadcast alerts to authorized users."""
    logger.info("Running automated daily expiry check...")
    today = date.today()
    today_str = today.isoformat()

    items = database.get_items_due_between(days_from_now=7)
    if not items:
        return

    expired = []
    due_3_days = []
    due_7_days = []

    for item in items:
        try:
            exp = date.fromisoformat(item["expiry_date"])
            days_left = (exp - today).days

            if days_left < 0:
                expired.append((item, f"Expired {abs(days_left)} days ago"))
            elif days_left == 0:
                expired.append((item, "DUE TODAY!"))
            elif days_left <= 3:
                due_3_days.append((item, f"{days_left} days left"))
            elif days_left <= 7:
                due_7_days.append((item, f"{days_left} days left"))
        except Exception:
            continue

    if not (expired or due_3_days or due_7_days):
        return

    lines = ["🔔 <b>EXPIRY & BILL DUE DATE DIGEST</b>\n" + ("━" * 28) + "\n"]

    if expired:
        lines.append("🚨 <b>EXPIRED / DUE TODAY:</b>")
        for item, tag in expired:
            amt = f" (${item['amount']:.2f})" if item['amount'] > 0 else ""
            lines.append(f"• <b>{item['title']}</b>{amt} — <code>{tag}</code> (ID: {item['id']})")
        lines.append("")

    if due_3_days:
        lines.append("⚠️ <b>EXPIRING IN 3 DAYS:</b>")
        for item, tag in due_3_days:
            amt = f" (${item['amount']:.2f})" if item['amount'] > 0 else ""
            lines.append(f"• <b>{item['title']}</b>{amt} — <code>{item['expiry_date']}</code> (ID: {item['id']})")
        lines.append("")

    if due_7_days:
        lines.append("🟡 <b>EXPIRING THIS WEEK:</b>")
        for item, tag in due_7_days:
            lines.append(f"• <b>{item['title']}</b> — <code>{item['expiry_date']}</code> (ID: {item['id']})")

    message_text = "\n".join(lines)

    for uid in config.AUTHORIZED_USER_IDS:
        try:
            await bot_instance.send_message(chat_id=uid, text=message_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Could not send reminder to {uid}: {e}")


def start_scheduler(bot_instance):
    """Start APScheduler daily job."""
    scheduler = AsyncIOScheduler()
    hour, minute = config.DAILY_CHECK_TIME.split(":")
    scheduler.add_job(run_daily_check, "cron", hour=int(hour), minute=int(minute), args=[bot_instance])
    scheduler.start()
    logger.info(f"Expiry scheduler started: checking daily at {config.DAILY_CHECK_TIME}")
    return scheduler
