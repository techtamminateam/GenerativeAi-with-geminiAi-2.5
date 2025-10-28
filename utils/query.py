def prompt_template_cyber(large_text=None):

    return f"""
        You are an expert insurance data extractor.
        The following text is extracted from a cyber insurance PDF
        using a mix of digital text, OCR text, Rows and tables.

        ### Extraction Rules
        - **Search through the ENTIRE document for every required field**.
        - Dates must always be in MM/DD/YYYY format.
        - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
        Continue scanning to the **very end of the document**.
        - Merge multi-line form numbers/titles into a **single entry** if they are split
        across lines or pages.
        -socialengineering,businessinterruption,privacybreachresponseservices ( do not extract these values in additional coverages)these data should be extracted under individual datapoints
        - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
        - Deduplicate only when text is truly identical.
        - If a field is missing, set it to `null`; if an array is empty, return `null`.
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
            10. Miscellaneous Premium
            11. Additional Coverage(s): (get all the possible information of coverages and sublimits of liability, return only value is present otherwise keep it has null)
            12. Forms and Endorsements: 
                Forms And Endorsements
                    - **Collect every form across the entire document**, including Property,
                    General Liability, Auto, Umbrella, Notices, and any state filings.
                    - Do NOT stop at the first “Forms and Endorsements” heading.
                    - Merge split lines into one entry.
                    - Normalize each entry strictly in this format:
                    "FormNumber | MM/YY   Form Title"
                    - Return **all forms** as a single JSON array.
            13. Endorsements: (don't include limits or Retention, and show when any of this is mentioned modified/changed/deleted/added details)
            14. Location (Extract only if it is present location address otherwise keep it has null)
            15. Exclusions: (return null value for this datapoint)
            16. Limits of Liability: (must list oliy liability limits with amounts which are not extracted in additional coverages section)
            17. Privacy Breach Response Services: (Limit value not premium)
            18. Business Interruption: (Limit value not premium)
            19. Media: (Limit value not premium)
            20. Social Engineering: (Limit value not premium)
            21. Terrorism: (return only if premium exist else keep it has null dont mention like "Waived")
            22. Deductible or Retention: 
            23. Retroactive Date[s]: (Extract only date)
            24. Prior and Pending Date: 
            25. Continuity Date[s]:
            26. Underlying Insurance: (list of insurance with details)

            {f'Text: {large_text}' if large_text else ''}

            Return only a pure JSON object, assigning null to any key without a corresponding value.
            """

