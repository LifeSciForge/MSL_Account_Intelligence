# streamlit_app.py
# =================
# Web interface for the MSL Account Intelligence Tool
# Run with: streamlit run streamlit_app.py
# Opens in browser at localhost:8501

import streamlit as st
from npi_search import (search_hospital, search_doctors,
                         format_hospital_for_llm, format_doctors_for_llm)
from trials_at_site import get_trials_by_specialty, format_trials_for_llm
from news_search import search_hospital_news, format_news_for_llm
from llm_brief import generate_visit_brief
from report_generator import (generate_account_report, format_report_as_text)

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="MSL Account Intelligence Tool",
    page_icon="🏥",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────────
st.title("🏥 MSL Account Intelligence Tool")
st.markdown("""
Generate an instant MSL pre-call intelligence brief for any US hospital.  
**Data sources:** NPI Registry · ClinicalTrials.gov · Tavily News · Claude AI
""")
st.divider()

# ── Input section ────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    hospital_name = st.text_input(
        "Hospital Name",
        placeholder="e.g. Mayo Clinic",
        help="Enter the US hospital name"
    )

with col2:
    state_code = st.text_input(
        "State Code (optional)",
        placeholder="e.g. MN",
        help="2-letter US state code to narrow results"
    )

with col3:
    specialty = st.text_input(
        "Therapeutic Area",
        placeholder="e.g. oncology",
        help="Medical specialty or disease area"
    )

# ── Generate button ───────────────────────────────────────────────
generate_button = st.button(
    "🔍 Generate Account Brief",
    type="primary",
    use_container_width=True
)

