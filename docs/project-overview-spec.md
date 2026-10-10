# PROJECT SPECIFICATION: AUTOMATED OPTIONS TRADING PLATFORM

## 1. Executive Summary & Vision
This document defines the high-level functional and technical specification for an **automated options trading platform** designed to execute algorithmic options strategies across multiple broker accounts seamlessly.

### Core Objectives
- **Sensibull + Broker Hybrid Portal**: Deliver a web interface featuring pre-configured strategy cards (Neutral, Bullish, Bearish) with dynamic strike selection and 1-click execution.
- **Automated Options Math**: Dynamically calculate At-The-Money (ATM) and In-The-Money (ITM) strike buckets based on real-time spot prices and index expiry calendars.
- **Multi-Demat Account Execution**: Place parallel orders across multiple connected broker Demat accounts (Zerodha, Dhan, Angel One) in sub-second speed.
- **Strict Risk Control**: Automate intraday time-based exit triggers (3:00 PM / 3:15 PM) to eliminate overnight holding risks and physical assignment penalties.
- **Regulatory Foundation**: Align strategy execution with SEBI/NISM research analyst standards, supporting phased expansion from family accounts to licensed commercial operations.

---

## 2. Core Stakeholders & Role Matrix

| Stakeholder | Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Aditya (Adi)** | Strategy & NISM Lead | Options formulas, strike selection logic, risk thresholds, SEBI compliance, strategy parameter testing. |
| **Software Architect (AI Agent / Dev)** | Technical Lead | Web portal, FastAPI options calculation engine, database models, broker API integration, multi-account parallel order router. |
| **Bhaiya / Lead** | Business & Marketing | Business strategy, client acquisition, funding allocation, long-term commercial scaling. |

---

## 3. High-Level System Architecture (Hybrid Python Powerhouse)

The system utilizes **Option C: Hybrid Python Powerhouse**, combining **Django** for user management, ORM, and admin UI with **FastAPI** for high-concurrency async order execution and market calculations.

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      1. Pure Python Web UI (HTMX)                      │
 │  - Sensibull-style strategy cards (Neutral, Bullish, Bearish)          │
 │  - Index Selector (Nifty | Sensex | BankNifty)                         │
 │  - Dynamic Leg Breakdown & 1-Click "Trade All" Modal                   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼ (Async HTTP / Websockets)
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    2. Web Portal & Admin (Django)                      │
 │  - Auth & Role-Based Access Control (Admin, Analyst, Client)           │
 │  - Encrypted Broker Vault (AES-256 for Zerodha / Dhan / Angel keys)    │
 │  - Django Admin Panel for Strategy Configuration & Audit Logs          │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                             (Shared PostgreSQL DB)
                                     │
 ┌───────────────────────────────────┴────────────────────────────────────┘
 │                  3. Async Execution Engine (FastAPI)                   │
 │  - Real-time Options Calculation Engine (ATM/ITM Buckets via numpy)    │
 │  - Expiry Calendar Auto-Adjuster (Tue: Nifty, Wed: Sensex, Thu: Bank)  │
 │  - Async Concurrent Multi-Broker Router (httpx + asyncio.gather)       │
 │  - 3:00 PM / 3:15 PM Auto Square-Off Background Task                   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ Zerodha Kite API  │       │     DhanHQ API    │       │  Angel SmartAPI   │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

---

## 4. Key Functional Modules to Build

### Module 1: Authentication & Multi-Demat Broker Vault
- **Role-Based Access Control (RBAC)**:
  - `Admin`: Full system control, API health monitoring.
  - `Analyst (Aditya)`: Strategy parameter definition, strike bucket formula updates.
  - `Client`: Linked Demat management, 1-click trade execution.
- **AES-256 Encryption**: Broker API keys and daily access tokens are encrypted using `cryptography.fernet` before saving to PostgreSQL.

### Module 2: Sensibull-Style Strategy Hub (Landing Page)
- **Index Selector**: Quick toggle across **Nifty, Sensex, and BankNifty**.
- **Strategy Cards**: Cards organized by market outlook (Straddles, Strangles, Bull Call Spreads, Bear Put Spreads).
- **HTMX Dynamic Legs**: Selecting a strategy dynamically calculates leg specifics (e.g., *Sell Oct Nifty Call/Put 1 Lot*) based on real-time spot price.
- **1-Click Trade All**: A modal presenting combined margin requirements, max profit/loss, and a single trigger button.

### Module 3: Options Calculation & Expiry Engine
- **Spot & Strike Pricing**: Evaluates spot index prices and selects target strike buckets (ATM, ITM1, OTM1).
- **Index Expiry Calendar Rules**:
  - Tuesday: Nifty Expiry
  - Wednesday: Sensex Expiry
  - Thursday: BankNifty Expiry
- **Real-Time Formula Processing**: Calculates Greeks/pricing using vectorized `numpy`/`pandas` operations in FastAPI.

### Module 4: Concurrent Multi-Broker Execution Router
- **Parallel Dispatch**: When "Trade All" is clicked, FastAPI reads all active linked broker tokens for the user and dispatches parallel HTTP requests using `httpx` and `asyncio.gather`.
- **Sub-Second Latency**: Guarantees synchronous multi-account order placement under 100ms.

### Module 5: Automated Risk Management & Time Triggers
- **3:00 PM / 3:15 PM Auto Square-Off**: Background Celery/FastAPI worker checks open positions and automatically executes market square-off orders prior to close.

---

## 5. Shared Database Schema Overview

```sql
-- Core Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'client', -- 'admin', 'analyst', 'client'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Multi-Demat Broker Credentials Vault
CREATE TABLE broker_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker_name VARCHAR(50) NOT NULL, -- 'zerodha', 'dhan', 'angelone'
    client_id VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    encrypted_access_token TEXT NOT NULL,
    token_expiry TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Strategy Rule Configuration
CREATE TABLE strategy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    target_index VARCHAR(20) NOT NULL, -- 'NIFTY', 'BANKNIFTY', 'SENSEX'
    legs_json JSONB NOT NULL,
    square_off_time TIME DEFAULT '15:00:00',
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 6. Phased Implementation Roadmap

1. **Phase 1: Local Pilot (Zero Cost)**
   - Build Django Auth, Broker Vault, and FastAPI Execution Engine.
   - Test locally using `.env` configurations and family Demat accounts across Zerodha/Dhan/Angel One.
2. **Phase 2: Production Cloud Launch**
   - Deploy Django + FastAPI + PostgreSQL using Docker Compose on cloud hosting.
   - Enable SSL, AES-256 vault security, and live market WebSocket tickers.
3. **Phase 3: Multi-Asset & AI Expansion**
   - Expand execution engine to Commodities (Crude Oil) and Crypto.
   - Integrate historical tick data models for machine-learning-driven strategy optimization.
