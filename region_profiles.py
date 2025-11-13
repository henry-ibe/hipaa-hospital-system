"""
Region-specific hospital profiles for realistic metrics
"""
import random

REGION_PROFILES = {
    'ny': {
        'name': 'Mount Sinai Hospital',
        'type': 'Urban High-Volume',
        'patient_multiplier': 1.5,
        'wait_time_base': 30,
        'occupancy_base': 85,
        'department_focus': {
            'Emergency': 1.8,
            'Cardiology': 1.2,
            'Surgery': 1.1,
            'Pediatrics': 1.0,
            'Radiology': 1.3
        },
        'satisfaction_range': (4.2, 4.6),
        'cost_multiplier': 1.3
    },
    'ca': {
        'name': 'UCLA Medical Center',
        'type': 'Research Hospital',
        'patient_multiplier': 1.2,
        'wait_time_base': 20,
        'occupancy_base': 75,
        'department_focus': {
            'Surgery': 1.6,
            'Radiology': 1.4,
            'Cardiology': 1.1,
            'Emergency': 1.0,
            'Pediatrics': 1.2
        },
        'satisfaction_range': (4.5, 4.8),
        'cost_multiplier': 1.2
    },
    'il': {
        'name': 'Northwestern Memorial',
        'type': 'Teaching Hospital',
        'patient_multiplier': 1.0,
        'wait_time_base': 15,
        'occupancy_base': 70,
        'department_focus': {
            'Cardiology': 1.5,
            'Emergency': 0.9,
            'Surgery': 1.1,
            'Pediatrics': 1.0,
            'Radiology': 1.0
        },
        'satisfaction_range': (4.3, 4.7),
        'cost_multiplier': 0.9
    }
}

def get_region_metrics(region, department):
    """Generate realistic metrics based on region profile"""
    profile = REGION_PROFILES.get(region, REGION_PROFILES['il'])
    
    base_patients = random.randint(50, 80)
    dept_focus = profile['department_focus'].get(department, 1.0)
    patient_count = int(base_patients * profile['patient_multiplier'] * dept_focus)
    
    wait_time_variance = 30 if department == 'Emergency' else 20
    wait_time = profile['wait_time_base'] + random.randint(-10, wait_time_variance)
    
    occupancy_variance = random.randint(-10, 15)
    occupancy = min(100, profile['occupancy_base'] + occupancy_variance)
    
    staff_util_base = 70 if patient_count < 80 else 85
    staff_util = staff_util_base + random.randint(-5, 15)
    
    return {
        'patients': patient_count,
        'wait_time': max(5, wait_time),
        'occupancy': max(30, occupancy),
        'staff_utilization': min(100, max(50, staff_util))
    }

def get_region_satisfaction(region):
    """Get region-specific satisfaction score"""
    profile = REGION_PROFILES.get(region, REGION_PROFILES['il'])
    min_sat, max_sat = profile['satisfaction_range']
    return round(random.uniform(min_sat, max_sat), 1)

def get_region_cost(region):
    """Get region-specific cost per transaction"""
    profile = REGION_PROFILES.get(region, REGION_PROFILES['il'])
    base_cost = 0.05
    return round(base_cost * profile['cost_multiplier'], 4)
