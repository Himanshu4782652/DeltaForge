# DeltaForge: Automated Quantitative Options Trading Platform

<p align="center">
  <strong>The Hybrid Python Powerhouse for Low-Latency Multi-Demat Options Execution</strong><br>
  <em>Sensibull-Inspired UI • Dynamic Strike Mathematics • Concurrent Multi-Broker Router • 3:15 PM Hard Exit Risk Engine</em>
</p>

---

## 1. Executive Summary & Vision

**DeltaForge** is an institutional-grade, full-stack quantitative options trading platform engineered to execute algorithmic derivative strategies across multiple broker accounts concurrently. 

Beginning with a lean, zero-overhead execution framework tested across family accounts, DeltaForge is architected to evolve into a fully licensed, SEBI-registered financial technology enterprise by **2028–2029**, managing public asset pools under a structured **5%–10% performance-fee model**.

### Strategic Roadmap
* **Phase 1: Local Framework Pilot (Immediate):** Development of local execution framework across Zerodha, Dhan, and Angel One accounts. Target yield: **~₹25,000 INR/month per account** across 5 family accounts (~₹1,25,000 INR aggregate monthly cash flow).
* **Phase 2: Pilot Validation (Months 1–6):** 6-month live execution trial with internal capital, validating high-probability Greeks decay strategies.
* **Phase 3: Multi-Asset & AI Expansion:** Deploying Crude Oil mid-month theta decay strategies, integrating Chartink/NSE screener pipelines, and training predictive deep learning models on 10+ years of NSE/BSE tick data.
* **Phase 4: Commercial Scale & SEBI Registration (2028–2029 Target):** Acquiring NISM Series VIII & XV certifications, SEBI Research Analyst (RA) registration, and deploying enterprise cloud infrastructure.

---

## 2. Core Stakeholders & Governance

| Stakeholder | Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Himanshu** | **Technical & Architecture Lead** | Microservices engineering, Django state management, FastAPI low-latency calculation engine, HTMX presentation layer, AES-256 broker vault, and sub-100ms multi-account order router. |
| **Aditya (Adi)** | **Quantitative Strategy & NISM Lead** | Options formulas, strike bucket logic, Black-Scholes Greeks models, risk thresholds, NISM Series VIII/XV certifications, and SEBI compliance. |
| **Strategic & Business Lead** | **Business & Capital Allocation** | Business strategy, client acquisition pipeline, operational capital deployment, and commercial scaling. |

---

## 3. High-Level Architecture (Option C: Hybrid Python)

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      1. Pure Python Frontend (HTMX)                    │
 │  - Sensibull-style Strategy Hub (Neutral, Bullish, Bearish Cards)      │
 │  - Index Selector Header (Nifty, Sensex, BankNifty, Crude Oil)         │
 │  - Leg Breakdown Modal & 1-Click "Trade All" Execution                 │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                        (HTMX / Async REST Requests)
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                  2. Django Web Portal (Port 8000)                      │
 │  - Session / JWT Authentication & Role-Based Access Control (RBAC)     │
 │  - Built-in Django Admin (User, Broker Accounts, Audit Logs)          │
 │  - Encrypted Broker Vault (AES-256 Fernet for Zerodha / Dhan / Angel)  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                             (Shared PostgreSQL DB)
                                     │
 ┌───────────────────────────────────┴────────────────────────────────────┐
 │               3. FastAPI Execution Engine (Port 8001)                  │
 │  - /api/v1/strikes/calculate  ➔ Dynamic ATM/ITM Option Formulas       │
 │  - /api/v1/trade/execute      ➔ Concurrent Multi-Broker Order Router   │
 │  - /api/v1/risk/square-off    ➔ 3:15 PM Mandatory Hard Exit Liquidator │
 │  - /ws/live-tickers           ➔ High-Frequency Market Data Stream      │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ Zerodha Kite API  │       │     DhanHQ API    │       │  Angel SmartAPI   │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

