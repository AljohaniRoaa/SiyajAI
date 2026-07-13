<div align="center">

# 🛡️ سياج | Siyaj AI

### Automated PDPL & NDMO Compliance Auditor for Saudi Datasets

*Siyaj (سياج) means "safeguard" in Arabic — a protective check around your data before it moves anywhere else.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Engine-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![PDPL](https://img.shields.io/badge/Compliance-Saudi%20PDPL-0b2545)](#)
[![NDMO](https://img.shields.io/badge/Governance-NDMO-134e4a)](#)

[Features](#-features) • [How It Works](#-how-it-works) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Roadmap](#-roadmap)

</div>

---

## 📋 Overview

**Siyaj AI** is a Streamlit application that lets you upload a CSV or Excel file and instantly see two things:

1. Whether the file contains **unmasked personal or sensitive data** relevant under the **Saudi Personal Data Protection Law (PDPL)**
2. Whether the file meets basic **structural data-quality standards** in line with **National Data Management Office (NDMO)** governance guidance

The result is an executive-style dashboard with a scored risk level, a column-by-column breakdown, and a masked data preview — so sensitive values are never shown on screen in the clear, even inside the audit tool itself.

> **Before a dataset is shared, analyzed, or loaded into another system, someone has to check it for personal data and structural quality.** In most organizations without a dedicated governance function, that check is manual, inconsistent, or skipped entirely. Siyaj AI automates the first pass.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧬 **Dynamic column mapping** | Every column is scanned by its *content*, not its header — mislabeled or generic headers (`col1`, `Unnamed: 0`) don't hide anything |
| 🪪 **Saudi-specific detection** | National ID / Iqama (10 digits, starting with 1 or 2), Saudi mobile numbers (`05xx` / `+966 5xx`), email addresses, and Saudi IBAN format |
| 🔒 **PDPL privacy risk scoring** | Weighted score based on unmasked IDs, contact details, financial identifiers, and header text suggesting special-category data |
| 🗂️ **NDMO governance risk scoring** | Weighted score based on empty columns, generic headers, missing values, and duplicate rows |
| 📊 **Executive dashboard** | Four KPI cards (Overall / PDPL / NDMO / Sensitive Columns Found) plus detail tabs |
| 🧾 **On-screen data masking** | Sensitive columns are automatically masked in the preview (e.g. `10****23`) — nothing sensitive is ever shown in the clear |

---

## ⚙️ How It Works

```
Upload (CSV / XLSX / XLS)
        │
        ▼
Load into a pandas DataFrame
        │
        ▼
Detection Engine — regex-based column classification
  • National ID   • Phone   • Email   • IBAN   • Date-like
        │
        ▼
Compliance Scoring Engine
  ┌─────────────────────┐   ┌──────────────────────┐
  │  PDPL privacy score   │   │  NDMO governance score│
  └─────────────────────┘   └──────────────────────┘
        │                            │
        └───────────┬────────────────┘
                     ▼
        Overall risk = higher of the two
                     │
                     ▼
   Executive Dashboard (KPI cards + 4 tabs)
```

Every classification is a **regex pattern with a documented reason**, and every risk score is a **transparent, addable set of weights** — no external AI/LLM API and no trained ML model are used. If a finding can't be traced back to a specific rule, it isn't in the tool.

---

## 🚀 Installation

```bash
git clone https://github.com/AljohaniRoaa/SiyajAI.git
cd SiyajAI
pip install streamlit pandas openpyxl
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**.

---

## 🖱️ Usage

1. Open the app in your browser
2. Upload a `.csv`, `.xlsx`, or `.xls` file from the sidebar
3. Review the **Executive Summary** cards for Overall / PDPL / NDMO risk
4. Open **Column Mapping** to see how each column was classified
5. Open **PDPL Findings** for specific privacy issues + guidance
6. Open **NDMO Findings** for structural data-quality issues
7. Open **Masked Data Preview** to see the data with sensitive columns hidden

---

## 🧠 Detection Logic

| Type | Pattern | Notes |
|---|---|---|
| National ID | `^(?:1\|2)\d{9}$` | 10 digits — 1 for citizens, 2 for residents/Iqama |
| Phone | `^(?:\+?966[\s\-]?5\d{8}\|0?5\d{8})$` | Saudi mobile format |
| Email | `^[^@\s]+@[^@\s]+\.[^@\s]+$` | Structural email check |
| IBAN | `^SA\d{2}[A-Z0-9]{18}$` | Saudi IBAN format |

A column is classified only if **≥55%** of its sampled values match — otherwise it falls back to a general dtype-based label.

---

## 🛠️ Tech Stack

- **Python 3** — core language
- **Streamlit** — application framework & UI
- **Pandas** — file reading and data manipulation
- **`re` (regex)** — the entire detection engine

No external AI/LLM API calls, no trained ML model — every risk score is rule-based and explainable end to end.

---

## 📁 Project Structure

```
SiyajAI/
├── app.py            # Single-file Streamlit application
├── requirements.txt
└── README.md
```

---

## 🗺️ Roadmap

- [ ] Expand pattern library to more Saudi-specific identifiers (e.g. commercial registration numbers)
- [ ] Reduce reliance on column-header keyword hints for special-category data
- [ ] Exportable audit reports (PDF/Excel)
- [ ] Map findings directly to specific PDPL articles
- [ ] Natural-language summarization layer on top of existing rule-based findings

---

## 👤 Developer

**Roaa Aljohani** — Data Quality & Data Governance Specialist
📧 aljohaniroaawork@gmail.com
🔗 [github.com/AljohaniRoaa](https://github.com/AljohaniRoaa)

---

<div align="center">

*Built for teams who don't have time to check every file by hand.*

</div>
