
def cyber_data_points():
    fields = [
        'Name Insured',
        'Other Named Insured',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Additional Coverage(s)',
        'Forms and Endorsements',
        'Endorsements',
        'Location',
        'Exclusions',
        'Limits of Liability',
        'Privacy Breach Response Services',
        'Business Interruption',
        'Media',
        'Social Engineering',
        'Terrorism',
        'Deductible or Retention',
        'Retroactive Date[s]',
        'Prior and Pending Date',
        'Continuity Date[s]',
        'Underlying Insurance'
    ]
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict  # <-- no comma

def general_liability_data_points():
    fields = [
        'Name Insured',
        'Other Named Insured',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Location',
        'General Liability',
        'Employee Benefit Liability Coverage',
        'Hired And Non owned Coverage',
        'Directors and Officers',
        'Cyber',
        'Professional Liability',
        'EPLI on Policy',
        'Errors and Omissions on Policy',
        'Terrorism',
        'Work Exclusion',
        'Additional Interest',
        'Additional Coverage',
        'Forms And Endorsements',
        'Endorsements'
    ]
    # Convert list to dict with default regex (catch-all)
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict  # <-- no comma

def comercial_auto_data_points():
    fields = [
        'Name Insured',
        'Other Named Insured',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Location',
        'Symbol',
        'Limits',
        'vehiclesinfo',
        'cyber',
        'scheduleddrivers',
        'hiredornon-ownedautolimits',
        'driveothercarcoverage',
        'terrorism',
        'exclusions',
        'Additional Interest',
        'Additional Coverage(s)',
        'Forms and Endorsements',
        'Endorsements',
    ]
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict  # <-- no comma

# utils/data_points.py
def business_owner_data_points():
    fields = [
        'Name Insured',
        'Other Named Insured (DBA)',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Location',
        'General Aggregate',
        'Products or Completed Operations Aggregate',
        'Personal And Advt Injury',
        'Medical expenses',
        'Damage to rented premises',
        'Each Occurrence',
        'Deductible',
        'Hired Or Non Owned Auto',
        'Advance Premium',
        'Additional Interest',
        "Schedule of Hazards Rating Info",
        'Employee Benefits Liability',
        'Directors and Officers',
        'Cyber',
        'Professional Liability',
        'EPLI on Policy',
        'Errors and Omissions on Policy',
        'Terrorism',
        'Work Exclusion',
        'Liability locations match property locations if applicable',
        'Building Value',
        'Business Personal Property Limit',
        'Business Income Limit',
        'Improvements and Betterments',
        'Wind And Hail',
        'Property Deductible',
        'Co Insurance',
        'Valuation',
        'Is Equipment Breakdown Listed',
        'Building Ordinance Or Law Listed Cov A',
        'Building Ordinance Demolition Cost Cov B',
        'Building Ordinance Inc Cost Of Construction Cov C',
        'Property Terrorism',
        'Inland Marine Details',
        'Equipment Schedule',
        'Deductibles',
        'Loss Payee',
        'Rental equipment from others',
        'Rental equipment to others',
        'Installation floater',
        'Inland Marine Terrorism',
        'Umbrella Limits',
        'Underlying Policies',
        'Policy Exclusions',
        'Additional Coverage(s)',
        'Forms And Endorsements',
        'Endorsements'
    ]

    # Convert list to dict with default regex (catch-all)
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict

def forms_hunting_points():
    return [
        "Forms and Endorsements complete list",
        "All form numbers, titles, and dates",
        "Endorsements list",
        "All insurance forms, notices, state filings",
        "Any text matching pattern like AA-123 (MM-YY)"
    ]

def property_data_points():
    fields = [
        'Name Insured',
        'Other Named Insured',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Location',
        'Building Value',
        'Improvements And Betterments',
        'Business Personal Property Limit',
        'Business Income Limit',
        'Wind and Hail',
        'Deductible',
        'Co Insurance',
        'Valuation',
        'Is Equipment Breakdown Listed',
        'Building Ordinance Or Law Listed Cov A',
        'Building Ordinance Demolition Cost Cov B',
        'Building Ordinance Inc Cost Of Construction Cov C',
        'Terrorism',
        'Exclusions',
        'Additional Interest',
        'Additional Coverage',
        'Forms And Endorsements',
        'Endorsements'
    ]
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict
    
def workers_compensation_points():
    fields = [
        'Name Insured',
        'Other Named Insured',
        'Additional Insured',
        'Mailing Address',
        'Policy Number',
        'Policy Period',
        'Issuing Company',
        'Premium',
        'Paid In Full Discount',
        'Miscellaneous Premium',
        'Location',
        'FEIN',
        'Coverage States',
        'Other States',
        'Employers Limits',
        'Rating Info',
        'Experience Mod',
        'Changes in Credits',
        'Members Excluded',
        'Terrorism',
        'Exclusions',
        'Additional Interest',
        'Additional Coverage',
        'Forms And Endorsements',
        'Endorsements'
    ]
    data_points_dict = {field: r"([\s\S]*?)" for field in fields}
    return data_points_dict
