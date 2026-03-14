# 🏥 MSL Account Intelligence Tool

AI-powered pre-call intelligence brief generator for US hospital accounts.
Enter any hospital name and therapeutic area — get an instant structured
account brief with physician profiles, active trials, recent news, and
an AI-generated MSL visit plan in 60 seconds.

---

## 🎯 What It Does

An MSL manually researching a hospital account spends 2-3 hours across
10 different sources. This tool does it in 60 seconds.

**Enter hospital + therapeutic area → get:**
- Hospital profile from NPI Registry
- Key physicians at that institution
- Active clinical trials at that site
- Latest news and developments
- AI-generated MSL visit brief with conversation starters
- Downloadable account brief

---

## 🛠️ Built With

| Tool | Purpose |
|---|---|
| Python | Core language |
| NPI Registry API | US hospital and physician profiles |
| ClinicalTrials.gov API | Active trials at the site |
| Tavily API | Latest news and developments |
| Claude API (Anthropic) | AI-generated MSL visit brief |
| Streamlit | Web interface |

---

## 📁 Project Structure
```
├── npi_search.py          # NPI Registry — hospital and doctor profiles
├── trials_at_site.py      # ClinicalTrials.gov — active trials at location
├── news_search.py         # Tavily — latest news and developments
├── llm_brief.py           # Claude AI — generates MSL visit brief
├── report_generator.py    # Assembles complete account report
├── streamlit_app.py       # Streamlit web interface
├── requirements.txt       # Python dependencies
└── .env.example           # API key template
```

---

## 🚀 Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/LifeSciForge/MSL_Account_Intelligence.git
cd MSL_Account_Intelligence
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API keys**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**5. Run the app**
```bash
streamlit run streamlit_app.py
```

Open browser at `http://localhost:8501`

---

## 💡 Example Searches

| Hospital | State | Specialty | What You Get |
|---|---|---|---|
| Mayo Clinic | MN | oncology | 10 trials, 5 news, full brief |
| MD Anderson Cancer Center | TX | oncology | Trial landscape, KOL profiles |
| Boston Children's Hospital | MA | rare disease | Rare disease trial mapping |
| Johns Hopkins Hospital | MD | neurology | Active trials, recent news |
| Cleveland Clinic | OH | cardiology | Full account intelligence |
| Memorial Sloan Kettering | NY | immunotherapy | CAR-T trial landscape |

---

## 🎯 Target Users

- **MSL** — pre-call visit preparation in 60 seconds
- **KAM** — account planning and prioritisation
- **Medical Affairs** — site identification for investigator-initiated trials
- **BD / Biotech** — partnership and collaboration site mapping
- **Sales Ops** — territory intelligence and mapping

---

## 🔑 API Keys Required

| Key | Source | Cost |
|---|---|---|
| TAVILY_API_KEY | tavily.com | Free tier available |
| ANTHROPIC_API_KEY | console.anthropic.com | Free trial available |

App runs in placeholder mode without API keys —
all hospital, trial, and news data still loads from live sources.

---

## 📊 Data Sources

All data is 100% open and publicly available:

- **NPI Registry** — US government database of 6M+ healthcare providers
- **ClinicalTrials.gov** — US government clinical trials database
- **Tavily** — AI-optimised web search for latest news
- **CMS Open Payments** — pharma payment transparency data (coming soon)

---

## 👤 Author

**Pranjal Das**
AI & Automation for Life Sciences
[github.com/LifeSciForge](https://github.com/LifeSciForge)

---

*Built to demonstrate practical AI application in pharma field and medical affairs operations*
```

---

Press **Cmd + S** → then push to GitHub using Source Control or Terminal:
```
git add .
git commit -m "Update README and rename to MSL Account Intelligence Tool"
git push
