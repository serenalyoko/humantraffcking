

import json
import os

import pandas as pd
import re


us_states = {
    "Connecticut": ["康涅狄格州", "康州", "康涅狄格", "Коннектикут", "КТ"],
    "Delaware": [ "特拉华州", "特州", "特拉华", "Делавэр", "ДЕ"],
    "Florida": [
        "FL", "佛罗里达州", "佛州", "佛罗里达", "Флорида", "ФЛ",
        "迈阿密", "奥兰多", "坦帕", "劳德代尔堡", "棕榈滩",
        # added from unknown list
        "Wesley chapel", "wesley chapel",
        "博卡",  # Boca Raton
        "St.cloud City", "st.cloud city",
        "gulf breeze santa rosa"
    ],
    "Georgia": [
         "佐治亚州", "佐州", "佐治亚", "乔治亚","Джорджия", "ДЖ", "亚市", "亚特兰大", "Marietta", 
        # added from unknown list
        "Augusta", "augusta"
    ],
    "Hawaii": [ "夏威夷州", "夏州", "夏威夷", "Гавайи", "ГВ", "檀香山"],
    "Idaho": ["爱达荷州", "爱州", "爱达荷", "Айдахо", "АЙ"],
    "Illinois": ["伊利诺伊州", "伊州", "伊利诺伊", "Иллинойс", "ИЛ", "芝加哥"],
    "Indiana": [ "印第安纳州", "印州", "印第安纳", "Индиана", "ИН"],
    "Iowa": [ "爱荷华州", "华州", "爱荷华", "Айова", "АЙ"],
    "Kansas": [ "堪萨斯州", "堪州", "堪萨斯", "Канзас"],
    "Kentucky": [ "肯塔基州", "肯州", "肯塔基", "Кентукки"],
    "Louisiana": ["路易斯安那州", "路州", "路易斯安那", "路易斯安娜","Луизиана", "ЛА"],
    "Maine": [ "缅因州", "缅州", "缅因", "Мэн"],
    "Maryland": [
        "MD", "马里兰州", "马州", "马里兰", "Мэриленд", "МД", "巴尔的摩","贝塞斯达", "罗克维尔",
        # added from unknown list
        "馬州 銀泉",
        "Ｒｏｃｋｖｉｌｌｅ Ｒｏｃｋｖｉｌｌｅ Ｍａｒｙｌａｎｄ"
    ],
    "Massachusetts": [
         "马萨诸塞州", "麻州", "马萨诸塞", "Массачусетс",  "波士顿",
        # added from unknown list
        "Boston", "boston"
    ],
    "Michigan": ["密歇根州", "密州", "密歇根", "Мичиган", "МИ"],
    "Minnesota": ["MN", "明尼苏达州", "明州", "明尼苏达", "Миннесота", "МН", "明里苏达"],
    "Mississippi": ["MS", "密西西比州", "西州", "密西西比", "Миссисипи", "МС"],
    "Missouri": [ "密苏里州", "苏州", "密苏里", "Миссури", "МО"],
    "Montana": ["MT", "蒙大拿州", "蒙州", "蒙大拿", "Монтана", "МТ"],
    "Nebraska": ["内布拉斯加州", "内州", "内布拉斯加", "Небраска", ],
    "Nevada": [
        "NV", "内华达州", "华达州", "内华达", "Невада",
        "拉斯维加斯","拉斯","拉丝维加斯", "维加斯", "LASVEGAS",
        # added from unknown list
        "Reno", "reno", "Reno."
    ],
    "California": [
        "CA", "加利福尼亚州", "加州", "加利福尼亚", "灣區","Калифорния", "КА",
        "SF", "日落","S F","santa cruz","红木","舊金山市","Los Angeles","工业市",
        "Anaheim","San Diego", "Santa Anita","罗兰岗", "河滨县", "旧金山", "安大略",
        "FONTANA", "圣盖博", "洛杉矶", "尔湾", "天普", "Fullerton", "阿罕布拉", "奥克兰",
        "湾区","圣何塞", "圣地亚哥", "萨克拉门托", "长滩", "帕萨迪纳", "卡尔斯巴德",
        "卡尔斯巴多", "卡尔斯巴", "圣芭芭拉", "圣芭芭拉市", "钻石吧", "三藩",
        "San Jose", "Redwood", "Fairfield", "Tiburon", "Union City", "北湾", "南湾",
        "硅谷","东湾", "sunset", "Fostercity", "三番", "辛利", "San Bruno", "berkeley",
        "Brentwood", "SAN GABRIEL",
        # added from unknown list
        "Stockton", "stockton", "Pleasanton", "pleasanton", "Pleasanto",
        "Fresno", "fresno", "半月湾", "Half Moon Bay",
        "伯克利", "柏克莱", "蒙特利公园", "圣克拉拉",
        "三谷", "中半岛", "半岛区",
        "Atherton", "Hercules", "Davis",
        "foster city", "east bay", "East bay"
    ],
    "New Hampshire": ["NH", "新罕布什尔州", "新罕州", "新罕布什尔", "Нью-Гэмпшир", "НХ"],
    "New Jersey": [
        "NJ", "新泽西州", "新州", "泽西市","新泽西", "jersey city","Нью-Джерси", "НД",
        # added from unknown list
        "Englewood Cliffs", "englewood cliffs",
        "East Hanover", "East Hanover East Hanover",
        "Edison", "edison"
    ],
    "New Mexico": ["NM", "新墨西哥州", "墨州", "新墨西哥", "Нью-Мексико", "НМ"],
    "New York": [
        "NY", "纽约州", "Queens","纽约州", "纽约", "Ｎｙ","洛克菲勒中心", "八大道附近",
        "紐約", "長島","BRONX","Нью-Йорк", "N Y","НЙ", "曼哈顿", "法拉盛","长岛",
        "布鲁克林", "皇后区", "法盛", "曼克顿", "上州", "雪城", "布鲁", "史丹顿岛", "皇后",
        # added from unknown list
        "elmhurst", "Elmhurst", "Elmhurst MY",
        "Woodhaven", "woodhaven",
        "Hempstead", "hempstead",
        "Islip", "islip",
        "BK", "Ｂｋ", "Ｂｋ Ｂｋ",
        "發拉盛",    # alt for Flushing
        "新鲜草原",  # Fresh Meadows
        "大学点",    # College Point
        "小頸區",    # Little Neck
        "8大道"
    ],
    "North Carolina": [
        "NC", "北卡罗来纳州", "北卡", "北卡罗来纳", "Северная Каролина", "СК", "夏洛特",
        # added from unknown list
        "Durham", "durham",
        "Duke university",
        "Durham Duke university"
    ],
    "North Dakota": ["ND", "北达科他州", "北达州", "北达科他", "Северная Дакота", "НД"],
    "Ohio": ["俄亥俄州", "俄州", "俄亥俄", "Огайо", "ОХ"],
    "Oklahoma": [ "俄克拉荷马州", "俄克州", "俄克拉荷马", "Оклахома"],
    "Oregon": [
         "俄勒冈州", "俄勒州", "泼特兰","俄勒冈", "波特兰","Beaverton", "泼特兰","Орегон", "ОР"
    ],
    "Pennsylvania": [
         "宾夕法尼亚州", "宾州", "宾夕法尼亚", "宾洲","Pittsburg","Пенсильвания", "ПА","滨州","费城", "匹兹堡"
    ],
    "Rhode Island": [ "罗得岛州", "罗州", "罗德岛","罗得岛", "Род-Айленд", "РИ"],
    "South Carolina": ["SC", "南卡罗来纳州", "南卡", "南卡罗来纳", "Южная Каролина", "СК"],
    "South Dakota": ["SD", "南达科他州", "南达州", "南达科他", "Южная Дакота", "СД"],
    "Tennessee": ["TN", "田纳西州", "田州", "田纳西", "Теннесси", "ТН"],
    "Texas": [
        "TX", "得克萨斯州", "德州", "得克萨斯", "Техас", "ТХ", "休斯顿", "达拉斯",
        "奥斯汀", "圣安东尼奥", "沃斯堡", "奥斯丁","休斯敦"
    ],
    "Utah": [ "犹他州", "犹州", "犹他", "Юта", "ЮТ"],
    "Vermont": ["VT", "佛蒙特州", "佛蒙州", "佛蒙特", "Вермонт", "ВТ"],
    "Virginia": [
        "VA", "弗吉尼亚州", "弗州", "弗吉尼亚", "Виргиния", "ВА", "维州", "维吉尼亚", "北维"
    ],
    "Washington": [
         "华盛顿州", "华州", "华盛顿", "西亚图","Вашингтон", "ВАШ", "西雅图",
        "Bellevue", "seattle",
        # added from unknown list
        "Everett", "everett",
        "Kent", "kent",
        "Lynnwood", "lynnwood",
        "Renton", "renton",
        "Bothell", "bothell",
        "塔科马"
    ],

    "West Virginia": [ "西弗吉尼亚州", "西弗州", "西弗吉尼亚", "Западная Виргиния", "ЗВ"],

    "Wisconsin": [ "威斯康星州", "威州", "威斯康星", "Висконсин", "ВС"],
    "Wyoming": ["WY", "怀俄明州", "怀州", "怀俄明", "Вайоминг", "ВЙ"],
    "DC": ["华盛顿特区", "哥伦比亚特区", "华盛顿区", "Вашингтонский округ", "WD" , "DC", "Dc", "dc", "大华"],
    "Colorado": [ "科罗拉多州", "科州", "科罗拉多", "Колорадо", "КО"],
    "Alabama": [ "阿拉巴马州", "阿州", "阿拉巴马", "Алабама", "АЛ"],
    "Alaska": [ "阿拉斯加州", "阿拉州", "阿拉斯加", "Аляска"],
    "Arizona": ["亚利桑那州", "亚利州", "亚利桑那", "Аризона", "АЗ"],
    "Arkansas": ["阿肯色州", "阿肯州", "阿肯色", "Арканзас", "АР"],

}