def prompt_template_general(large_text=None):
    return f"""You are an expert insurance data extractor.
            The following text is extracted from a General insurance PDF
            using a mix of digital text, OCR text, Rows and tables.

            ### Extraction Rules
            - **Search through the ENTIRE document for every required field**.
            - **If a value is not explicitly present in the text, do NOT guess or invent it.**
            - Only extract values that are clearly present in the document.
            - If a field is missing, set it to `null`; if an array is empty, return `[]`.
            - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
            Continue scanning to the **very end of the document**.
            - Merge multi-line form numbers/titles into a **single entry** if they are split
            across lines or pages.
            - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
            - Deduplicate only when text is truly identical.
            - Output must be **only** a valid JSON object. No explanations or commentary.
            - **Never fabricate, infer, or assume values. Only copy what is present.**

            ### Datapoints to Extract ###
            1. Name Insured (primary insured)
            2. Other Named Insured (DBA) (other named insureds)
            3. Additional Insured
            4. Mailing Address
            5. Policy Number
            6. Policy Period
            7. Issuing Company
            8. Premium
                - include all coverage premiums and total premium
            9. Paid In Full Discount
            10. Miscellaneous Premium
            11. Location (example:PREM 1 - 600 HARRISON ST FLOORS 3&4 - SAN FRANCISCO - CA - 94107)
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
                Examle: "employeebenefitsliability": [
                    "Each Claim Limit": "$ 1,000,000",
                    "Aggregate Limit": "$ 1,000,000",
                    "Deductible": "$ 2,500 Each Claim",
                    "Retroactive Date": "06/30/2023"
                ]
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
            23. Property Terrorism (data which is present in buidling prperty values under property declarations)
            24. Inland Marine Details
            25. Equipment Schedule
            26. Deductibles (extract only deductibles mentioned undder this section, not extract from other sections)
            27. Loss Payee (loss payee/ mortgage)
            28. Rental equipment from others
            29. Rental equipment to others
            30. Installation floater
            31. Inland Marine Terrorism (terrosion present under the inland marine page should be extracted)
            32. Umbrella Limits (Limits present under umbrella coverages)
            33. Underlying Policies(Extract only data ubder this section and return full details)
            34. Policy Exclusions (Note: Only mention Policy Exclusions not Exclusions)
            35. Additional Coverage(s)(Extract on coverages and their values)

            36. Forms And Endorsements
                - Extraction only forms from "Forms And Endorsements" section.
                - Normalize each entry strictly in this format:
                "FormNumber | MM/YY   Form Title" (if coverage also exist return as BOP BP0159 |  08/08  WATER EXCLUSION ENDORSEMENT )
                - Return **all forms** as a single JSON array.

            37. EndorsementsEndorsements (Data under Description of changes should be extracted(changed, added, deleted, estimated total premium, paid in full discount))
                - Extract only from particular endorsement declaration page

            ### Output Rules
            - Return **only** the structured JSON object with the keys above in the exact order.
            - Dates → MM/DD/YYYY
            - Currency → keep "$" and commas as shown.
            - Missing values → null.

            {f'Text: {large_text}' if large_text else ''}
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
                - If a datapoint is missing, explicitly set it to null (or null for arrays).  
                - Do not assume or invent values — only return if present.  
                - Output must be a pure JSON object with no extra commentary.
            ### Datapoints to Extract ###
            1. Name Insured  
            2. Other Named Insured (DBA)  
            3. Additional Insured → [{{Name, Address}}]  
            4. Mailing Address  
            5. Policy Number  
            6. Policy Period → (MM/DD/YYYY to MM/DD/YYYY) 
            7. Issuing Company  
            8. Premium (extract only coverage premiums and total premium, not vehicles, taxes or fees) 
            9. Paid In Full Discount  
            10. Miscellaneous Premium (extract only if present, else keep it has null) 
            11. Location (Extract location under declaration page only, if multiple locations return all locations in array otherwise null)
            12. Symbol (extract only which was selected by crossmark)
                - Example:"symbol": [
                        "Combined Liability": "7, 8, 9, 19",
                        "Uninsured Motorist": "6",
                        "Underinsured Motorist": "6",
                        "Personal Injury Protection": "7",
                        "Comprehensive": "7",
                        "Collision": "7",
                        "Road Trouble Service": "7",
                        "Additional Expense": "7"]
            13. Limits (return only coverage limits with values, when there is no value dont extract the label)
                - Example: [LIABILITY- BI EACH ACCIDENT : $1000000
                            MEDICAL PAYMENTS -EACH PERSON : $5000]
            14. Vehicles Info 
                - Must capture all vehicles listed with full details
                - Return each vehicle in the specified format
                - Example: "Unit : 1. - VIN : 1FTNX21F93EB04329 - Year : 2003 - Make : FORD - Model : F250 - PREMIUM : $1,612.57"  
                - If model is null then output should be like this: "Unit : 1. - VIN : 1FTNX21F93EB04329 - Year : 2003 - Make : FORD - PREMIUM : $1,612.57"
                - Return costnew values also if and if it is present under this section only
            15. Scheduled Drivers → [{{NameLast, FirstName, DOB or Age, State, License Number, Premium}}]  
            16. Hired Or Non-Owned Auto Limits → {{Hired Autos Liability, Non-Owned Autos Liability}}  
            17. Drive Other Car Coverage   (Extract only if data present at declaration page, else keep it has null)
            18. Terrorism (Extrcat only if data present at premiums or schedule of terrorism act page, Only return if it has numerical value else return null)  
            19. Exclusions (Extrcat only if data present at this particular section)  
            20. Additional Interest → [{{Name, Address, Role if specified}}]  
            21. Additional Coverage(s) (include coverage which are not extracted in previous datapoints only, and return label which consists values only) 
            22. Forms and Endorsements: 
                Forms And Endorsements
                    - **Collect every form across the entire document**, including Property,
                    General Liability, Auto, Umbrella, Notices, and any state filings.
                    - Do NOT stop at the first “Forms and Endorsements” heading.
                    - Merge split lines into one entry.
                    - Normalize each entry strictly in this format:
                    "FormNumber | MM/YY   Form Title"
                    - Return **all forms** as a single JSON array.
            23. EndorsementsEndorsements (Data under Description of changes should be extracted(changed, added, deleted, estimated total premium, paid in full discount))
                    - Extract only from particular endorsement declaration page
            ### Final Output Rules ###
            - Must return a single valid JSON object only.  
            - Missing datapoints must be null.  
            ### Special Priority ###
            Ensure **all datapoints** are extracted if present.  
            Pay particular attention to **Vehicles Info** and **Scheduled Drivers**, as these often appear in structured tables.  
            Do not skip or truncate them.  

            ### DOCUMENT CONTENT ###
            {f'Text: {large_text}' if large_text else ''}
            """

