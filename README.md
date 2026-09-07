# 🔱 Bhola Updates Telegram Forwarder Bot

Custom Telegram Userbot designed for **Bhola Updates**. It monitors the Source channel in real-time, filters out irrelevant messages, and transforms only the 5 target formats into your custom branding.

---

## 🎯 Supported Message Formats & Transformations

1. **ALL RESULTS Summary:**
   * Removes promotional links (`bhai567.org`, etc.).
   * Excludes `SUPREME DAY` and `SUPREME NIGHT` markets.
   * Changes headers to `🔱BHOLA UPDATES🔱`, `🌞DAY RESULTS🌞`, `🌕NIGHT RESULTS🌕`.
   * Appends `🔱BHOLA UPDATES🔱` footer.

2. **Single Market Fast Updates (e.g. TIME BAZAR, KALYAN, etc.):**
   * Formats into:
     ```text
     💰[MARKET NAME] 💰
     ╭───── ✦ ─────╮
     🎯 [DIGITS] 🎯
     ╰───── ✦ ─────╯
     🔱BHOLA UPDATES🔱
     ```

3. **Good Night Greeting:**
   * Converts to:
     ```text
     😴 GOOD NIGHT 😴
     KAL PHIR SE NAYE SHURUAAT
     ```

4. **Good Morning Greeting:**
   * Converts to:
     ```text
     🌄 GOOD MORNING 🌄
     ```

5. **Matka Application / App Promo:**
   * Replaces Bhai 567 ads with the custom **Bhola Ji Office** rate card and contact (`7697113466`).

6. **All Other Messages:**
   * Automatically ignored/skipped.

---

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Bot
Double-click **`start.bat`** (or run `python main.py` in terminal).

### Step 3: Login & Channel Setup
* **On first run**: It will ask for your phone number and Telegram verification code to sign in securely.
* **Select Channels**: If not configured in `.env`, it will show your channels and ask you to select the Source and Destination channels.