job_types = {
    "Marketing/Sales": [
        "Marketing", "销售", "Sales/Insurance/Finance", "销售人员地点",
        "🍻 市场销售", "Exhibition/Trade show"
    ],

    "Modeling/Entertainment": [
        "Modeling", "Performer/Entertainer", "Dancing"
    ],

    "Clerical/Office/Admin": [
        "文职人员", "文员", "办公室文员", "Admin/Office",
        "Clerical", "Assistant", "Receptionist",
        "🍻 助理文员"
    ],

    "Customer Service": [
        "Customer Service", "Server", "餐厅", "Restaurant service",
        "🍻 门店店员"
    ],

    "Arts/Music/Media": [
        "Arts/Music/Media"
    ],

    "Translation/Tourism": [
        "翻译", "Translator", "翻译/导游", "Tour Guide",
        "Real estate/Tourism"
    ],

    "Driver/Logistics": [
        "Driver", "司机", "🍻 各类司机", "Driving/Logistics",
        "Auto repair", "物流", "仓库物流", "🍻 仓库物流"
    ],

    "Massage/Wellness/Therapy": [
        "Massage", "massage","按摩师", "按摩推拿针灸",
        "🍻 按摩SPA", "🍻 按摩转让", "按摩",
        "Salon/Spa", "🍻 美甲美型"
    ],

    "Homecare/Nanny/Housekeeping": [
        "保姆/家政", "保姆／家政", "保姆/家教",
        "Nanny", "Housekeeping", "保洁清洗保姆",
        "🍻 家政保姆"
    ],

    "Construction/Skilled Trades": [
        "Construction/Renovation", "装修/建筑/装潢",
        "技工/装修工", "Construction/Skilled Trades",
        "Carpentry", "🍻 工地装修"
    ],

    "Warehouse/Factory/Manufacturing": [
        "Warehouse", "仓库",
        "Factory/Manufacturing", "Factory/Production",
        "Factory", "Sewing/Furniture", "工厂"
    ],

    "Healthcare/Clinic": [
        "Healthcare", "Clinic", "Egg Donor"
    ],

    "IT/Programming/Tech": [
        "IT/Programming", "电脑相关", "Technician/Engineer",
        "Analyst", "Operations"
    ],

    "Research/Education": [
        "Research/Study", "Education", "Tutor"
    ],

    "Security/Law Enforcement": [
        "Security", "Security/Law Enforcement"
    ],

    "E-commerce": [
        "E-commerce"
    ],

    "Buyer/Procurement": [
        "Buyer/procurement"
    ],

    "Real Estate": [
        "Real Estate"
    ],

    "Pet/Animal Care": [
        "Pet/Animal Care"
    ],

    "Hospitality": [
        "餐饮", "🍻 餐饮工作", "餐厅"
    ],

    "Escort/Sex Work": [
        "Escort"
    ],

    "Government/Military": [
        "Military", "Government job"
    ],

    "Other/Uncategorized": [
        "Other", "生意转让", "[求职招聘]", "[北美租房]"
    ]
}