def prompt_template_general_liability(large_text=None):
    return f"""
            The following text is extracted from a insurance PDF
            using a mix of digital text, OCR text, Rows and tables.
            ### Extraction Rules
            -for following datapoints the data should be extracted which is present under the that particular declaration page only :
                1.Employee Benefits Liability
                2.Directors and Officers
                3.Cyber
                4.Professional Liability
                5.EPLI on Policy
                6.Inland Marine Details
                7.Equipment Schedule
            - **Search through the ENTIRE document for every required field**.
            - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
            Continue scanning to the **very end of the document**.
            - Merge multi-line form numbers/titles into a **single entry** if they are split
            across lines or pages.
            - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
            - Deduplicate only when text is truly identical.
            - If a field is missing, set it to `null`; if an array is empty, return `null`.
            - Output must be **only** a valid JSON object. No explanations or commentary.

            ### Datapoints to Extract ###
            1. Name Insured (name primary insured)
            2. Other Named Insured (DBA) - (DBA, alternate names, or any entity listed as an additional named insured, including "doing business as", "DBA", "Also Known As", "a/k/a", "t/a", "f/k/a", or similar labels. Extract all such names and return as an array. If none, return null.)
            3. Additional Insured: Includes any party listed as an additional insured under the same entity name, a separate named insured, or a 'doing business as' (DBA) designation.
            4. Mailing Address
            5. Policy Number (extract only policy number not any other text around it or any other number like reactivation number, renewal no etc)
            6. Policy Period (MM/DD/YYYY to MM/DD/YYYY)
            7. Issuing Company
            8. Premium
                - include all coverage premiums and total premium
            9. Paid In Full Discount
            10. Miscellaneous Premium
            11. Location (Extract Full location details icluding premises number, building number, suite, city, state, zip etc if and they exist in lacation section only)
                -Example: [ "PREM": "001","BLDG": "001", "Address": "3690 NW Adriatic Lane #107","City": "Jensen Beach","State": "FL","Zip": "34957"]
            12. General Liability: 
                - Extract the value **only from the "General Liability declaration page or section"**. Do not extract from other sections, schedules, or tables.
                - For each, include both the value (e.g., "$5,000") and any descriptive text that appears after the value (e.g., "Per Occurrence", "Any One Premise", etc.).
                - Output format for each: "<value> <descriptive text after value>" , not like "Medical expenses": "$10,000 Per Occurrence",
                    - General Aggregate
                    - Products or Completed Operations Aggregate
                    - Personal And Advt Injury
                    - Medical expenses
                    - Damage to rented premises
                    - Each Occurrence
                    - Deductible (when there is no numerical value dont extract the label)
                    - Hazards Rating Info (Must extract each and every data related to this and extract full data of each row and columns with their respective exact headers and values, dont summarize or skip any rows only skip which are not in tabular format)
            13.Employee Benefit Liability Coverage
            14.Hired And Non owned Coverage (don't extract from auto liability page)
            15.Directors and Officers
            16.Cyber(data should be extracted only which is present under the that particular "cyber" declaration page only)
            17.Professional Liability
            18.EPLI on Policy
            19.Errors and Omissions on Policy (Extract only from the "Errors and Omissions" declaration page or section)
            20.Terrorism (Extract only if it has a numerical value otherwise keep it has null)
            21.Work Exclusion (Extract only if it has a numerical value otherwise donot extract, if no data extected keep it as null)
            22.Additional Interest
            23.Additional Coverage (return all coverages with values,when there is no value dont extract the label)
            24.Forms And Endorsements
                - Extraction only forms from "Forms And Endorsements" section.
                - Normalize each entry strictly in this format:
                "FormNumber | MM/YY   Form Title" (if coverage also exist return as BOP BP0159 |  08/08  WATER EXCLUSION ENDORSEMENT )
                - Return **all forms** as a single JSON array
            25.EndorsementsEndorsements (Data under Description of changes should be extracted(changed, added, deleted, estimated total premium, paid in full discount))
                - Extract only from particular endorsement declaration page otherwise keep it null

        

            ### Retrieved Sections
            {f'Text: {large_text}' if large_text else ''}

            ### Final Output
            ### Output Rules
            - Return **only** the structured JSON object with the keys above in the exact order.
            - Dates → MM/DD/YYYY
            - Currency → keep "$" and commas as shown.
            - Missing values → null.
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
    -for following datapoints the data should be extracted which is present under the that particular declaration page only 
        1.Employee Benefits Liability
        2.Directors and Officers
        3.Cyber
        4.Professional Liability
        5.EPLI on Policy
        6.Inland Marine Details
        7.Equipment Schedule
    -NO data for these datapoints, pass them as null:
        Policy Exclusions
        Rental equipment from others
        Rental equipment to others
        Work Exclusion
        Liability locations match property locations if applicable
        Miscellaneous Premium 
    - **Search through the ENTIRE document for every required field**.
    - Do NOT stop at the first heading of “Forms and Endorsements” or “Endorsements”.
      Continue scanning to the **very end of the document**.
    - Merge multi-line form numbers/titles into a **single entry** if they are split
      across lines or pages.
    - Preserve all numbers, dates, symbols, and formatting exactly as they appear.
    - Deduplicate only when text is truly identical.
    - If a field is missing, set it to `null`; if an array is empty, return `null`.
    - Output must be **only** a valid JSON object. No explanations or commentary.

    ### Datapoints to Extract ###
    1. Name Insured
    2. Other Named Insured (DBA)
    3. Additional Insured (it will be with same name or other named insured or DBA )
    4. Mailing Address
    5. Policy Number
    6. Policy Period
    7. Issuing Company
    8. Premium 
    9. Paid In Full Discount (Present in premium( need to extract the data which is present under discounted premium))
    10. Miscellaneous Premium(like taxes, fees, surcharges etc, if amount not found return null)
    11. Location
        - Extract location details **only from the "declaration of location" page or section**.
        - Do not extract location data from other sections, schedules, or tables.
        - If multiple locations are listed in the declaration of location, return all as an array.
        - If no location is found in the declaration of location, set this field to null.
    12. General Liability:
        - Extract the value **only from the "General Liability declaration page or section"**. Do not extract from other sections, schedules, or tables execpt for Schedule of Hazards Rating Info.
        - *Schedule of Hazards Rating Info* if these details are present in this section, then extract data from other section or table which consists the Class code, Description, Rating Basis, Exposure, Final Rate, Advance Premium etc. 
        - For each, include both the value (e.g., "$5,000") and any descriptive text that appears after the value (e.g., "Per Occurrence", "Any One Premise", etc.).
        - Output format for each: "<value> <descriptive text after value>" , not like "Medical expenses": "$10,000 Medical Expenses Limit",
        - Example: 
            - "Medical expenses": "$5,000 Per Occurrence"
            - "Personal And Advt Injury": "$1,000,000 Per Occurrence"
            - "Damage to rented premises": "$50,000 Any One Premise"
        - Datapoints (each as a separate key in the output):
            - General Aggregate
            - Products or Completed Operations Aggregate
            - Personal And Advt Injury
            - Medical expenses
            - Damage to rented premises
            - Each Occurrence
            - Deductible
            - Hired Or Non Owned Auto
            - Advance Premium
            - Additional Interest
            - For "Schedule of Hazards Rating Info". Return as an array of dictionaries, each with:
                - Loc/BLDG No
                - TERR
                - Classification Code
                - Coverage description
                - Description
                - Rating Basis
                - Exposure
                - Final Rate
                - Advance Premium
    13. Employee Benefits Liability
    14. Directors and Officers
    15. Cyber(data should be extracted only which is present under the that particular "cyber" declaration page only)
    16. Professional Liability
    17. EPLI on Policy
    18. Errors and Omissions on Policy
    19. Terrorism (Extrcat only if data present at premiums or schedule of terrorism act page)
    20. Work Exclusion
    21. Liability locations match property locations if applicable
    22. Property (Need to extract the datapoints in individual dictionary but not under the general liability dictionary, And this data should be extracted which is present under the property declaration page only)
            -Building Value
            -Business Personal Property Limit(need to extract prem.no,bldg.no labels and its values along with limit data)
            -Business Income Limit
            -Improvements and Betterments
            -Wind And Hail
            -Property Deductible(need to extract prem.no,bldg.no labels and its values along with limit data and all deductible under this section only)
            -Co Insurance
            -Valuation
            -Is Equipment Breakdown Listed
            -Building Ordinance Or Law Listed Cov A
            -Building Ordinance Demolition Cost Cov B
            -Building Ordinance Inc Cost Of Construction Cov C
            -Additional Interests
    23. Property Terrorism (data which is present in buidling prperty values under property declarations)
    24. Inland Marine Details
    25. Equipment Schedule
    26. Deductibles (extract only deductibles mentioned undder this section, not extract from other sections)
    27. Loss Payee (loss payee/ mortgage)
    28. Rental equipment from others
    29. Rental equipment to others
    30. Installation floater
    31. Inland Marine Terrorism (terrosion present under the inland marine page should be extracted)
    32. Umbrella Limits (Limits present under umbrella coverages)
    33. Underlying Policies(Extract only data ubder this section and return full details)
    34. Policy Exclusions (Note: Only mention Policy Exclusions not Exclusions)
    35. Additional Coverage(s)(Extract on coverages and their values)

    36. Forms And Endorsements
        - Extraction only forms from "Forms And Endorsements" section.
        - Normalize each entry strictly in this format:
          "FormNumber | MM/YY   Form Title" (if coverage also exist return as BOP BP0159 |  08/08  WATER EXCLUSION ENDORSEMENT )
        - Return **all forms** as a single JSON array.

    37. EndorsementsEndorsements (Data under Description of changes should be extracted(changed, added, deleted, estimated total premium, paid in full discount))
        - Extract only from particular endorsement declaration page

    ### Output Rules
    - Return **only** the structured JSON object with the keys above in the exact order.
    - Dates → MM/DD/YYYY
    - Currency → keep "$" and commas as shown.
    - Missing values → null.

    {f'Text: {large_text}' if large_text else ''}
    """

