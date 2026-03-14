# report_generator.py
# ====================
# Assembles all data into a complete MSL account brief
# Takes outputs from all other modules and builds
# a structured, downloadable account report

from datetime import datetime

def generate_account_report(hospital_name, specialty, 
                             hospitals, doctors, trials, 
                             news_articles, llm_brief):
    """
    Assemble all data into a complete account report.
    
    Args:
        hospital_name: Name of the hospital
        specialty: Therapeutic area
        hospitals: List from npi_search.py
        doctors: List from npi_search.py
        trials: List from trials_at_site.py
        news_articles: List from news_search.py
        llm_brief: Dictionary from llm_brief.py
    
    Returns:
        Dictionary with complete account report
    """
    
    print(f"Assembling account report for {hospital_name}...")
    
    report = {
        "title": f"MSL Account Brief: {hospital_name}",
        "hospital_name": hospital_name,
        "specialty": specialty,
        "generated_at": datetime.now().strftime("%B %d, %Y at %H:%M"),
        "summary_stats": build_summary_stats(
            hospitals, doctors, trials, news_articles
        ),
        "hospital_profile": build_hospital_profile(hospitals),
        "key_doctors": build_doctors_section(doctors),
        "trials_section": build_trials_section(trials),
        "news_section": build_news_section(news_articles),
        "visit_brief": llm_brief.get("brief", ""),
        "brief_status": llm_brief.get("status", "unknown")
    }
    
    return report


def build_summary_stats(hospitals, doctors, trials, news_articles):
    """
    Build high level summary statistics.
    """
    
    # Count trial phases
    phase_counts = {}
    for trial in trials:
        phase = trial.get("phase", "Unknown")
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    # Count unique sponsors
    sponsors = set(t.get("sponsor", "") for t in trials)
    
    return {
        "hospitals_found": len(hospitals),
        "doctors_found": len(doctors),
        "active_trials": len(trials),
        "news_articles": len(news_articles),
        "trial_phases": phase_counts,
        "unique_sponsors": len(sponsors)
    }


def build_hospital_profile(hospitals):
    """
    Build formatted hospital profile section.
    """
    
    if not hospitals:
        return []
    
    profile = []
    for h in hospitals[:3]:
        profile.append({
            "name": h.get("name", "Unknown"),
            "npi": h.get("npi", "Unknown"),
            "address": f"{h.get('address', '')}, {h.get('city', '')}, {h.get('state', '')}",
            "phone": h.get("phone", "Unknown"),
            "specialty": h.get("specialty", "Unknown"),
            "npi_url": h.get("npi_url", "")
        })
    
    return profile


def build_doctors_section(doctors):
    """
    Build formatted doctors section.
    """
    
    if not doctors:
        return []
    
    formatted = []
    for doc in doctors[:10]:
        formatted.append({
            "name": doc.get("full_name", "Unknown"),
            "credential": doc.get("credential", ""),
            "specialty": doc.get("specialty", "Unknown"),
            "location": f"{doc.get('city', '')}, {doc.get('state', '')}",
            "phone": doc.get("phone", "Unknown"),
            "npi_url": doc.get("npi_url", "")
        })
    
    return formatted


def build_trials_section(trials):
    """
    Build formatted trials section.
    """
    
    if not trials:
        return []
    
    formatted = []
    for trial in trials[:8]:
        formatted.append({
            "nct_id": trial.get("nct_id", "Unknown"),
            "title": trial.get("title", "Unknown")[:100],
            "phase": trial.get("phase", "Unknown"),
            "status": trial.get("status", "Unknown"),
            "sponsor": trial.get("sponsor", "Unknown"),
            "endpoint": trial.get("primary_endpoint", "")[:80],
            "completion_date": trial.get("completion_date", "Unknown"),
            "url": trial.get("url", "")
        })
    
    return formatted


def build_news_section(articles):
    """
    Build formatted news section.
    """
    
    if not articles:
        return []
    
    formatted = []
    for article in articles[:5]:
        formatted.append({
            "title": article.get("title", "Unknown"),
            "preview": article.get("content", "")[:200],
            "url": article.get("url", "")
        })
    
    return formatted