def group_job_type(job_type_value):
    for general_type, variants in job_types.items():
        if job_type_value in variants:
            return general_type
    return "Other/Uncategorized"

def rewrite_location(location):
    new_loc = location
    updated = False
    states = [state.lower() for state in us_states.keys()]
    if location.lower() in states:
        return location

    for state, variants in us_states.items():
        all_variants = [state] + variants
        for variant in all_variants:
            if variant.lower() in location.lower():
                new_loc = state
                updated = True
                return state
    #if not updated:
    #    print("Unknown location:", location)
    return new_loc


def extract_phone_numbers(text):
    phone_pattern = re.compile(
        r'(\+?\d{1,3}[\s\-\.]?)?(\(?\d{3}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}|\d{3}[\s\-\.]?\d{4}'
    ) 
    if "电话" in text:
        lines = text.split("\n")
        for line in lines:
            if "电话" in line:
                line = line.replace(" ", "")
                phone_match = re.search(r'(\+?\d{1,3}[\s\-\.]?)?(\(?\d{3}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}|\d{3}[\s\-\.]?\d{4}', line)
                #if phone_match:
                    #print("Extracted phone:", phone_match.group())
                
        return True, [phone_match.group()] if phone_match else []
 # Exclude patterns like "6000-8000" or "1000-2000" (salary ranges)
    salary_pattern = re.compile(r'\b\d{3,5}\s*-\s*\d{3,5}\b')
    matches = phone_pattern.findall(text)
    # If matches are tuples, join them into strings
    filtered = []
    for m in matches:
        if isinstance(m, tuple):
            m_str = ''.join(m)
        else:
            m_str = m
        if m_str and not salary_pattern.search(m_str):
            filtered.append(m_str)
    #print(text, filtered)
    return bool(filtered), filtered