def prompt_template_package(large_text=None):
    return f"""You are an expert insurance data extractor. Extract data from the Package insurance PDF text below with ABSOLUTE CONSISTENCY.

            ### CRITICAL CONSISTENCY RULES
            1. Extract EXACTLY what is written - no interpretation, no inference
            2. Use IDENTICAL formatting patterns for similar data types
            3. When multiple valid options exist, ALWAYS choose the FIRST occurrence
            4. If uncertain between multiple values, return ALL as comma-separated string
            5. Preserve original spacing, punctuation, and case EXACTLY as shown
            6. **FOR PROPERTY FIELDS: NEVER extract just the value - ALWAYS include the complete location/building identifiers in the EXACT format shown in the document**
            - WRONG: "Co Insurance": "80%"
            - CORRECT: "Co Insurance": ["LOCATION : # 1 - BUILDING # 1 - Building : 80%"]
            - WRONG: "Valuation": "RC"
            - CORRECT: "Valuation": ["Location Number : 0001 - Building Number : 001 - Building - Replacement Cost"]

            ### SCOPE RULES (CRITICAL - READ CAREFULLY)
            Extract data ONLY from these specific declaration pages/sections:
            - Employee Benefits Liability → Only from its declaration page
            - Directors and Officers → Only from its declaration page  
            - Cyber → Only from "Cyber" declaration page
            - Professional Liability → Only from its declaration page
            - EPLI on Policy → Only from its declaration page
            - Inland Marine Details → Only from its declaration page
            - Equipment Schedule → Only from its declaration page
            - Property → Only from Property declaration page
            - General Liability → Only from General Liability declaration page (EXCEPTION: Schedule of Hazards may reference other sections)

            ### NULL VALUES (Set these to null - do NOT search for them)
            - Policy Exclusions
            - Rental equipment from others
            - Rental equipment to others
            - Work Exclusion
            - Liability locations match property locations if applicable
            - Miscellaneous Premium

            ### EXTRACTION DATAPOINTS

            **1. Name Insured**
            - Extract: Full legal name as shown on declaration page
            - Format: Exact text as written

            **2. Other Named Insured (DBA)**
            - Extract: Any DBA or alternate business names
            - Format: Exact text, or null if absent

            **3. Additional Insured**
            - Extract: Names listed as additional insured
            - Format: If multiple, return as array; otherwise single string

            **4. Mailing Address**
            - Extract: Complete mailing address
            - Format: Single line with commas: "Street, City, ST Zip"

            **5. Policy Number**
            - Extract: Policy/contract number
            - Format: Exact alphanumeric as shown

            **6. Policy Period**
            - Extract: Start and end dates
            - Format: "MM/DD/YYYY to MM/DD/YYYY"

            **7. Issuing Company**
            - Extract: Insurance company name
            - Format: Exact text as written

            **8. Premium**
            - Extract: ALL premium line items from premium section up to "Total Premium"
            - Format: Object with keys as premium labels, values as amounts
            - Example: {{"General Liability Premium": "$5,000", "Property Premium": "$3,000", "Total Premium": "$8,000"}}
            - Include currency symbol and commas

            **9. Paid In Full Discount**
            - Extract: Discount amount from discounted premium section
            - Format: "$X,XXX" or null

            **10. Miscellaneous Premium**
            - Status: ALWAYS return null (per scope rules)

            **11. Location**
            - Extract: ONLY from "Declaration of Location" page/section
            - Format: "LocNum Address, City, ST Zip"
            - Example: "1 1731 W Business U.S. 60, Dexter, MO 63841"
            - If multiple: return as array
            - If none in Declaration of Location: null

            **12. General Liability**
            Extract ONLY from General Liability declaration or Commercial General Liability declaration page or section or shedule. Each field format: "Value Description"

            Required fields (each as separate key):
            - "General Aggregate": "$X,XXX,XXX Per Occurrence" (include descriptor after value)
            - "Products or Completed Operations Aggregate": "$X,XXX,XXX [descriptor]"
            - "Personal And Advt Injury": "$X,XXX,XXX [descriptor]"
            - "Medical expenses": "$X,XXX [descriptor]"
            - "Damage to rented premises": "$X,XXX [descriptor]"
            - "Each Occurrence": "$X,XXX,XXX [descriptor]"
            - "Deductible": "$X,XXX [descriptor]"
            - "Hired Or Non Owned Auto": "$X,XXX,XXX [descriptor]"
            - "Advance Premium": "$X,XXX"
            - "Additional Interest": "Name/details or null"
            - "Schedule of Hazards Rating Info": Array of objects with:
            * "Loc/BLDG No": "exact value"
            * "TERR": "exact value"
            * "Classification Code": "exact value"
            * "Coverage description": "exact value"
            * "Description": "exact value"
            * "Rating Basis": "exact value"
            * "Exposure": "exact value"
            * "Final Rate": "exact value"

            **13. Employee Benefits Liability**
            - Extract: ONLY from its declaration page
            - Format: Object with coverage details or null

            **14. Directors and Officers**
            - Extract: ONLY from its declaration page
            - Format: Object with coverage details or null

            **15. Cyber**
            - Extract: ONLY from Cyber declaration page
            - Format: Object with coverage details or null

            **16. Professional Liability**
            - Extract: ONLY from its declaration page
            - Format: Object with coverage details or null

            **17. EPLI on Policy**
            - Extract: ONLY from its declaration page
            - Format: Object with coverage details or null

            **18. Errors and Omissions on Policy**
            - Extract: Coverage details if present
            - Format: Object with details or null

            **19. Terrorism**
            - Extract: ONLY if present in premiums or "Schedule of Terrorism Act" page
            - Format: Object with details or null

            **20. Work Exclusion**
            - Status: ALWAYS return null (per scope rules)

            **21. Liability locations match property locations if applicable**
            - Status: ALWAYS return null (per scope rules)

            **22. Property**
            Extract ONLY from Property declaration page. 

            **IMPORTANT: For fields marked as ARRAY, must extract ALL occurrences with format mentioned and return as array of strings**

            - "Building Value": ARRAY - Extract ALL buildings
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $X,XXX,XXX - Cause Of Loss : [type] - Premium : $X,XXX.XX"
            * Example: ["Location Number : 0001 - Building Number : 001 - $4,722,000 - Cause Of Loss : Special Including Theft - Premium : $6,324.00"]

            - "Business Personal Property Limit": ARRAY - Extract ALL occurrences
            * Format per entry: "Location Number : XXXX - Occupancy Number : XXX - $XXX,XXX - Cause Of Loss : [type] - Premium : $X,XXX.XX"
            * Example: ["Location Number : 0001 - Occupancy Number : 001 - $472,200 - Cause Of Loss : Special Including Theft - Premium : $1,283.00"]

            - "Business Income Limit": ARRAY - Extract ALL occurrences
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $XXX,XXX - Cause Of Loss : [type] - Premium : $X,XXX.XX"

            - "Improvements and Betterments": ARRAY - Extract ALL occurrences
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $XXX,XXX - Cause Of Loss : [type] - Premium : $X,XXX.XX"

            - "Wind And Hail": ARRAY - Extract ALL occurrences
            * Format per entry: "Location Number : XXXX - Building Number : XXX - Building - Wind Or Hail Deductible : X%"
            * Example: ["Location Number : 0001 - Building Number : 001 - Building - Wind Or Hail Deductible : 2%"]

            - "Property Deductible": ARRAY - Extract ALL deductibles under this section
            * Format per entry: "Location Number : XXXX - Building Number : XXX - Building - $X,XXX"
            * Example: ["Location Number : 0001 - Building Number : 001 - Building - $5,000", "Location Number : 0002 - Building Number : 001 - Building - $7,500"]

            - "Co Insurance": ARRAY - Extract ALL occurrences with COMPLETE location and building identifiers
            * **CRITICAL**: DO NOT extract just "80%" - MUST include Co insurance of all locations and buildings with their numbers
            * Format per entry: "LOCATION : # X - BUILDING # X - Building : XX%"
            * Example: ["LOCATION : # 1 - BUILDING # 1 - Building : 80%", "LOCATION : # 2 - BUILDING # 1 - Building : 80%"]
            * If document uses "Location Number" format, use: "Location Number : XXXX - Building Number : XXX - Building - XX%"
            * Extract the ENTIRE row/line including all location identifiers, not just the percentage

            - "Valuation": ARRAY - Extract ALL occurrences with COMPLETE location and building identifiers
            * **CRITICAL**: DO NOT extract just "RC" or "Replacement Cost" - MUST include location and building numbers
            * Format per entry: "Location Number : XXXX - Building Number : XXX - Building - [valuation type]"
            * Example: ["Location Number : 0001 - Building Number : 001 - Building - Replacement Cost", "Location Number : 0002 - Building Number : 001 - Building - Actual Cash Value"]
            * If document uses "LOCATION : #" format, adapt accordingly
            * Extract the ENTIRE row/line including all location identifiers, not just the valuation type

            - "Is Equipment Breakdown Listed": "Yes" or "No" or null

            - "Building Ordinance Or Law Listed Cov A": ARRAY or null - Extract ALL if multiple
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $XXX,XXX" or just amount

            - "Building Ordinance Demolition Cost Cov B": ARRAY or null - Extract ALL if multiple
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $XXX,XXX" or just amount

            - "Building Ordinance Inc Cost Of Construction Cov C": ARRAY or null - Extract ALL if multiple
            * Format per entry: "Location Number : XXXX - Building Number : XXX - $XXX,XXX" or just amount

            **23. Property Terrorism**
            - Extract: Terrorism values within building property values under Property declarations
            - Format: Object or null

            **24. Inland Marine Details**
            - Extract: ONLY from Inland Marine declaration page
            - Format: Object with details or null

            **25. Equipment Schedule**
            - Extract: ONLY from Equipment Schedule section
            - Format: Array of equipment items or null

            **26. Deductibles**
            - Extract: ONLY from section labeled "Deductibles"
            - Do NOT extract deductibles from other sections
            - Format: Object with deductible types and amounts

            **27. Loss Payee**
            - Extract: Loss payee or mortgage information page only
            - Format: Array of names/addresses or null

            **28. Rental equipment from others**
            - Status: ALWAYS return null (per scope rules)

            **29. Rental equipment to others**
            - Status: ALWAYS return null (per scope rules)

            **30. Installation floater**
            - Extract: Coverage details if present
            - Format: Object or null

            **31. Inland Marine Terrorism**
            - Extract: Terrorism section under Inland Marine page only
            - Format: Object or null

            **32. Umbrella Limits**
            - Extract: Limits from Umbrella coverages section
            - Format: Object with limit types and amounts

            **33. Underlying Policies**
            - Extract: ONLY from "Underlying Policies" section
            - Return COMPLETE details as shown
            - Format: Array of policy objects with all fields

            **34. Policy Exclusions**
            - Status: ALWAYS return null (per scope rules)

            **35. Additional Coverage(s)**
            - Extract: Coverage names and values
            - Format: Object with coverage names as keys, values as amounts

            **36. Forms And Endorsements**
            - Extract: ONLY from "Forms And Endorsements" section
            - Scan to END of document
            - Merge multi-line entries into single entry
            - Format EXACTLY: "FormNumber | MM/YY   Form Title"
            - If coverage code exists: "BOP BP0159 | 08/08  WATER EXCLUSION ENDORSEMENT"
            - Return: Single array of ALL forms (deduplicate exact duplicates only)

            **37. Endorsements**
            - Extract: ONLY from endorsement declaration page
            - Include: Description of changes (changed, added, deleted, estimated total premium, paid in full discount)
            - Format: Object with change details

            ### FINAL INSTRUCTIONS
            - Return ONLY valid JSON - no explanations, no markdown code blocks, no preamble
            - All dates: MM/DD/YYYY format
            - All currency: Keep $ symbol and commas
            - Missing data: null
            - Empty arrays: null (not [])
            - When in doubt: Extract exactly as written, no assumptions

            {f'Text: {large_text}' if large_text else ''}
            """
