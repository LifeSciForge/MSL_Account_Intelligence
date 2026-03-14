# trials_at_site.py
# ==================
# Finds clinical trials running at a specific hospital
# Reuses ClinicalTrials.gov API from Project 03
# But this time searches by facility/location
# 100% free government data — no API key needed

import requests

# ClinicalTrials.gov API v2
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def get_trials_at_hospital(hospital_name, state=None, max_results=10):
    """
    Find clinical trials running at a specific hospital.
    
    Args:
        hospital_name: Name of the hospital e.g. 'Mayo Clinic'
        state: Optional US state e.g. 'Minnesota'
        max_results: Maximum number of trials to return
    
    Returns:
        List of trial dictionaries
    """
    
    print(f"Searching trials at: {hospital_name}")
    
    # Search by facility name
    query = hospital_name
    if state:
        query += f" {state}"
    
    params = {
        "query.locn": query,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING",
        "pageSize": max_results,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        studies = data.get("studies", [])
        print(f"Found {len(studies)} trials at {hospital_name}")
        
        trials = []
        for study in studies:
            trial = parse_trial(study)
            if trial:
                trials.append(trial)
        
        return trials
        
    except Exception as e:
        print(f"Error fetching trials: {e}")
        return []


def get_trials_by_specialty(hospital_name, specialty, max_results=10):
    """
    Find trials at a hospital filtered by medical specialty.
    
    Args:
        hospital_name: Name of the hospital
        specialty: Medical specialty e.g. 'oncology'
        max_results: Maximum results to return
    
    Returns:
        List of trial dictionaries
    """
    
    print(f"Searching {specialty} trials at: {hospital_name}")
    
    params = {
        "query.locn": hospital_name,
        "query.cond": specialty,
        "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING",
        "pageSize": max_results,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        studies = data.get("studies", [])
        print(f"Found {len(studies)} {specialty} trials")
        
        trials = []
        for study in studies:
            trial = parse_trial(study)
            if trial:
                trials.append(trial)
        
        return trials
        
    except Exception as e:
        print(f"Error fetching trials by specialty: {e}")
        return []


def parse_trial(study):
    """
    Parse a raw ClinicalTrials.gov study record.
    """
    
    try:
        protocol = study.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        desc_module = protocol.get("descriptionModule", {})
        design_module = protocol.get("designModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        outcomes_module = protocol.get("outcomesModule", {})
        
        # Get phase
        phases = design_module.get("phases", ["Unknown"])
        phase = phases[0] if phases else "Unknown"
        
        # Get primary endpoint
        primary_outcomes = outcomes_module.get("primaryOutcomes", [])
        endpoint = primary_outcomes[0].get("measure", "Not specified") if primary_outcomes else "Not specified"
        
        # Get sponsor
        lead_sponsor = sponsor_module.get("leadSponsor", {})
        sponsor = lead_sponsor.get("name", "Unknown")
        
        trial = {
            "nct_id": id_module.get("nctId", "Unknown"),
            "title": id_module.get("briefTitle", "Unknown"),
            "status": status_module.get("overallStatus", "Unknown"),
            "phase": phase,
            "sponsor": sponsor,
            "primary_endpoint": endpoint[:100],
            "summary": desc_module.get("briefSummary", "")[:200],
            "start_date": status_module.get("startDateStruct", {}).get("date", "Unknown"),
            "completion_date": status_module.get("primaryCompletionDateStruct", {}).get("date", "Unknown"),
            "url": f"https://clinicaltrials.gov/study/{id_module.get('nctId', '')}"
        }
        
        return trial
        
    except Exception as e:
        print(f"Error parsing trial: {e}")
        return None


def format_trials_for_llm(trials, hospital_name):
    """
    Format trial data as clean text for Claude input.
    """
    
    if not trials:
        return f"No active clinical trials found at {hospital_name}."
    
    lines = [f"Active clinical trials at {hospital_name}:"]
    
    for i, trial in enumerate(trials[:8], 1):
        lines.append(f"\n{i}. {trial['title'][:80]}")
        lines.append(f"   NCT: {trial['nct_id']} | Phase: {trial['phase']} | Status: {trial['status']}")
        lines.append(f"   Sponsor: {trial['sponsor']}")
        lines.append(f"   Endpoint: {trial['primary_endpoint'][:60]}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    # Test with Mayo Clinic oncology trials
    trials = get_trials_by_specialty("Mayo Clinic", "oncology")
    
    if trials:
        print(f"\nFirst trial found:")
        print(f"Title: {trials[0]['title'][:80]}")
        print(f"NCT: {trials[0]['nct_id']}")
        print(f"Phase: {trials[0]['phase']}")
        print(f"Sponsor: {trials[0]['sponsor']}")
    else:
        print("No trials found")