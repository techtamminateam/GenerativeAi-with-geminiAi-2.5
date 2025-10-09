def prompt_template_cyber(large_text=None):

    return f"""
        You are an expert insurance data extractor.
        The following text is extracted from a Business Owner’s Policy (BOP) insurance PDF
        using a mix of digital text, OCR text, Rows and tables.

        ### Extraction Rules
        - **Search through the ENTIRE document for every required field**.
        - Dates must always be in MM/DD/YYYY format.
        - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
        Continue scanning to the **very end of the document**.
        - Merge multi-line form numbers/titles into a **single entry** if they are split
        across lines or pages.
        - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
        - Deduplicate only when text is truly identical.
        - If a field is missing, set it to `null`; if an array is empty, return `[]`.
        - Output must be **only** a valid JSON object. No explanations or commentary.

        ### Datapoints to Extract ###
            1. Name Insured: 
            2. Other Named Insured: (Can also be called as DBA)
            3. Additional Insured: (retunr as array of objects with name and address)
            4. Mailing Address:
            5. Policy Number: (return only policy number not any other text around it)
            6. Policy Period: (MM/DD/YYYY to MM/DD/YYYY)
            7. Issuing Company:
            8. Premium: (include details)
            9. Paid In Full Discount
            10. Miscellaneous Premium (like taxes, fees, surcharges etc):
            11. Additional Coverage(s): (get all the possible information and sublimits of liability)
            12. Forms and Endorsements: 
                Forms And Endorsements
                    - **Collect every form across the entire document**, including Property,
                    General Liability, Auto, Umbrella, Notices, and any state filings.
                    - Do NOT stop at the first “Forms and Endorsements” heading.
                    - Merge split lines into one entry.
                    - Normalize each entry strictly in this format:
                    "FormNumber (MM-YY) | MM/YY   Form Title"
                    - Return **all forms** as a single JSON array.
            13. Endorsements: (don't include limits or Retention, and show when any of this is mentioned modified/changed/deleted/added details)
            14. Location (include full address)
            15. Exclusions: (return only Policy Exclusions with value only not endorsements exclusions)
            16. Limits of Liability: (must list all liability limits with amounts and **Extract only Policy limits not sublimited coverages**)

            17. Privacy Breach Response Services: (Premium)
            18. Business Interruption: (Premium)
            19. Media: (Premium)
            20. Social Engineering: (Premium)
            21. Terrorism: (return only if premium exist other keep it has null)
            22. Deductible or Retention: 
            23. Retroactive Date[s]: 
            24. Prior and Pending Date: 
            25. Continuity Date[s]:
            26. Underlying Insurance: (list of insurance with details)

            {f'Text: {large_text}' if large_text else ''}

            Return only a pure JSON object, assigning null to any key without a corresponding value.
            """

