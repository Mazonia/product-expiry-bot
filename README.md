# 🔔 Instant Bill & Expiry Date Alert Bot

An AI-powered smart assistant for Telegram that tracks bills, payment due dates, medication expirations, food best-before dates, and warranty renewals with Google Gemini Vision AI.

Simply snap and send a photo of any grocery item, medicine box, utility bill, or receipt. The bot automatically extracts the item name, category, and expiry date, tracks it in a local SQLite database, and sends proactive notifications before anything expires or becomes overdue.

---

## ✨ Features & Capabilities

- 📸 **Snap & Track with Gemini Vision AI**: Send a photo directly in Telegram. Google Gemini 2.0 Flash Vision extracts the item details, product name, price/amount, category, and expiry date automatically.
- 🔔 **Proactive Daily Alerts**: Automated background scheduler checks items every morning:
  - 🚨 **EXPIRED / DUE TODAY**: Critical urgency notification.
  - ⚠️ **EXPIRING IN 3 DAYS**: Final reminder notice.
  - 📅 **EXPIRING IN 7 DAYS**: Early warning alert.
- 🧾 **Bill & Expense Management**: Track utility bills, subscriptions, and rent with due dates and pending monetary sums (`/bills`).
- 💊 **Medication Safety Guardian**: Never consume expired medication again.
- 🥬 **Zero Food Waste**: Check expiring fridge and pantry items (`/expiring 5`) to prioritize meal planning.
- ✍️ **Manual Entry Supported**: `/add <Item Name> <YYYY-MM-DD> [Category] [Amount]`.
- 📊 **Quick Inquiries**:
  - `/list` — Display all tracked active items.
  - `/expiring <days>` — View items expiring within the given days.
  - `/bills` — Summary of pending bills and total unpaid amount.
  - `/delete <id>` — Remove an item from the database.
- 🏷️ **Dedicated Windows Process Name**: Runs as `expiry-bot.exe` with console title `Bill-Expiry-Alert-Bot` for instant Task Manager identification.

---

## 📋 Prerequisites & Setup Guide

### 1. Getting a Telegram Bot Token
1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Send `/start` and then `/newbot`.
3. Choose a display name (e.g. `My Expiry Alert Bot`) and a username ending in `bot` (e.g. `john_expiry_alert_bot`).
4. Copy the HTTP API token:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Getting Your Numeric Telegram User ID
1. Search for **[@userinfobot](https://t.me/userinfobot)** in Telegram.
2. Send `/start`.
3. Copy your numeric **Id** (e.g., `987654321`). This is needed for daily alert deliveries.

### 3. Getting a Free Google Gemini API Key
Gemini 2.0 Flash Vision is used for automatic photo OCR and item extraction.
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** / **"Create API key in new project"**.
4. Copy the generated key.
5. Set `GEMINI_API_KEY=...` in your `.env` file.

---

## 🚀 Installation & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Mazonia/product-expiry-bot.git
   cd product-expiry-bot
   ```

2. **Configure your `.env` file**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Fill in your configuration:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   AUTHORIZED_USER_IDS=987654321
   GEMINI_API_KEY=AIzaSy...your_gemini_key_here
   DAILY_CHECK_TIME=09:00
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Bot**:
   - **Option A (Recommended)**: Double-click `run.bat` or execute:
     ```powershell
     .\run.bat
     ```
     *(Runs as `expiry-bot.exe` in Windows Task Manager)*
   - **Option B**:
     ```powershell
     python bot.py
     ```

5. **Start Tracking**:
   - Open your bot in Telegram and send `/start`.
   - Take a photo of any receipt, medicine box, or food expiration label and send it directly!

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
