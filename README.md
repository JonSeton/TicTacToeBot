# 🤖 Tic-Tac-Toe Bot

A Python bot that plays optimally on [playtictactoe.org](https://playtictactoe.org) using Selenium and the **minimax** algorithm.

---

## ✅ Features

* 🕹️ Plays on **playtictactoe.org** automatically
* 🧠 Uses **minimax** for unbeatable play
* ❌ Plays as **X** or **O**
* 🔁 Supports **multiple games** in a row
* 🔍 Detects game state, turn order, and restarts
* 🛠️ Recovers from missed moves or browser delays
* 🏆 Handles **wins**, **losses**, and **ties**

---

## 🛠️ Setup

1. Install **Python 3.7+**
2. Install dependencies:

   ```bash
   pip install --user -r requirements.txt
   ```

   > 💡 Use `--user` or run terminal as admin if you get permission errors
3. Install **Google Chrome**
4. WebDriver setup:

   * **No need to download manually!**
   * `webdriver-manager` installs the correct version automatically

---

## ▶️ How to Use

1. Run the bot:

   ```bash
   python tictactoe_bot.py
   ```
2. What happens:

   * Chrome opens and navigates to playtictactoe.org
   * The bot starts playing immediately
   * Handles multiple games automatically
   * Switches between X and O as needed

---

## 🎮 Game Behavior

* **As X**:

  * Makes the first move (usually center)
  * Aims to win or tie with perfect play
* **As O**:

  * Waits for the opponent’s first move
  * Responds with optimal counter-moves
* **Between games**:

  * Detects game end and restarts
  * Adjusts if the opponent restarts or changes sides

---

## 🧩 Troubleshooting

* **Permission Errors**

  * Use `--user` or run your terminal as **administrator**

* **Chrome Issues**

  * Close any open Chrome windows
  * Make sure Chrome is updated

* **Bot Not Detecting Moves**

  * It will auto-recover or restart a new game if needed

---

## 📌 Notes

* Uses **Selenium WebDriver** for browser automation
* Powered by **minimax** for perfect play
* Includes **robust fallback logic** to handle delays or UI quirks
* Reliable across various game scenarios and errors