def prompt_template_general(large_text=None):
    return f"""
            You are provided with structured text extracted from a PDF insurance document. The structure uses special tags for clarity:
            - [LINE] denotes a line of text extracted directly from the PDF.
            - [TABLE X START] and [TABLE X END] denote the start and end of table X.
            - [ROW] and [COL] are used to indicate table rows and columns.
            - [OCR_LINE] denotes text obtained through OCR where normal extraction failed.
            Your task is to extract insurance-related data points by **matching exact or close label names from the PDF** (see list below). Use the context near each label to extract the correct value.
            Match the following fields **based on exact label names** or their variations as they may appear in the document (e.g., "Insured Name" instead of "Name Insured", or "Policy #" instead of "Policy Number").
            The data may be spread across multiple sections, so search across all sections and return all of them.
            **Rules for nulls:
                - When checking for null values or extracting datapoints, account for similar words or variations in formatting, such as 'PREM' matching 'Prem.No.', 'BLDG' matching 'Bldg.No.', 'Building Value' matching 'Building Limit' or 'Limit of Insurance', etc. Treat these variations as equivalent for matching purposes but preserve the exact text as it appears in the document.
                - For any field, if no exact or similar match is found after checking variations, set to null or empty array as appropriate.
            Here are the data points to extract:
            1. Name Insured   
            2. Other Named Insured (DBA)   
            3. Additional Insured   
            4. Mailing Address   
            5. Policy Number 
            6. Policy Period   
            7. Issuing Company   
            8. Premium  + include details
            9. Paid In Full Discount   
            10. Miscellaneous Premium   
            11. Location 
                -Return all row and columns of location like including Prem, Building number, address etc which matches exact address.
                -Prem and Building must present eg- PREM 1 - BLDG 1 - 825 Wadsworth Blvd - Denver - CO - 80215
                -Also mention variable name according to their values
                -return them in one line and put - in between them
            12. General Liability (include every detail)
                - Medical expenses + include details
                - Damage to rented premises
                - Each Occurrence
                - Personal And Advt Injury
                - Products or Completed Operations Aggregate
                - General Aggregate, Deductible
                - Hired Or Non Owned Auto
                - Schedule of Hazards Rating Info 
                    - Example:[St/Terr": "CO 501",
                              "Code": "61212",
                              "Classification": "Buildings or Premises-bank or office-mercantile or manufacturing (lessor's risk only)-Other than Not For Profit",
                              "Prem Basis": "a) 6,000",
                              "Prem Ops": "125.78",
                              "Pr/Co": "Incl",
                              "All Other": 755]
                    - Return all rows and columns of schedule of hazards rating info

            13. Employee Benefits Liability (if any section is found, capture details — else null)   
            14. Directors and Officers (check for D&O coverage section — else null)   
            15. Cyber (Cyber Security Liability Section, if mentioned explicitly)   
            16. Professional Liability (E&O or malpractice-related coverages if present)   
            17. EPLI on Policy (Employment Practices Liability Insurance)   
            18. Errors and Omissions on Policy   
            19. Terrorism (coverage status and premium if listed)   
            20. Work Exclusion   
            21. Liability locations match property locations if applicable (Yes/No/true/false)   
            22. Property (search for "DESCRIPTION OF PREMISES:" and find all details below mentioned)
                - Building Value:   
                    Example:["PREM 1 - BLDG 1 - Building - 901000 - Special Form Including Theft",]
                    - Return all rows and columns of schedule of hazards rating info
                - Business Income Limit   
                - Improvements and Betterments   
                - Wind and Hail   
                - Property Deductible   
                - Co-Insurance 
                    - Always return with PREM and BLDG.   
                    - Format: "PREM x - BLDG y - <coinsurance percentage>".   
                    - Return all entries in array. 
                - Valuation   
                    - Extract valuation basis per building (RC, ACV, etc.).   
                    - Format: "PREM x - BLDG y - <valuation text>".   
                    - Return all in array.
                - Is Equipment Breakdown Listed?   
                - Building Ordinance or Law Coverage A   
                - Building Ordinance Demolition Cost Coverage B   
                - Building Ordinance Increased Cost of Construction Coverage C   
                - Additional Interests (e.g., Mortgage Holders)   

            23. Property Terrorism   
            24. Inland Marine Details   
            25. Equipment Schedule   
            26. Deductibles (other than property deductible)   
            27. Loss Payee   
            28. Rental Equipment From Others   
            29. Rental Equipment To Others   
            30. Installation Floater   
            31. Inland Marine Terrorism   
            32. Umbrella Limits   
            33. Underlying Policies   
            34. Policy Exclusions   
            35. Additional Coverages
                - The "Additional Coverages" section may span multiple sections. Do not stop at a section break — continue searching until no more forms are found.   
                - Ignore section headers, footers, or unrelated section titles.   
                - Extract every detail. Do not summarize or skip. Output must contain the **full list** exactly as in the document.    

            36. Forms and Endorsements
                - The "Forms and Endorsements" section may span multiple sections. Do not stop at a section break — continue searching until no more forms are found.   
                - Ignore section headers, footers, or unrelated section titles.   
                - Extract every detail in following format in same line:
                  - Form number | Date     Title (put | between Form number and date, put spaces between date and title)
                - Ensure you capture **all forms** from the entire document sections, not just the first section.   
                - Do not summarize or skip. Output must contain the **full list** exactly as in the document.    

            37. Endorsements   

            ### Instructions:
            - Search for each field using **its exact label** or a variation commonly seen in insurance PDFs.
            - Use information immediately **next to**, **below**, or in the **same row** or **column** as the label.
            - Return the results in a structured **JSON** format.
            - If a field is not found, return `"Not listed"`.

            Only return the structured JSON.

            Retrieved Sections:
            {f"Extracted Text: {large_text}" if large_text else ""}

            ## Final Output Rules:
            - Output must be **only** the JSON object. No natural language.   
            - Numbers must be plain integers or floats (no currency symbols).   
            - Dates must be MM/DD/YYYY.   
            - Arrays must be `[]` if no entries found.   
            - All missing data explicitly set to `null`.   
            """

