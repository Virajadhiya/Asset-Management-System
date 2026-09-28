from datetime import datetime

COMPONENT_WEIGHTS = {
    "DECK": 0.25,
    "SUPERSTRUCTURE": 0.25,
    "SUBSTRUCTURE": 0.20,
    "FOUNDATION": 0.15,
    "BEARINGS": 0.10,
    "EXPANSION_JOINTS": 0.05,
}

def calculate_health_index(components: list, design_life: int = 100, year_built: int = None) -> dict:
    if not components:
        return {"score": 0.0, "category": "CRITICAL", "version": "prototype-v1"}
        
    structural_score = 0.0
    weight_sum = 0.0
    safety_scores = []
    
    for comp in components:
        rating = comp.condition_rating
        # Normalize 1-5 to 0-100: (rating - 1) / 4 * 100
        # Rating 1 = worst (0%), Rating 5 = best (100%)
        normalized = max(0, min(100, (rating - 1) / 4 * 100))
        
        c_type = comp.component_type
        if c_type in COMPONENT_WEIGHTS:
            w = COMPONENT_WEIGHTS[c_type]
            structural_score += normalized * w
            weight_sum += w
        elif c_type in ["SAFETY_BARRIERS", "DRAINAGE", "APPROACHES"]:
            safety_scores.append(normalized)

    if weight_sum > 0:
        structural = structural_score / weight_sum
    else:
        structural = 70.0 # Default if no main structural components rated

    functional = 80.0
    safety = sum(safety_scores) / len(safety_scores) if safety_scores else 70.0
    
    age = datetime.utcnow().year - year_built if year_built else 0
    age_factor = max(0, 100 - (age / design_life * 100)) if design_life else 50.0
    
    bhi = 0.40 * structural + 0.30 * functional + 0.20 * safety + 0.10 * age_factor
    
    if bhi >= 85:
        category = "EXCELLENT"
    elif bhi >= 70:
        category = "GOOD"
    elif bhi >= 55:
        category = "FAIR"
    elif bhi >= 40:
        category = "POOR"
    else:
        category = "CRITICAL"
        
    return {
        "score": round(bhi, 2),
        "category": category,
        "version": "prototype-v1"
    }
