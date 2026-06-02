========================================================================
PROJECT SYSTEM MANIFEST: RETRO VENDING NODE TERMINAL (COMPLETE UNIFIED TEXT)
========================================================================
Description: This unified text file compiles every single detail, setup guide,
and full configuration files into a single master document.
========================================================================

========================================================================
PART 1: PROJECT OVERVIEW & DOCUMENTATION (README.md)
========================================================================

# 🕹️ Retro Vending Node Terminal

A professional-grade, polyglot-ready automated vending interface built to simulate responsive hardware device interactions. This system couples an interactive, retro-themed arcade frontend UI with a lightweight relational telemetry tracking engine. 

---

## ⚡ Core Engine Features

* **Multi-Item Real-Time Synchronization:** Tracks live product stock schemas locally within the client state registry, automatically blocking phantom double-purchases before hitting network endpoints.
* **Persistent SQLite Tracking Matrix:** Built with file-backed storage arrays to ensure historical analytical datasets survive active runtime service reloads.
* **Dynamic Interactive Overlay Popups:** Features real-time state listeners that intercept remaining unspent currency balances to display dedicated refund and vended asset tracking notification modals.
* **Hardware Telemetry Stream Simulator:** Background execution loops fetch hardware environmental diagnostics periodically every 4,000ms.

---

## 🛠️ System Technology Stack

| Layer | Component Technology | Purpose / Application |
| :--- | :--- | :--- |
| **Frontend** | HTML5 / JavaScript (ES6+) | Direct client-side state manipulation & asynchronous event processing loops |
| **Styling** | Tailwind CSS CDN / CRT Matrix | Atomic styling engine rendering retro arcade layout aesthetics |
| **Backend** | Python / Flask microservice | Exposes REST API pipelines and processes relational telemetry validations |
| **Database** | Flask-SQLAlchemy / SQLite | Models structural transaction schemas and keeps inventory tracking safe |
| **External** | QRCode.js Library | Generates clean client-side dynamic payload streams for UPI routing |

---

## 🚀 Step-by-Step Execution Guide

### 1. Environment Setup & Component Installation
Open your terminal with administrative privileges and install the necessary dependencies:
```bash
pip install flask flask-cors flask-sqlalchemy

# Windows
del vending_machine.db
python app.py

# Mac / Linux
rm -f vending_machine.db
python app.py