def prompt_template_commercial_auto(large_text=None):
    return f"""You are an expert insurance data extractor.
        The following text is extracted from a Property insurance PDF using a mix of
        digital text, OCR text, and tables.  
        Some forms or endorsements may be spread across multiple pages or split into separate
        lines. Your task is to search the **ENTIRE** document and extract every required
        datapoint listed below.  

        ### Extraction Rules ###
            - Extract datapoints exactly as they appear (preserve numbers, punctuation, symbols and wording).  
            - All symbols used in the document (e.g., $, %, commas) must be preserved as-is in the JSON.  
            - Dates must always be in MM/DD/YYYY format.  
            - The Policy Period must be split into start and end.  
            - For Policy Period End, check alternative labels: "PROPOSED EXP DATE", "Expiration Date", "End date".  
            - End date should not be null if present anywhere in the document.  
            - Premiums must be extracted in the format:
                "Coverage Name": "$1,147.49"
            - Symbols must be extracted in the format:
                Example: "Category": 1, 2, 7, 8, 9
            - Vehicles Info must be extracted in the format:
                "Unit : 1. - VIN : 1FTNX21F93EB04329 - Year : 2003 - Make : FORD - Model : F250 - PREMIUM : $1,612.57"

            - Scheduled Drivers must be extracted in the format:
                {{NameLast, FirstName, DOB or Age, State, License Number, Premium}}
                - Include all available fields exactly as in the document
                - Return as an array of objects
                - Multiple values (Limits, Vehicles, Endorsements, Additional Interests, etc.) must always be returned in arrays.  
                - If a datapoint is missing, explicitly set it to null (or [] for arrays).  
                - Do not assume or invent values — only return if present.  
                - Output must be a pure JSON object with no extra commentary.
            ### Datapoints to Extract ###
            1. Name Insured  
            2. Other Named Insured (DBA)  
            3. Additional Insured → [{{Name, Address}}]  
            4. Mailing Address  
            5. Policy Number  
            6. Policy Period → {{Start, End}}  
            7. Issuing Company  
            8. Premium → strictly formatted with preserved symbols  
            9. Paid In Full Discount  
            10. Miscellaneous Premium  
            11. Location + include all details  
            12. Symbol  
                - Example:"symbol": [
                        "Combined Liability": "7, 8, 9, 19",
                        "Uninsured Motorist": "6",
                        "Underinsured Motorist": "6",
                        "Personal Injury Protection": "7",
                        "Comprehensive": "7",
                        "Collision": "7",
                        "Road Trouble Service": "7",
                        "Additional Expense": "7"]
            13. Limits → all limits with labels + values  
            14. Vehicles Info 
                - Must capture all vehicles listed with full details
                - Return each vehicle in the specified format
                - Example: "Unit : 1. - VIN : 1FTNX21F93EB04329 - Year : 2003 - Make : FORD - Model : F250 - PREMIUM : $1,612.57"  
            15. Cyber → if present  
            16. Scheduled Drivers → [{{NameLast, FirstName, DOB or Age, State, License Number, Premium}}]  
            17. Hired Or Non-Owned Auto Limits → {{Hired Autos Liability, Non-Owned Autos Liability}}  
            18. Drive Other Car Coverage  
            19. Terrorism → {{Coverage, Premium, Exclusions, Inclusion_Status}}  
            20. Exclusions → all exclusions explicitly listed  
            21. Additional Interest → [{{Name, Address, Role if specified}}]  
            22. Additional Coverage(s) + include all coverages and values  
            23. Forms And Endorsements  
                    - **Collect every form across the entire document**, including but not limited to
                       Property, General Liability, Auto, Umbrella, Notices, and State filings.  
                    - Do NOT stop at the first "Forms and Endorsements" heading—scan to the end of the document.  
                    - Merge lines if a form number or title is split.  
                    - Normalize strictly into this format:  
                        "FormNumber (MM-YY) | MM/YY   Form Title"  
                    - Return **all forms** as a single JSON array, even if they belong to different coverage parts.  
            24. Endorsements → [{{Title, Effective Date, Details}}]  
            ### Final Output Rules ###
            - Must return a single valid JSON object only.  
            - Arrays must be empty [] if not found.  
            - Missing datapoints must be null.  
            ### Special Priority ###
            Ensure **all datapoints** are extracted if present.  
            Pay particular attention to **Vehicles Info** and **Scheduled Drivers**, as these often appear in structured tables.  
            Do not skip or truncate them.  

            ### DOCUMENT CONTENT ###
            {f'Text: {large_text}' if large_text else ''}
            """

