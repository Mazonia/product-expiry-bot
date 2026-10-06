# 💡 Instant Bill & Expiry Date Alert Bot

An intelligent Telegram assistant that tracks bills, medication expirations, food best-before dates, and official document renewals with Gemini Vision AI.

## 🌟 Features
- **📸 Snap & Track with AI Vision**: Snap a photo of any receipt, utility bill, medicine box, or grocery packaging. Gemini 2.0 Flash Vision automatically extracts the item name, category, and expiry date.
- **🔔 Proactive Automated Alerts**: Scheduled daily checks alert you:
  - 🚨 **EXPIRED / DUE TODAY**
  - ⚠️ **EXPIRING IN 3 DAYS**
  - 🟡 **EXPIRING IN 7 DAYS**
- **💳 Pending Bills Sum**: Keeps a tally of upcoming expenses and utility due dates.
- **💊 Medication Expiry Protection**: Prevents taking expired medicine with dosage tracking.
- **🥦 Grocery Waste Prevention**: Know what food to eat first before it goes bad.
- **✍️ Manual Entry Supported**: `/add Electricity 2026-10-25 Bill 45.00`.

## 🛠️ Quick Setup
1. Create a bot using [@BotFather](https://t.me/BotFather) on Telegram.
2. Get a free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com).
3. Copy `.env.example` to `.env` and configure:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   AUTHORIZED_USER_IDS=your_telegram_id
   GEMINI_API_KEY=your_gemini_key
   ```
4. Double-click `run.bat` or run:
   ```bash
   python bot.py
   ```
5. Snap and send a photo to your bot in Telegram!