def extract_emails(text):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    return bool(email_pattern.search(text))

def get_contact_options(has_phone, has_email, text):
    method = "Other"
    if has_phone and has_email:
        method = "both"
    elif has_phone:
        has_email = extract_emails(text)
        if not has_email:
            method = "phone"
        else:
            method = "both"
    elif has_email:
        has_phone = extract_phone_numbers(text)
        if not has_phone:
            method = "email"
        else:
            method = "both"

    return method
    
if __name__ == "__main__":
    path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_2.1.csv"
    df = pd.read_csv(path)
    df = df[~df["job_description"].isna() & (df["job_description"].str.strip() != "")]
    locations = df["location"].tolist()
    jd = df["job_description"].tolist()
    job_type = df["job type"].tolist()
    contact_method = df["contact method"].tolist()
    print(set(job_type))
    count_missing = 0
    count_unknown = 0
    all = 0
    

    phone_numbers = []
    for i in range(len(locations)):
        # Determine contact method type
        method = ""
        has_phone = False
        has_email = False
        numbers = []
        # Simple phone pattern: 10+ digits, possibly with spaces, dashes, parentheses
        phone_pattern = re.compile(r'(\+?\d[\d\-\(\) ]{8,}\d)')
        if isinstance(contact_method[i], str):
            if "@" in contact_method[i]:
                has_email = True
            if phone_pattern.search(contact_method[i]):
                has_phone = True
                numbers = phone_pattern.findall(contact_method[i])

        if has_email or has_phone:
            method = get_contact_options(has_phone, has_email, jd[i])
        else:
            has_phone,number = extract_phone_numbers(jd[i])
            for n in number:
                numbers.append(n)
            has_email = extract_emails(jd[i])
            method = get_contact_options(has_phone, has_email, jd[i])
        # Convert numbers list to a JSON-compatible string
        if numbers:
            phone_numbers.append(json.dumps(numbers, ensure_ascii=False))
        else:
            phone_numbers.append("[]")


        contact_method[i] = method 
        #if pd.isna(jd[i]) or jd[i].strip() == "":
        #    continue
        #all += 1
        grouped_type = group_job_type(str(job_type[i]))
        job_type[i] = grouped_type
        if pd.isna(locations[i]) or locations[i].strip() == "" or "other" in str(locations[i]).lower()  or "其他" in str(locations[i]):
            locations[i] = "Not specified"
        else:
            locations[i] = rewrite_location(str(locations[i]))
        

    df["location"] = locations
    df["job type"] = job_type
    df["contact method"] = contact_method
    df["extracted phone numbers"] = phone_numbers
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_3.0.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
        #if pd.isna(locations[i]) or locations[i].strip() == "" or "other" in locations[i].lower()  or "其他" in locations[i]:
        #    description = jd[i].replace("联系时请一定说明是在洛杉矶华人资讯网看到的，谢谢！", "").replace("联系时请一定说明是在西雅图华人资讯网看到的，谢谢", "").replace("联系时请一定说明是在大华府华人资讯网看到的，谢谢", "")
        #    state = get_state(description)
        #    if state != "":
        #        locations[i] = state
            #if state == "":
                #with open("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/missing_states.txt", "a", encoding="utf-8") as f:
                #    f.write(description + "\n")
                #count_missing += 1
        #    locations[i] = state