def prompt_template_general_liability(large_text=None) :
    return f"""You are an expert insurance data extractor.
        ### Task
        Extract **all** possible datapoints from the provided Business Owner's Policy (BOP) text.
        Return **one valid JSON object** strictly matching the schema below.
        Do NOT include explanations, comments, or text outside JSON.

        ### Key Focus
        Be especially thorough in capturing:
        - **Every Form and Endorsement** (include all numbers, dates, and titles exactly as shown).
        - **All Premium coverages** and the **Total Premium** (return every coverage line you can find).
        - **All Hazards / Class code entries** (Class code, Classification, Exposure, Premium Basis, Rate), capture all of rows and columns under this.
        Scan every table, schedule, endorsement, and free-text section.  
        Merge information across pages; deduplicate only if values are identical.

        ### Rules
        - Keys MUST match the schema exactly, including capitalization and spaces.
        - Include all nested objects and arrays, even if null or empty.
        - Preserve all formatting, symbols, numbers, dates, and special characters exactly as they appear.
        - For fields not found in any section, return null for single values or [] for arrays.

        ### Datapoints to Extract (strict order)
        {{
        "Name Insured": string | null,
        "Other Named Insured": [string] | null,
        "Additional Insured": [string] | null,
        "Mailing Address": string | null,
        "Policy Number": string | null,
        "Policy Period": string | null,
        "Issuing Company": string | null,
        "Premium": {{
            "<Coverage Name>": string | number,
            "Total premium": number
        }} | null,
        "Paid In Full Discount": string | null,
        "Miscellaneous Premium": string | null,
        "Location": [string] | [],
        "Each Occurrence limit": string | null,
        "General Aggregate Limit": string | null,
        "Products or Completed Operations Aggregate": string | null,
        "Personal And Advertising Injury Limit": string | null,
        "Damage to Rented Premises Limit": string | null,
        "Medical Payments Limit": string | null,
        "Deductible": [string] | null,
        "Hazards Rating info": [{{
            "Class code": string,
            "Classification": string,
            "Exposure": string,
            "Premium Basis": string,
            "Rate": string
        }}] | [],
        "Employee Benefit Liability Coverage": string | null,
        "Hired And Non owned Coverage": string | null,
        "Directors and Officers": string | null,
        "Cyber": string | null,
        "Professional Liability": string | null,
        "EPLI on Policy": string | null,
        "Errors and Omissions on Policy": string | null,
        "Terrorism": string | null,
        "Work Exclusion": string | null,
        "Additional Interest": [string] | [],
        "Additional Coverage": [{{
            "Coverage": string,
            "Limit": string | number,
            "Premium": string | number
        }}] | [],
        "Forms And Endorsements": [string] | []
            - Normalize strictly into this format:  
            "FormNumber (MM-YY) | MM/YY   Form Title",
        "Endorsements": [string] | []
        }}

        ### Retrieved Sections
        {f'Text: {large_text}' if large_text else ''}

        ### Final Output
        Return **only** the above JSON object with all keys present in the exact order.
        If a datapoint is not found, set it to null or [] accordingly.
        """

