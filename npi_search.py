# npi_search.py
# ==============
# Searches the NPI Registry for hospitals and doctors
# NPI = National Provider Identifier
# Every US doctor and hospital has a unique NPI number
# This is 100% free government data — no API key needed

import requests
import json

# Base URL for NPI Registry API
NPI_BASE_URL = "https://npiregistry.cms.hhs.gov/api/"

def search_hospital(hospital_name, state=None):
    """
    Search for a hospital by name in the NPI Registry.
    
    Args:
        hospital_name: Name of the hospital e.g. 'Mayo Clinic'
        state: Optional US state code e.g. 'MN' for Minnesota
    
    Returns:
        List of matching hospital dictionaries
    """
    
    print(f"Searching NPI Registry for hospital: {hospital_name}")
    
    params = {
        "version": "2.1",
        "enumeration_type": "NPI-2",  # NPI-2 = organisations/hospitals
        "organization_name": hospital_name,
        "limit": 10
    }
    
    if state:
        params["state"] = state
    
    try:
        response = requests.get(NPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        print(f"Found {len(results)} matching hospitals")
        
        hospitals = []
        for result in results:
            hospital = parse_organisation(result)
            if hospital:
                hospitals.append(hospital)
        
        return hospitals
        
    except Exception as e:
        print(f"Error searching NPI Registry: {e}")
        return []


def search_doctors(hospital_name, specialty=None, state=None):
    """
    Search for doctors at a specific hospital.
    
    Args:
        hospital_name: Name of the hospital
        specialty: Medical specialty e.g. 'oncology'
        state: Optional US state code
    
    Returns:
        List of doctor dictionaries
    """
    
    print(f"Searching for doctors at: {hospital_name}")
    
    params = {
        "version": "2.1",
        "enumeration_type": "NPI-1",
        "city": hospital_name,
        "limit": 20
    }
    
    if state:
        params["state"] = state
    
    if specialty:
        params["taxonomy_description"] = specialty
    
    try:
        response = requests.get(NPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        print(f"Found {len(results)} doctors")
        
        doctors = []
        for result in results:
            doctor = parse_individual(result)
            if doctor:
                doctors.append(doctor)
        
        return doctors
        
    except Exception as e:
        print(f"Error searching doctors: {e}")
        return []


def parse_organisation(result):
    """
    Parse a raw NPI result for an organisation/hospital.
    """
    
    try:
        basic = result.get("basic", {})
        addresses = result.get("addresses", [{}])
        taxonomies = result.get("taxonomies", [{}])
        
        # Get primary address
        address = addresses[0] if addresses else {}
        
        # Get primary taxonomy (specialty)
        taxonomy = taxonomies[0] if taxonomies else {}
        
        hospital = {
            "npi": result.get("number", "Unknown"),
            "name": basic.get("organization_name", "Unknown"),
            "status": basic.get("status", "Unknown"),
            "address": address.get("address_1", "Unknown"),
            "city": address.get("city", "Unknown"),
            "state": address.get("state", "Unknown"),
            "zip": address.get("postal_code", "Unknown"),
            "phone": address.get("telephone_number", "Unknown"),
            "specialty": taxonomy.get("desc", "Unknown"),
            "npi_url": f"https://npiregistry.cms.hhs.gov/provider-view/{result.get('number', '')}"
        }
        
        return hospital
        
    except Exception as e:
        print(f"Error parsing organisation: {e}")
        return None


def parse_individual(result):
    """
    Parse a raw NPI result for an individual doctor.
    """
    
    try:
        basic = result.get("basic", {})
        addresses = result.get("addresses", [{}])
        taxonomies = result.get("taxonomies", [{}])
        
        address = addresses[0] if addresses else {}
        taxonomy = taxonomies[0] if taxonomies else {}
        
        doctor = {
            "npi": result.get("number", "Unknown"),
            "first_name": basic.get("first_name", ""),
            "last_name": basic.get("last_name", ""),
            "full_name": f"Dr. {basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
            "credential": basic.get("credential", ""),
            "specialty": taxonomy.get("desc", "Unknown"),
            "city": address.get("city", "Unknown"),
            "state": address.get("state", "Unknown"),
            "phone": address.get("telephone_number", "Unknown"),
            "npi_url": f"https://npiregistry.cms.hhs.gov/provider-view/{result.get('number', '')}"
        }
        
        return doctor
        
    except Exception as e:
        print(f"Error parsing individual: {e}")
        return None


def format_hospital_for_llm(hospital):
    """
    Format hospital data as clean text for Claude input.
    """
    
    return f"""
Hospital: {hospital['name']}
NPI: {hospital['npi']}
Address: {hospital['address']}, {hospital['city']}, {hospital['state']} {hospital['zip']}
Phone: {hospital['phone']}
Specialty: {hospital['specialty']}
Status: {hospital['status']}
"""


def format_doctors_for_llm(doctors):
    """
    Format doctor list as clean text for Claude input.
    """
    
    if not doctors:
        return "No doctors found."
    
    lines = []
    for i, doc in enumerate(doctors[:10], 1):
        lines.append(f"{i}. {doc['full_name']} {doc['credential']} — {doc['specialty']} — {doc['city']}, {doc['state']}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    # Test hospital search
    hospitals = search_hospital("Mayo Clinic", state="MN")
    
    if hospitals:
        print(f"\nFirst hospital found:")
        print(f"Name: {hospitals[0]['name']}")
        print(f"Location: {hospitals[0]['city']}, {hospitals[0]['state']}")
        print(f"NPI: {hospitals[0]['npi']}")
    else:
        print("No hospitals found")
    
    # Test doctor search
    print("\n" + "="*50)
    doctors = search_doctors("Rochester", state="MN")
    
    if doctors:
        print(f"\nFirst doctor found:")
        print(f"Name: {doctors[0]['full_name']}")
        print(f"Specialty: {doctors[0]['specialty']}")
    else:
        print("No doctors found")