---

## 4. Key Functional Modules

### Module 1: Encrypted Multi-Demat Broker Vault
* Stores API credentials and daily session tokens for multiple Demat accounts.
* All access tokens and API secrets are encrypted at rest using **AES-256 Symmetric Encryption** (`cryptography.fernet`).

### Module 2: Sensibull-Style Strategy Hub (Landing UI)
* Interactive Index Selector (**Nifty**, **BankNifty**, **Sensex**, **Crude Oil**) with dynamic expiry day awareness.
* Categorized strategy cards: **Market Neutral** (Delta-Straddles), **Bullish** (Call Spreads), **Bearish** (Put Spreads).
* Dynamic strike generation: Clicking a card computes exact contract strikes based on live spot rates.

### Module 3: Concurrent Multi-Broker Order Router
* Dispatches orders across all linked accounts simultaneously using `asyncio.gather` and `httpx`.
* Target execution latency: **< 100ms**.
* Isolated endpoint resilience: A rejection or timeout on one broker does not block remaining accounts.

### Module 4: 3:15 PM Hard Exit Risk Enforcement
* Automatically squares off all open intraday positions at **3:15 PM** (15 minutes prior to market close).
* **Rationale:** Completely eliminates physical delivery assignment risk for stock options and protects profits from severe late-session illiquidity and cash settlement spikes.

---

## 5. Repository Directory Structure

```text
DeltaForge/
├── manage.py                   # Django management script
├── django_app/                 # Django Core (Port 8000)
│   ├── settings.py             # App settings, DB config, Fernet keys
│   ├── urls.py                 # Core routing
│   ├── wsgi.py / asgi.py
│   └── apps/
│       ├── authentication/     # Custom User model, RBAC (Admin/Analyst/Client)
│       ├── broker_vault/       # Encrypted BrokerAccount model & AES-256 vault
│       └── strategy_manager/   # StrategyConfig, TradeExecutionLog, HTMX views
├── fastapi_app/                # FastAPI Execution Engine (Port 8001)
│   ├── main.py                 # API router & WebSocket feeds
│   ├── options_math/           # Strike selection & Black-Scholes Greeks
│   ├── broker_connectors/      # Zerodha, Dhan, and Angel One SDK wrappers
│   └── execution_router/       # Async parallel order dispatcher
├── templates/                  # Server-rendered HTMX templates
│   ├── base.html               # Header, benchmark toggles, spot feed
│   ├── landing.html            # Strategy catalog & vault status
│   └── components/             # Trade modal, execution banner
├── static/                     # CSS stylesheets & theme assets
├── docs/                       # Project specifications & blueprints
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Container configuration (Postgres, Redis, Django, FastAPI)
└── .env.example                # Environment variable template
```

---

## 6. Getting Started (Local Development)

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/Himanshu4782652/DeltaForge.git
cd DeltaForge

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Secrets
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Generate your AES-256 encryption key using Python:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste the generated key into `FERNET_SECRET_KEY` in your `.env` file.

### 3. Initialize Database & Create Superuser
```bash
python manage.py makemigrations authentication broker_vault strategy_manager
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Microservices

**Terminal 1 — FastAPI Execution Engine (Port 8001):**
```bash
uvicorn fastapi_app.main:app --port 8001 --reload
```

**Terminal 2 — Django Web Portal & HTMX UI (Port 8000):**
```bash
python manage.py runserver 8000
```

Open [http://localhost:8000](http://localhost:8000) to access the **DeltaForge Strategy Hub**, or [http://localhost:8000/admin/](http://localhost:8000/admin/) to manage broker accounts and strategies.

---

## 7. License & Compliance Notice

This software is developed strictly for internal quantitative research and private multi-account execution across authorized accounts. Commercial advisory or asset management operations require compliance with SEBI Research Analyst (RA) regulations and NISM certification standards.