def prompt_template_property(large_text=None):
    return f"""
    You are an expert insurance data extractor.
    The following text is extracted from a Property insurance PDF using a mix of
    digital text, OCR text, and tables.  
    Some forms or endorsements may be spread across multiple pages or split into separate
    lines. Your task is to search the **ENTIRE** document and extract every required
    datapoint listed below.  

    ### Rules for Extraction
    - **Never stop** at the first occurrence of any section.  
      Continue scanning until the **very end of the document** to ensure nothing is missed.
    - Merge multi-line form numbers/titles into a **single entry** if they are split.
    - Deduplicate only when the text is **identical**.
    - Preserve all numbers, dates, symbols, and formatting exactly as shown.
    - If no value exists for a field, set it to `null` (or `[]` for arrays).
  
 
    ### Datapoints to Extract ###
    1. Name Insured  
    2. Other Named Insured (DBA)  
    3. Additional Insured → [{{"Name": "string", "Address": "string"}}]  
    4. Mailing Address  
    5. Policy Number  
    6. Policy Period → {{"Start": "MM/DD/YYYY", "End": "MM/DD/YYYY"}}  
    7. Issuing Company  
    8. Premium → include all coverage-level premiums and the total premium  
    9. Paid In Full Discount  
    10. Miscellaneous Premium  

    11. Location  
        - Must capture all risk location details (address, suite, city, state, ZIP).  
        - If labeled as "Location", "Premises", "Risk Address", "Schedule of Locations", or "Description of Premises", extract it.  
        - If multiple locations exist, return all of them in an array.  
        - If no separate location is listed, but the insured premises address matches the mailing address, return that under Location as well.  

    12. Property (look across declarations, schedules, endorsements, and forms)  
        - Building Value:  
            * Search for "DESCRIPTION OF PREMISES:", "Building Value", "Building Limit", "Limit of Insurance", "Coverage A - Building", "Building Coverage", "Building Amount".  
            * Always include PREM and BLDG identifiers if available.  
            * Format: "PREM x - BLDG y - Building - $<amount> - <coverage description>".  
            * Example: "PREM 2 - BLDG 1 - Building - $1,007,000 - Special Form Including Theft".  
            * Return multiple buildings in an array.  
        - Business Income Limit  
        - Improvements and Betterments  
        - Wind and Hail (if included or excluded)  
        - Property Deductible (search for all deductibles, including general and peril-specific).  
        - Co-Insurance:  
            * Always capture with PREM and BLDG context.  
            * Example: "PREM 1 - BLDG 1 - 80%".  
        - Valuation:  
            * Extract basis per building (RC = Replacement Cost, ACV = Actual Cost Value, etc.).  
            * Format: "PREM x - BLDG y - <valuation text>".  
        - Is Equipment Breakdown Listed?  
        - Building Ordinance or Law Coverage A  
        - Building Ordinance Demolition Cost Coverage B  
        - Building Ordinance Increased Cost of Construction Coverage C  
        - Additional Interests (e.g., Mortgage Holders)  

    13. Terrorism → {{"Coverage": "string", "Premium": "string", "Exclusions": ["string"], "Inclusion_Status": "string"}}  
    14. Exclusions → all exclusions explicitly listed in the policy  
    15. Additional Interest → [{{"Name": "string", "Address": "string", "Role": "string"}}]  
    16. Additional Coverage(s) → include all additional coverages  

    17. Forms And Endorsements  
        - **Collect every form across the entire document**, including but not limited to
          Property, General Liability, Auto, Umbrella, Notices, and State filings.  
        - Do NOT stop at the first "Forms and Endorsements" heading—scan to the end of
          the document.  
        - Merge lines if a form number or title is split.  
        - Normalize strictly into this format:  
          "FormNumber (MM-YY) | MM/YY   Form Title"  
        - Return **all forms** as a single JSON array, even if they belong to different
          coverage parts.

    18. Endorsements  
        - Extract every endorsement with Title, Effective Date, and any available details.  
        - Merge multi-line descriptions into one string.

    ### Output Rules
    - Return **only a valid JSON object** with the above keys.
    - Dates → MM/DD/YYYY
    - Currency → preserve `$` and commas
    - Arrays → [] if not found
    - Missing values → null

    {f'Text: {large_text}' if large_text else ''}
    """

