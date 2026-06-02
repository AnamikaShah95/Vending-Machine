# 🕹️ Retro Vending Node Terminal

### Vend | Track | Analyze

**Retro Vending Node** is a futuristic vending machine simulator that blends arcade-style UI with real-time telemetry tracking — built with **Python Flask, SQLite, and Tailwind CSS**.

---

## 📂 Project Structure

```bash
retro-vending-node/
│
├── app.py              # Flask backend service
├── static/             # Frontend assets (HTML, CSS, JS)
├── templates/          # UI templates
├── vending_machine.db  # SQLite database (auto-generated)
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```
---

## ✨ Features

| Feature | Description |
|----------|--------------|
| 🎮 Arcade UI | Neon-styled retro interface with interactive vending cart |
| 🔄 Real-Time Sync | Prevents double-purchases with live stock tracking |
| 💾 SQLite Persistence | Keeps transaction history safe across reloads |
| 📊 Telemetry | Background diagnostics every 4s |
| 💸 Coin System | Drag & drop Rs.10 / Rs.50 tokens to purchase items |

---

## 🚀 Usage

After starting the Flask server (`python app.py`), open your browser and go to:


### 🎮 How to Use
- Insert coins by dragging Rs.10 or Rs.50 tokens into the coin slot.
- Select items using the arcade-style buttons (A–D and 1–4).
- Click **VEND CART** to dispense your selected items.
- Use **RESET** to clear the cart and start fresh.
- Monitor the bottom dashboard for:
  - Gross revenue
  - Order volumes
  - Top category sold
  - Trigger refill option

### Example Workflows
- Insert Rs.50 → Vend Diet Coke  
- Insert Rs.10 → Vend Fanta  
- Insert Rs.60 → Vend Milkshake  

---

## ⚡ Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Install dependencies
pip install flask flask-cors flask-sqlalchemy

# 3. Run the app
python app.py

---




