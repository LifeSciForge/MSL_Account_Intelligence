# llm_brief.py
# =============
# Generates an MSL pre-call visit brief using Claude AI
# Takes hospital data, trials, and news as input
# Returns a structured visit brief ready to use
# Requires ANTHROPIC_API_KEY in .env file

import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def generate_visit_brief(hospital_name, specialty, hospital_data,
                          doctors_data, trials_data, news_data):
    """
    Generate a structured MSL pre-call visit brief.
    
    Args:
        hospital_name: Name of the hospital
        specialty: Therapeutic area e.g. 'oncology'
        hospital_data: Formatted hospital info from npi_search.py
        doctors_data: Formatted doctor list from npi_search.py
        trials_data: Formatted trials from trials_at_site.py
        news_data: Formatted news from news_search.py
    
    Returns:
        Dictionary with structured visit brief
    """
    
    # Check if API key is configured
    if not API_KEY:
        print("No API key configured — returning placeholder brief")
        return get_placeholder_brief(hospital_name, specialty)
    
    prompt = build_prompt(
        hospital_name, specialty, hospital_data,
        doctors_data, trials_data, news_data
    )
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=API_KEY)
        print(f"Generating AI visit brief for {hospital_name}...")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis_text = response.content[0].text
        
        return {
            "hospital_name": hospital_name,
            "specialty": specialty,
            "brief": analysis_text,
            "status": "success"
        }
        
    except ImportError:
        print("Anthropic library not installed. Run: pip install anthropic")
        return get_placeholder_brief(hospital_name, specialty)
    except Exception as e:
        print(f"Error generating brief: {e}")
        return get_placeholder_brief(hospital_name, specialty)


def build_prompt(hospital_name, specialty, hospital_data,
                 doctors_data, trials_data, news_data):
    """
    Build the MSL visit brief prompt for Claude.
    """
    
    return f"""You are a senior Medical Science Liaison (MSL) with 15 years 
of experience preparing pre-call visit briefs for pharma field teams.

Prepare a concise, actionable pre-call visit brief for the following account:

HOSPITAL: {hospital_name}
THERAPEUTIC FOCUS: {specialty}

HOSPITAL PROFILE:
{hospital_data}

KEY PHYSICIANS:
{doctors_data}

ACTIVE CLINICAL TRIALS AT THIS SITE:
{trials_data}

RECENT NEWS AND DEVELOPMENTS:
{news_data}

Please generate a structured MSL Pre-Call Visit Brief with these sections:

1. ACCOUNT SNAPSHOT
   - Hospital type and size
   - Key therapeutic strengths
   - Strategic importance rating (High/Medium/Low) with rationale

2. KEY OPINION LEADERS
   - Top 3 physicians to engage
   - Their specialty and research focus
   - Recommended engagement approach for each

3. CLINICAL TRIAL ACTIVITY
   - Active trials relevant to our therapy area
   - Trial phases and sponsors
   - Opportunities for investigator-initiated trials

4. RECENT DEVELOPMENTS
   - Latest news and strategic moves
   - New partnerships or collaborations
   - Any competitive activity

5. MSL VISIT OBJECTIVES
   - Top 3 goals for this visit
   - Key scientific messages to communicate
   - Materials and resources to bring

6. CONVERSATION STARTERS
   - 3 specific discussion points based on recent news
   - Questions to ask to understand unmet needs
   - Follow-up actions to propose

Keep each section concise — 3 to 5 bullet points.
Focus on actionable insights for an MSL preparing for a hospital visit.
"""


def get_placeholder_brief(hospital_name, specialty):
    """
    Returns placeholder brief when no API key is configured.
    """
    
    return {
        "hospital_name": hospital_name,
        "specialty": specialty,
        "brief": f"""
## MSL Pre-Call Visit Brief: {hospital_name}
## Therapeutic Focus: {specialty}

**Note: Placeholder brief. Add ANTHROPIC_API_KEY to .env for real AI analysis.**

1. ACCOUNT SNAPSHOT
   - Major academic medical centre with strong research focus
   - Leading {specialty} programme with multiple active trials
   - Strategic importance: HIGH — key opinion leader institution
   - Strong pharma industry relationships across therapy areas

2. KEY OPINION LEADERS
   - Multiple fellowship-trained {specialty} specialists on staff
   - Active investigators in industry-sponsored trials
   - Recommended: Schedule scientific exchange meeting with PI team

3. CLINICAL TRIAL ACTIVITY
   - Multiple Phase 2 and Phase 3 trials active at this site
   - Both industry-sponsored and investigator-initiated trials
   - Opportunity to discuss IIT support and data generation

4. RECENT DEVELOPMENTS
   - Active research collaborations with pharma partners
   - Recent publications in high-impact journals
   - Expanding clinical trial portfolio in {specialty}

5. MSL VISIT OBJECTIVES
   - Establish scientific exchange with key investigators
   - Understand current treatment protocols and gaps
   - Discuss trial participation and IIT opportunities

6. CONVERSATION STARTERS
   - Recent trial results in {specialty} and clinical implications
   - Unmet needs in current treatment algorithms
   - Interest in upcoming data presentations at conferences

*Add your Anthropic API key to .env to replace with real AI analysis.*
""",
        "status": "placeholder"
    }


# Quick test
if __name__ == "__main__":
    result = generate_visit_brief(
        hospital_name="Mayo Clinic",
        specialty="oncology",
        hospital_data="Major academic medical centre, Rochester MN, NPI: 1881018208",
        doctors_data="20 physicians found including oncologists and radiologists",
        trials_data="10 active oncology trials including Phase 2 and Phase 3 studies",
        news_data="Merck and Mayo Clinic announce AI-enabled drug discovery collaboration"
    )
    
    print(f"Brief status: {result['status']}")
    print(f"\nBrief preview:")
    print(result['brief'][:600])