def prompt_template_business_owner(large_text=None):
    return f"""
    You are an expert insurance data extractor.
    The following text is extracted from a Business Owner’s Policy (BOP) insurance PDF
    using a mix of digital text, OCR text, Rows and tables.

    ### Extraction Rules
    - **Search through the ENTIRE document for every required field**.
    - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
      Continue scanning to the **very end of the document**.
    - Merge multi-line form numbers/titles into a **single entry** if they are split
      across lines or pages.
    - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
    - Deduplicate only when text is truly identical.
    - If a field is missing, set it to `null`; if an array is empty, return `[]`.
    - Output must be **only** a valid JSON object. No explanations or commentary.

    ### Datapoints to Extract ###
    1. Name Insured
    2. Other Named Insured (DBA)
    3. Additional Insured
    4. Mailing Address
    5. Policy Number
    6. Policy Period
    7. Issuing Company
    8. Premium
        - include all coverage premiums and total premium
    9. Paid In Full Discount
    10. Miscellaneous Premium
    11. Location
        Example:["PREM": "001",
            "BLDG": "001",
            "Address": "235 E MAIN ST STE 102A",
            "City": "NORTHVILLE",
            "State": "MI",
            "Zip": "48167",]
    12. General Liability: (need to extract text along with value, example: "Medical expenses": "$10,000 any one person")
       - General Aggregate
       - Products or Completed Operations Aggregate
       - Personal And Advt Injury
       - Medical expenses
       - Damage to rented premises
       - Each Occurrence
       - Deductible
       - Hired Or Non Owned Auto
       - Schedule of Hazards Rating Info (extract *every* row/column, search entire document to get all data, return all rows and columns)
           - Loc/BLDG No
           - TERR
           - Classification Code
           - Coverage description
           - Description
           - Rating Basis
           - Exposure
           - Final Rate
           - Advance Premium
       - Additional Interest
    13. Employee Benefits Liability
    14. Directors and Officers
    15. Cyber
    16. Professional Liability
    17. EPLI on Policy
    18. Errors and Omissions on Policy
    19. Terrorism
    20. Work Exclusion
    21. Liability locations match property locations if applicable
    22. Property
            -Building Value
            -Business Personal Property Limit
            -Business Income Limit
            -Improvements and Betterments
            -Wind And Hail
            -Property Deductible
            -Co Insurance
            -Valuation
            -Is Equipment Breakdown Listed
            -Building Ordinance Or Law Listed Cov A
            -Building Ordinance Demolition Cost Cov B
            -Building Ordinance Inc Cost Of Construction Cov C
            -Additional Interests
    23. Property Terrorism
    24. Inland Marine Details
    25. Equipment Schedule
    26. Deductibles
    27. Loss Payee
    28. Rental equipment from others
    29. Rental equipment to others
    30. Installation floater
    31. Inland Marine Terrorism
    32. Umbrella Limits
    33. Underlying Policies + *Must include all underlying policies, return all rows and colomns under this section*
    34. Policy Exclusions (Note: Only mention Policy Exclusions not Exclusions)
    35. Additional Coverage(s)

    36. Forms And Endorsements
        - **Collect every form across the entire document**, including Property,
          General Liability, Auto, Umbrella, Notices, and any state filings.
        - Do NOT stop at the first “Forms and Endorsements” heading.
        - Merge split lines into one entry.
        - Normalize each entry strictly in this format:
          "FormNumber (MM-YY) | MM/YY   Form Title"
        - Return **all forms** as a single JSON array.

    37. Endorsements
        - Extract every endorsement with Title, Effective Date, and any available details.
        - Merge multi-line descriptions into one string.
        - Return all endorsements as a JSON array.

    ### Output Rules
    - Return **only** the structured JSON object with the keys above in the exact order.
    - Dates → MM/DD/YYYY
    - Currency → keep "$" and commas as shown.
    - Arrays → [] if not found.
    - Missing values → null.

    ### Critical Extraction Enforcement ###
    - Pay *special attention* to **Schedule of Hazards Rating Info**.
    - Treat every line, even if repetitive or unclear, as **a separate row**.
    - Do NOT summarize or skip rows.
    - Output **every row and column** in this section, even partial or unclear text.
    - If text alignment is messy (OCR lines not aligned), reconstruct into columns logically:
        ["Loc/BLDG No", "TERR", "Classification Code", "Coverage Description", "Description", "Rating Basis", "Exposure", "Final Rate", "Advance Premium"]
    - Example output format for each row:
        {{"Loc/BLDG No": "001", "TERR": "01", "Classification Code": "12345", ...}}

    {f'Text: {large_text}' if large_text else ''}
    """

# def prompt_template_package(large_text=None):
#     """
#     Enhanced PACKAGE (Business Owner) template.
#     ✅ Compatible with new multi-turn + fuzzy key pipeline
#     ✅ Retains special formats, examples and array rules
#     """
#     return f"""
#     You are an expert insurance data extractor.
#     The following text is extracted from a Business Owner’s (PACKAGE) insurance PDF
#     using a mix of digital text, OCR text, and tables.

#     ### Extraction Rules
#     - Search the **ENTIRE document** (all pages, all chunks).
#     - Do **not** stop at the first heading (e.g. “Forms and Endorsements”).
#     - Merge multi-line form numbers/titles into a single entry.
#     - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
#     - Deduplicate only when text is truly identical.
#     - If a field is missing → `null` (or `[]` for arrays).
#     - Output must be **one valid JSON object** only.