# ── Results ───────────────────────────────────────────────────────
if generate_button:
    
    if not hospital_name or not specialty:
        st.error("Please enter both a hospital name and therapeutic area.")
        st.stop()
    
    # Progress tracking
    progress = st.progress(0)
    status = st.empty()
    
    # Step 1 — Hospital profile
    status.text("🏥 Searching NPI Registry for hospital profile...")
    progress.progress(15)
    hospitals = search_hospital(hospital_name, state=state_code or None)
    
    # Step 2 — Key doctors
    status.text("👨‍⚕️ Finding key physicians...")
    progress.progress(30)
    # City lookup map for major hospitals
    city_map = {
        "md anderson": "Houston",
        "mayo clinic": "Rochester",
        "johns hopkins": "Baltimore",
        "memorial sloan kettering": "New York",
        "cleveland clinic": "Cleveland",
        "boston children": "Boston",
        "massachusetts general": "Boston",
        "ucla": "Los Angeles",
        "ucsf": "San Francisco",
    }
    
    # Find city from hospital name
    hospital_lower = hospital_name.lower()
    city_guess = next(
        (city for key, city in city_map.items() if key in hospital_lower),
        hospital_name.split()[0]  # fallback to first word
    )
    
    doctors = search_doctors(city_guess, state=state_code or None)
    
    # Step 3 — Clinical trials
    status.text("🔬 Searching active clinical trials...")
    progress.progress(50)
    trials = get_trials_by_specialty(hospital_name, specialty)
    
    # Step 4 — News
    status.text("📰 Fetching latest news...")
    progress.progress(65)
    news_articles = search_hospital_news(
        hospital_name,
        state=state_code or None
    )
    
    # Step 5 — Format for LLM
    hospital_text = format_hospital_for_llm(hospitals[0]) if hospitals else f"Hospital: {hospital_name}"
    doctors_text = format_doctors_for_llm(doctors)
    trials_text = format_trials_for_llm(trials, hospital_name)
    news_text = format_news_for_llm(news_articles, hospital_name)
    
    # Step 6 — Generate AI brief
    status.text("🤖 Generating MSL visit brief...")
    progress.progress(80)
    llm_brief = generate_visit_brief(
        hospital_name, specialty,
        hospital_text, doctors_text,
        trials_text, news_text
    )
    
    # Step 7 — Assemble report
    status.text("📄 Assembling account report...")
    progress.progress(95)
    report = generate_account_report(
        hospital_name, specialty,
        hospitals, doctors, trials,
        news_articles, llm_brief
    )
    
    progress.progress(100)
    status.text("✅ Account brief complete!")
    
    st.divider()
    
    # ── Summary metrics ──────────────────────────────────────────
    st.subheader("📊 Account Snapshot")
    stats = report["summary_stats"]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Physicians Found", stats["doctors_found"])
    m2.metric("Active Trials", stats["active_trials"])
    m3.metric("Trial Sponsors", stats["unique_sponsors"])
    m4.metric("News Articles", stats["news_articles"])
    
    st.divider()
    
    # ── Hospital profile ─────────────────────────────────────────
    st.subheader("🏥 Hospital Profile")
    if report["hospital_profile"]:
        for h in report["hospital_profile"]:
            with st.expander(h["name"]):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**NPI:** {h['npi']}")
                    st.write(f"**Address:** {h['address']}")
                with col_b:
                    st.write(f"**Phone:** {h['phone']}")
                    st.write(f"**Specialty:** {h['specialty']}")
                if h["npi_url"]:
                    st.link_button("View NPI Record", h["npi_url"])
    else:
        st.info("No hospital profile found in NPI Registry.")
    
    st.divider()
    
    # ── Key physicians ───────────────────────────────────────────
    st.subheader("👨‍⚕️ Key Physicians")
    if report["key_doctors"]:
        for doc in report["key_doctors"][:8]:
            with st.expander(f"{doc['name']} {doc['credential']} — {doc['specialty']}"):
                st.write(f"**Location:** {doc['location']}")
                st.write(f"**Phone:** {doc['phone']}")
                if doc["npi_url"]:
                    st.link_button("View NPI Profile", doc["npi_url"])
    else:
        st.info("No physicians found.")
    
    st.divider()
    
    # ── Clinical trials ──────────────────────────────────────────
    st.subheader("🔬 Active Clinical Trials")
    if report["trials_section"]:
        for trial in report["trials_section"]:
            with st.expander(f"{trial['nct_id']} — {trial['title'][:70]}..."):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Phase:** {trial['phase']}")
                    st.write(f"**Status:** {trial['status']}")
                    st.write(f"**Sponsor:** {trial['sponsor']}")
                with col_b:
                    st.write(f"**Endpoint:** {trial['endpoint']}")
                    st.write(f"**Completion:** {trial['completion_date']}")
                st.link_button("View on ClinicalTrials.gov", trial["url"])
    else:
        st.info("No active trials found at this site.")
    
    st.divider()
    
    # ── Recent news ──────────────────────────────────────────────
    st.subheader("📰 Recent News")
    if report["news_section"]:
        for article in report["news_section"]:
            with st.expander(article["title"]):
                st.write(article["preview"])
                st.link_button("Read Full Article", article["url"])
    else:
        st.info("No recent news found.")
    
    st.divider()
    
    # ── MSL Visit Brief ──────────────────────────────────────────
    st.subheader("🤖 MSL Visit Brief")
    
    if report["brief_status"] == "placeholder":
        st.warning(
            "⚠️ Showing placeholder brief. "
            "Add ANTHROPIC_API_KEY to .env to activate real Claude AI analysis."
        )
    
    st.markdown(report["visit_brief"])
    
    st.divider()
    
    # ── Download ─────────────────────────────────────────────────
    st.subheader("📥 Download Account Brief")
    report_text = format_report_as_text(report)
    st.download_button(
        label="Download Full Brief as Text",
        data=report_text,
        file_name=f"account_brief_{hospital_name}_{specialty}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ── Footer ────────────────────────────────────────────────────────
st.divider()
st.caption(
    "MSL Account Intelligence Tool · "
    "Data: NPI Registry + ClinicalTrials.gov + Tavily · "
    "Built by Pranjal Das · github.com/LifeSciForge"
)