def format_report_as_text(report):
    """
    Format the complete report as readable plain text.
    """
    
    lines = []
    lines.append("=" * 70)
    lines.append(report["title"].upper())
    lines.append(f"Therapeutic Focus: {report['specialty'].title()}")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("=" * 70)
    
    # Summary stats
    stats = report["summary_stats"]
    lines.append("\n📊 ACCOUNT SNAPSHOT")
    lines.append(f"  Doctors Found: {stats['doctors_found']}")
    lines.append(f"  Active Trials: {stats['active_trials']}")
    lines.append(f"  Trial Sponsors: {stats['unique_sponsors']}")
    lines.append(f"  News Articles: {stats['news_articles']}")
    
    if stats["trial_phases"]:
        lines.append("\n  Trial Phases:")
        for phase, count in stats["trial_phases"].items():
            lines.append(f"    {phase}: {count} trial(s)")
    
    # Hospital profile
    if report["hospital_profile"]:
        lines.append("\n🏥 HOSPITAL PROFILE")
        for h in report["hospital_profile"]:
            lines.append(f"\n  {h['name']}")
            lines.append(f"  Address: {h['address']}")
            lines.append(f"  Phone: {h['phone']}")
            lines.append(f"  NPI: {h['npi']}")
    
    # Key doctors
    if report["key_doctors"]:
        lines.append("\n👨‍⚕️ KEY PHYSICIANS")
        for i, doc in enumerate(report["key_doctors"][:5], 1):
            lines.append(f"\n  {i}. {doc['name']} {doc['credential']}")
            lines.append(f"     Specialty: {doc['specialty']}")
            lines.append(f"     Location: {doc['location']}")
    
    # Active trials
    if report["trials_section"]:
        lines.append("\n🔬 ACTIVE CLINICAL TRIALS")
        for i, trial in enumerate(report["trials_section"][:5], 1):
            lines.append(f"\n  {i}. {trial['title'][:70]}...")
            lines.append(f"     NCT: {trial['nct_id']} | Phase: {trial['phase']}")
            lines.append(f"     Sponsor: {trial['sponsor']}")
            lines.append(f"     URL: {trial['url']}")
    
    # Recent news
    if report["news_section"]:
        lines.append("\n📰 RECENT NEWS")
        for i, article in enumerate(report["news_section"], 1):
            lines.append(f"\n  {i}. {article['title']}")
            lines.append(f"     {article['preview'][:100]}...")
            lines.append(f"     URL: {article['url']}")
    
    # MSL Visit Brief
    lines.append("\n🤖 MSL VISIT BRIEF")
    lines.append(report["visit_brief"])
    
    lines.append("\n" + "=" * 70)
    lines.append("MSL Account Brief — Pharma Account Research Tool")
    lines.append("Data: NPI Registry · ClinicalTrials.gov · Tavily · Claude AI")
    lines.append("=" * 70)
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    # Sample data
    sample_hospitals = [{
        "name": "MAYO CLINIC",
        "npi": "1881018208",
        "address": "200 FIRST ST SW",
        "city": "ROCHESTER",
        "state": "MN",
        "phone": "507-284-2511",
        "specialty": "General Acute Care Hospital",
        "npi_url": "https://npiregistry.cms.hhs.gov/provider-view/1881018208"
    }]
    
    sample_doctors = [{
        "full_name": "Dr. TIMOTHY AADLAND",
        "credential": "MD",
        "specialty": "Radiology, Diagnostic Radiology",
        "city": "ROCHESTER",
        "state": "MN",
        "phone": "507-284-2511",
        "npi_url": ""
    }]
    
    sample_trials = [{
        "nct_id": "NCT03933826",
        "title": "CISTO: Comparison of Intravesical Therapy and Surgery",
        "phase": "PHASE3",
        "status": "RECRUITING",
        "sponsor": "University of Washington",
        "primary_endpoint": "Overall Survival",
        "completion_date": "2026-12-01",
        "url": "https://clinicaltrials.gov/study/NCT03933826"
    }]
    
    sample_news = [{
        "title": "Merck and Mayo Clinic Announce AI Collaboration",
        "content": "Merck and Mayo Clinic announce new R&D collaboration for AI-enabled drug discovery",
        "url": "https://newsnetwork.mayoclinic.org"
    }]
    
    sample_brief = {
        "brief": "Placeholder MSL brief — add API key for real analysis.",
        "status": "placeholder"
    }
    
    # Generate report
    report = generate_account_report(
        "Mayo Clinic", "oncology",
        sample_hospitals, sample_doctors,
        sample_trials, sample_news, sample_brief
    )
    
    print(format_report_as_text(report))