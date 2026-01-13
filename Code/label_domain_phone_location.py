import pandas as pd
import json
import os

def get_state_from_area_code(phone_number, area_code_map, domain_location):
    no_country_code = phone_number.replace("+1", "").replace("1(", "").replace("1 (", "")
    number = ''.join(filter(str.isdigit, no_country_code))
    if len(number) < 3:
        return "Unknown"
    if len(number) == 7:
        return domain_location
    area_code = number[:3]
    return area_code_map.get(area_code, "Unknown")

abbrev_to_state = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California", 
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "DC" 
      }
if __name__ == "__main__":
    input_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_with_original_labels.csv"
    area_code = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/USA_Telephone_Area_Codes.csv"
    df = pd.read_csv(input_path, low_memory=False)
    area_code_dict = pd.read_csv(area_code)
    area_code = area_code_dict["Telephone Area Code "].tolist()
    state_abbreviation = area_code_dict["State Abbreviation"].tolist()
    area_code_map = {}
    for i in range(len(area_code)):
        area_code_map[str(area_code[i])] = state_abbreviation[i]

    domain_location = df["domain location"].tolist()
    for i in range(len(domain_location)):
        loc = domain_location[i]
        if loc == "vegas":
            domain_location[i] = "Nevada"
        elif loc == "la":
            domain_location[i] = "California"
        elif loc == "ny":
            domain_location[i] = "New York"
        elif loc == "pa":
            domain_location[i] = "Pennsylvania"
        elif loc == "sf":
            domain_location[i] = "California"
        elif loc == "dc":
            domain_location[i] = "DC"
        elif loc == "chicago":
            domain_location[i] = "Illinois"
        elif loc == "seattle":
            domain_location[i] = "Washington"
        elif loc == "atlanta":
            domain_location[i] = "Georgia"
        elif loc == "florida":
            domain_location[i] = "Florida"
        elif loc == "houston":
            domain_location[i] = "Texas"
    df["domain location"] = domain_location
    phone_numbers = df["extracted phone numbers"].tolist()
    phone_location = []
    for i in range(len(phone_numbers)):
        location = get_state_from_area_code(phone_numbers[i], area_code_map, domain_location[i])
        state = abbrev_to_state[location] if location in abbrev_to_state else location
        phone_location.append(state)
    df["phone location"] = phone_location
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_5.0.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')