#     ### Datapoints to Extract
#     1. Name Insured
#     2. Other Named Insured (DBA)
#     3. Additional Insured
#     4. Mailing Address
#     5. Policy Number
#     6. Policy Period  →  {{ "Start": "MM/DD/YYYY", "End": "MM/DD/YYYY" }}
#     7. Issuing Company
#     8. Premium → include all coverage-level premiums and total premium
#     9. Paid In Full Discount
#     10. Miscellaneous Premium
#     11. Location
#         - Must return **exact** PREM/BLDG style.
#         - Example: "LOC - 1 - 10424 N 14500E Rd - Grant Park - IL - 60940"
#     12. General Liability
#         - Include every sub-limit with value:
#             - General Aggregate
#             - Products or Completed Operations Aggregate
#             - Personal And Advt Injury
#             - Medical expenses
#             - Damage to rented premises
#             - Each Occurrence
#             - Deductible
#             - Hired Or Non Owned Auto
#         - Schedule of Hazards Rating Info
#             - Capture *every* row/column across the document.
#             - Return as array of full rows in this format:
#               {{
#                 "Loc/BLDG No": "...",
#                 "TERR": "...",
#                 "Classification Code": "...",
#                 "Coverage description": "...",
#                 "Description": "...",
#                 "Rating Basis": "...",
#                 "Exposure": "...",
#                 "Final Rate": "...",
#                 "Advance Premium": "..."
#               }}
#     13. Employee Benefits Liability
#     14. Directors and Officers
#     15. Cyber → include all premiums or sub-coverages if spread across pages
#     16. Professional Liability
#     17. EPLI on Policy → include Bodily Injury details if present
#     18. Errors and Omissions on Policy
#     19. Terrorism
#     20. Work Exclusion
#     21. Liability locations match property locations if applicable (true/false)
#     22. Property
#         -Building Value
#         -Business Personal Property Limit
#         -Business Income Limit
#         -Improvements and Betterments
#         -Wind And Hail (include PREM and BLDG)
#         -Property Deductible
#         -Co Insurance
#         -Valuation
#         -Is Equipment Breakdown Listed
#         -Building Ordinance Or Law Listed Cov A
#         -Building Ordinance Demolition Cost Cov B
#         -Building Ordinance Inc Cost Of Construction Cov C
#         -Additional Interests
#     23. Property Terrorism
#     24. Inland Marine Details
#     25. Equipment Schedule (capture all rows even if split across chunks)
#     26. Deductibles (capture all rows even if split across chunks)
#     27. Loss Payee
#         - Example:
#           {{
#             "Location Number": "0001",
#             "Building Number": "0001",
#             "Name": "Wesleyan Investment Foundation",
#             "Address": "Po Box 7250, Fishers, IN 46038"
#           }}
#     28. Rental equipment from others
#     29. Rental equipment to others
#     30. Installation floater
#     31. Inland Marine Terrorism
#     32. Umbrella Limits
#     33. Underlying Policies
#         - Must include **all** underlying policies with all rows/columns.
#     34. Policy Exclusions  (Note: Only policy-level exclusions)
#     35. Additional Coverage(s)
#         - Include every additional coverage with exact labels and values.

#     36. Forms And Endorsements
#         - **Collect every form across the entire document**.
#         - Do NOT stop after the first section.
#         - Merge split lines into one entry.
#         - Normalize strictly:
#           "FormNumber (MM-YY) | MM/YY   Form Title"
#         - Return as a single JSON array.

#     37. Endorsements
#         - Extract every endorsement with Title, Effective Date, and any available details.
#         - Merge multi-line descriptions into one string.
#         - Return all endorsements as a JSON array.

#     ### Output Rules
#     - Output only a single valid JSON object.
#     - Dates → MM/DD/YYYY
#     - Currency → preserve "$" and commas
#     - Arrays → [] if not found
#     - Missing values → null

#     {f'Text: {large_text}' if large_text else ''}
#     """


def prompt_template_package(large_text=None):
    """
    Enhanced Business Owner (BOP) prompt – matches the style of the updated property
    prompt but keeps the original business_owner datapoints unchanged.
    """
    return f"""
    You are an expert insurance data extractor.
    The following text is extracted from a Business Owner’s Policy (BOP) insurance PDF
    using a mix of digital text, OCR text, and tables.

    ### Extraction Rules
    - **Search through the ENTIRE document for every required field**.
    - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
      Continue scanning to the **very end of the document**.
    - Merge multi-line form numbers/titles into a **single entry** if they are split
      across lines or pages.
    - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
    - Deduplicate only when text is truly identical.
    - If a field is missing, set it to `null`; if an array is empty, return `[]`.
    - Output must be **only** a valid JSON object. No explanations or commentary.

    ### Datapoints to Extract ###
    1. Name Insured
    2. Other Named Insured (DBA)
    3. Additional Insured
    4. Mailing Address
    5. Policy Number
    6. Policy Period
    7. Issuing Company
    8. Premium
        - include all coverage premiums and total premium
    9. Paid In Full Discount
    10. Miscellaneous Premium
    11. Location
        Example: "LOC - 1 - 10424 N 14500E Rd - Grant Park - IL - 60940"
    12. General Liability: (need to extract text along with value, example: "Medical expenses": "$10,000 any one person")
            - General Aggregate
            - Products or Completed Operations Aggregate
            - Personal And Advt Injury
            - Medical expenses
            - Damage to rented premises
            - Each Occurrence
            - Deductible
            - Hired Or Non Owned Auto
            - Schedule of Hazards Rating Info 
                - extract *every* row/column, search entire document to get all data, return all rows and columns
                - search entire chunks and return all data under this section
                - Search for classifiaction chunks and return all datapoints mentioned below
                    - Loc/BLDG No
                    - TERR
                    - Classification Code
                    - Coverage description
                    - Description
                    - Rating Basis
                    - Exposure
                    - Final Rate
                    - Advance Premium
                    - Additional Interest
    13. Employee Benefits Liability
    14. Directors and Officers
    15. Cyber
            - this data may spread across multiple pages, so search entire documnet and return all of them
            - search entire chunks
    16. Professional Liability
    17. EPLI on Policy
        - search for "Employers' Liability Insurance" etc and return all details
        - Example : [Bodily Injury by Accident
                    Bodily Injury by Disease
                    Bodily Injury by Disease]
    18. Errors and Omissions on Policy
        - This data may spread across multiple chunks, so all chunks and return all data
    19. Terrorism
    20. Work Exclusion
    21. Liability locations match property locations if applicable
        - Return Exact output if it is true
    22. Property + extract along with buiding and premisis numbers
            -Building Value
            -Business Personal Property Limit
            -Business Income Limit
            -Improvements and Betterments
            -Wind And Hail + need to extract data along with locaction number and building number
            -Property Deductible
            -Co Insurance
            -Valuation
            -Is Equipment Breakdown Listed
            -Building Ordinance Or Law Listed Cov A
            -Building Ordinance Demolition Cost Cov B
            -Building Ordinance Inc Cost Of Construction Cov C
            -Additional Interests
    23. Property Terrorism
    24. Inland Marine Details
    25. Equipment Schedule
        - This data may spread across multiple chunks, so all chunks and return all data
    26. Deductibles
        - This data may spread across multiple chunks, so all chunks and return all 
    27. Loss Payee
        - Example :[
            "Location Number" : 0001,
            "Building Number" : 0001,
            "Name": "Wesleyan Investment Foundation",
            "Address": "Po Box 7250, Fishers, IN 46038"
            ]
    28. Rental equipment from others
    29. Rental equipment to others
    30. Installation floater 
        - search floater on entire document and return all data
    31. Inland Marine Terrorism
        - Search for inland marine or marine terrorism etc, and return deatils under them
    32. Umbrella Limits
    33. Underlying Policies
        - *Must include all underlying policies, return all rows and colomns under this section*
    34. Policy Exclusions (Note: Only mention Policy Exclusions not Exclusions)
    35. Additional Coverage(s)
        - Include coverage with their exact labels and values
        - Return all additional or coverage details
        - Search entire document or search coverage shedule and return all the data

    36. Forms And Endorsements
        - **Collect every form across the entire document**, including Property,
          General Liability, Auto, Umbrella, Notices, and any state filings.
        - Do NOT stop at the first “Forms and Endorsements” heading.
        - This data may spread across multipe pages, so do not stop after getting few forms, return all forms present in the entire document
        - Merge split lines into one entry.
        - Normalize each entry strictly in this format:
          "FormNumber (MM-YY) | MM/YY   Form Title"
        - Return **all forms** as a single JSON array.

    37. Endorsements
        - Extract every endorsement with Title, Effective Date, and any available details.
        - Merge multi-line descriptions into one string.
        - Return all endorsements as a JSON array.

    ### Output Rules
    - Return **only** the structured JSON object with the keys above in the exact order.
    - Dates → MM/DD/YYYY
    - Currency → keep "$" and commas as shown.
    - Arrays → [] if not found.
    - Missing values → null.

    {f'Text: {large_text}' if large_text else ''}
    """