

import json
import os

import pandas as pd


us_states = {
    "Connecticut": [
        "康涅狄格州", "康州", "康涅狄格",
        "Коннектикут", "Коннектикута", "Коннектикуте", "Коннектикута",
        "КТ", "CT",
        "Стэмфорд", "Стэмфорда", "Стэмфорде", "Стэмфорда",
        "Гринвич", "Гринвича", "Гринвиче", "Гринвича",
        "Норуок", "Норуока", "Норуоке", "Норуока",
        "Бриджпорт", "Бриджпорта", "Бриджпорте", "Бриджпорта",
        "Данбери", "Данбери", "Данбери",
        "Хартфорд", "Хартфорда", "Хартфорде", "Хартфорда",
        "Уэст-Хартфорд", "Уэст-Хартфорда", "Уэст-Хартфорде", "Уэст-Хартфорда",
        "Ист-Хартфорд", "Ист-Хартфорда", "Ист-Хартфорде", "Ист-Хартфорда",
        "Нью-Бритен", "Нью-Бритена", "Нью-Бритене", "Нью-Бритена",
        "Миддлтаун", "Миддлтауна", "Миддлтауне", "Миддлтауна",
        "Нью-Лондон", "Нью-Лондона", "Нью-Лондоне", "Нью-Лондона",
        "Норидж", "Нориджа", "Норидже", "Нориджа",
        "Личфилд", "Личфилда", "Личфилде", "Личфилда"
    ],
    "Delaware": [ 
        "特拉华州", "特州", "特拉华", "Делавэр", "ДЕ",
        "Делавэра", "Делавэре", "Делавэра",
        "Уилмингтон", "Уилмингтона", "Уилмингтоне", "Уилмингтона",
        "Довер", "Довера", "Довере", "Довера",
        "Ньюарк", "Ньюарка", "Ньюарке", "Ньюарка",
        "Миддлтаун", "Миддлтауна", "Миддлтауне", "Миддлтауна",
        "Смирна", "Смирны", "Смирне", "Смирны",
        "Бэр", "Бэре", "Бэра",
        "Рехобот-Бич", "Рехобот-Бича", "Рехобот-Биче", "Рехобот-Бича",
        "Льюис", "Льюиса", "Льюисе", "Льюиса",
        "округ Нью-Касл", "округа Нью-Касл", "в округе Нью-Касл",
        "округ Кент", "округа Кент", "в округе Кент",
        "округ Сассекс", "округа Сассекс", "в округе Сассекс",
        "север Делавэра", "юг Делавэра", "прибрежный Делавэр", "побережье Делавэра"
    ],
    "Florida": [
        "FL", "佛罗里达州", "佛州", "佛罗里达", "Флорида", "ФЛ",
        "迈阿密", "奥兰多", "坦帕", "劳德代尔堡", "棕榈滩",
        "Wesley chapel", "wesley chapel",
        "博卡",  
        "St.cloud City", "st.cloud city",
        "gulf breeze santa rosa",
        "Флориды", "Флориде", "Флориду", "ФЛ", "Майами", "Орландо", 
        "Тампа", "Тампы", "Тампе", "Тампу",
        "Форт-Лодердейл", "Форт-Лодердейла", "Форт-Лодердейле",
        "Палм-Бич", "Палм-Бича", "Палм-Биче",
        "Бока-Ратон", "Бока-Ратона", "Бока-Ратоне",
        "Wesley chapel", "wesley chapel", "Уэсли-Чапел", "Уэсли-Чапела", "Уэсли-Чапеле",
        "Сент-Клауд", "Сент-Клауда", "Сент-Клауде",
        "Галф-Бриз", "Галф-Бриза", "Галф-Бризе", "Побережье Мексиканского залива"
    ],
    "Georgia": [
        "佐治亚州", "佐州", "佐治亚", "乔治亚","Джорджия", "ДЖ", "亚市", "亚特兰大", "Marietta", 
        "Augusta", "augusta", "Атланта", "Атланты", "Атланте",
        "Marietta", "marietta", "Мариетта", "Мариетты", "Мариетте",
        "Augusta", "augusta", "Огаста", "Огасты", "Огасте", "Джорджии", "Джорджии", "Джорджию"
    ],
    "Hawaii": [
        "夏威夷州", "夏州", "夏威夷", "Гавайи", "ГВ", "檀香山",
        "Гавайев", "на Гавайях", "Гонолулу", "Гонолулу", "Оаху", "Мауи", "Кауаи", "Большой остров",
        "Тихоокеанские острова", "Гавайские острова"
    ],
    "Idaho": [
        "爱达荷州", "爱州", "爱达荷", "Айдахо", "АЙ", "Boise", "boise", "Бойсе",
        "Idaho Falls", "idaho falls", "Айдахо-Фолс", "Айдахо-Фолса"
    ],
    "Illinois": [
        "伊利诺伊州", "伊州", "伊利诺伊", "Иллинойс", "ИЛ", "芝加哥",
        "Чикаго", "Иллинойса", "Иллинойсе",
        "Aurora", "aurora", "Орора", "Ороры", "Ороре",
        "Rockford", "rockford", "Рокфорд", "Рокфорда", "Рокфорде",
        "Joliet", "joliet", "Джолиет", "Джолиета", "Джолиете",
        "Naperville", "naperville", "Нейпервилл", "Нейпервилла", "Нейпервилле",
        "Springfield", "springfield", "Спрингфилд", "Спрингфилда", "Спрингфилде",
        "Peoria", "peoria", "Пеория", "Пеории", "Пеории",
        "Evanston", "evanston", "Эванстон", "Эванстона", "Эванстоне",
        "Champaign", "champaign", "Шампейн", "Шампейна", "Шампейне",
        "Bloomington", "bloomington", "Блумингтон", "Блумингтона", "Блумингтоне"
    ],
    "Indiana": [
        "印第安纳州", "印州", "印第安纳", "Индиана", "ИН",
        "Индианы", "Индиане",
        "Indianapolis", "indianapolis", "Индианаполис", "Индианаполиса", "Индианаполисе",
        "Fort Wayne", "fort wayne", "Форт-Уэйн", "Форт-Уэйна", "Форт-Уэйне",
        "Evansville", "evansville", "Эвансвилл", "Эвансвилла", "Эвансвилле",
        "South Bend", "south bend", "Саут-Бенд", "Саут-Бенда", "Саут-Бенде"
    ],
    "Iowa": [
        "爱荷华州", "华州", "爱荷华", "Айова", "АЙ",
        "Айовы", "Айове",
        "Des Moines", "des moines", "Де-Мойн", "Де-Мойна", "Де-Мойне",
        "Cedar Rapids", "cedar rapids", "Сидар-Рапидс", "Сидар-Рапидса", "Сидар-Рапидсе",
        "Davenport", "davenport", "Давенпорт", "Давенпорта", "Давенпорте",
        "Iowa City", "iowa city", "Айова-Сити", "Айова-Сити"
    ],
    "Kansas": [
        "堪萨斯州", "堪州", "堪萨斯", "Канзас",
        "Канзаса", "Канзасе",
        "Wichita", "wichita", "Уичито", "Уичито",
        "Overland Park", "overland park", "Оверленд-Парк", "Оверленд-Парка", "Оверленд-Парке",
        "Kansas City", "kansas city", "Канзас-Сити", "Канзас-Сити",
        "Topeka", "topeka", "Топика", "Топики", "Топике",
        "Lawrence", "lawrence", "Лоуренс", "Лоуренса", "Лоуренсе"
    ],
    "Kentucky": [
        "肯塔基州", "肯州", "肯塔基", "Кентукки",
        "Louisville", "louisville", "Луисвилл", "Луисвилла", "Луисвилле",
        "Lexington", "lexington", "Лексингтон", "Лексингтона", "Лексингтоне",
        "Bowling Green", "bowling green", "Боулинг-Грин", "Боулинг-Грина", "Боулинг-Грине",
        "Owensboro", "owensboro", "Оуэнсборо", "Оуэнсборо"
    ],
    "Louisiana": [
        "路易斯安那州", "路州", "路易斯安那", "路易斯安娜","Луизиана", "ЛА",
        "New Orleans", "new orleans", "Новый Орлеан", "Нового Орлеана", "Новом Орлеане",
        "Baton Rouge", "baton rouge", "Батон-Руж", "Батон-Ружа", "Батон-Руже",
        "Shreveport", "shreveport", "Шривпорт", "Шривпорта", "Шривпорте",
        "Lafayette", "lafayette", "Лафайет", "Лафайета", "Лафайете",
        "Lake Charles", "lake charles", "Лейк-Чарльз", "Лейк-Чарльза", "Лейк-Чарльзе"
    ],
    "Maine": [
        "缅因州", "缅州", "缅因", "Мэн", "Мэна", "Мэне",
        "Lewiston", "lewiston", "Льюистон", "Льюистона", "Льюистоне",
        "Bangor", "bangor", "Бангор", "Бангора", "Бангоре",
        "Augusta", "augusta", "Огаста", "Огасты", "Огасте"
    ],
    "Maryland": [
        "MD", "马里兰州", "马州", "马里兰", "Мэриленд", "МД", "巴尔的摩","贝塞斯达", "罗克维尔",
        "馬州 銀泉",
        "Ｒｏｃｋｖｉｌｌｅ Ｒｏｃｋｖｉｌｌｅ Ｍａｒｙｌａｎｄ",
        "Мэриленда", "Мэриленде",
        "Baltimore", "baltimore", "Балтимор", "Балтимора", "Балтиморе",
        "Bethesda", "bethesda", "Бетесда", "Бетесды", "Бетесде",
        "Rockville", "rockville", "Роквилл", "Роквилла", "Роквилле",
        "Silver Spring", "silver spring", "Силвер-Спринг", "Силвер-Спринга", "Силвер-Спринге",
        "Gaithersburg", "gaithersburg", "Гейтерсберг", "Гейтерсберга", "Гейтерсберге",
        "Annapolis", "annapolis", "Аннаполис", "Аннаполиса", "Аннаполисе",
        "Eastern Shore", "Восточный берег",
        "Metro DC", "Вашингтонская агломерация"
    ],
    "Massachusetts": [
        "马萨诸塞州", "麻州", "马萨诸塞", "Массачусетс",  "波士顿",
        "Boston", "boston",
        "Массачусетса", "Массачусетсе",
        "Бостон", "Бостона", "Бостоне",
        "Cambridge", "cambridge", "Кембридж", "Кембриджа", "Кембридже",
        "Worcester", "worcester", "Вустер", "Вустера", "Вустере",
        "Springfield", "springfield", "Спрингфилд", "Спрингфилда", "Спрингфилде",
        "Lowell", "lowell", "Лоуэлл", "Лоуэлла", "Лоуэлле",
        "Newton", "newton", "Ньютон", "Ньютона", "Ньютоне",
        "Cape Cod", "Кейп-Код"
    ],
    "Michigan": [
        "密歇根州", "密州", "密歇根", "Мичиган", "МИ", "Мичигана", "Мичигане",
        "Detroit", "detroit", "Детройт", "Детройта", "Детройте",
        "Grand Rapids", "grand rapids", "Гранд-Рапидс", "Гранд-Рапидса", "Гранд-Рапидсе",
        "Ann Arbor", "ann arbor", "Анн-Арбор", "Анн-Арбора", "Анн-Арборе",
        "Lansing", "lansing", "Лансинг", "Лансинга", "Лансинге",
        "Flint", "flint", "Флинт", "Флинта", "Флинте",
        "Kalamazoo", "kalamazoo", "Каламазу", "Каламазу",
        "Агломерация Детройта"
    ],
    "Minnesota": [
        "MN", "明尼苏达州", "明州", "明尼苏达", "Миннесота", "МН", "明里苏达",
        "Миннесоты", "Миннесоте",
        "Minneapolis", "minneapolis", "Миннеаполис", "Миннеаполиса", "Миннеаполисе",
        "Saint Paul", "st paul", "Сент-Пол", "Сент-Пола", "Сент-Поле",
        "Rochester", "rochester", "Рочестер", "Рочестера", "Рочестере",
        "Duluth", "duluth", "Дулут", "Дулута", "Дулуте",
        "Twin Cities", "Города-побратимы"
    ],
    "Mississippi": [
        "MS", "密西西比州", "西州", "密西西比", "Миссисипи", "МС",
        "Jackson", "jackson", "Джексон", "Джексона", "Джексоне",
        "Gulfport", "gulfport", "Галфпорт", "Галфпорта", "Галфпорте",
        "Biloxi", "biloxi", "Билокси", "Билокси",
        "Hattiesburg", "hattiesburg", "Хаттисберг", "Хаттисберга", "Хаттисберге",
        "Southaven", "southaven", "Саутхейвен", "Саутхейвена", "Саутхейвене",
        "Mississippi Delta", "Дельта Миссисипи",
        "Gulf Coast", "Побережье Мексиканского залива"
    ],
    "Missouri": [
        "密苏里州", "苏州", "密苏里", "Миссури", "МО",
        "St. Louis", "st louis", "Сент-Луис", "Сент-Луиса", "Сент-Луисе",
        "Columbia", "columbia", "Колумбия", "Колумбии", "Колумбии",
        "Springfield", "springfield", "Спрингфилд", "Спрингфилда", "Спрингфилде",
        "Independence", "independence", "Индепенденс", "Индепенденса", "Индепенденсе",
        "Ozarks", "Озарк"
    ],
    "Montana": [
        "MT", "蒙大拿州", "蒙州", "蒙大拿", "Монтана", "МТ",
        "Монтаны", "Монтане",
        "Billings", "billings", "Биллингс", "Биллингса", "Биллингсе",
        "Missoula", "missoula", "Миссула", "Миссулы", "Миссуле",
        "Bozeman", "bozeman", "Боузман", "Боузмана", "Боузмане",
        "Great Falls", "great falls", "Грейт-Фолс", "Грейт-Фолса", "Грейт-Фолсе",
        "Helena", "helena", "Хелена", "Хелены", "Хелене"
    ],
    "Nebraska": [
        "内布拉斯加州", "内州", "内布拉斯加", "Небраска",
        "Небраски", "Небраске",
        "Omaha", "omaha", "Омаха", "Омахи", "Омахе",
        "Lincoln", "lincoln", "Линкольн", "Линкольна", "Линкольне",
        "Bellevue", "bellevue", "Белвью", "Белвью",
        "Grand Island", "grand island", "Гранд-Айленд", "Гранд-Айленда", "Гранд-Айленде",
        "Kearney", "kearney", "Кирни", "Кирни"
    ],
    "Nevada": [
        "NV", "内华达州", "华达州", "内华达", "Невада",
        "拉斯维加斯","拉斯","拉丝维加斯", "维加斯", "LASVEGAS",
        "Reno", "reno", "Reno.",
        "Las Vegas", "las vegas", "LASVEGAS", "Лас-Вегас", "Лас-Вегаса", "Лас-Вегасе",
        "Рино", "Рино",
        "Henderson", "henderson", "Хендерсон", "Хендерсона", "Хендерсоне",
        "North Las Vegas", "north las vegas", "Норт-Лас-Вегас", "Норт-Лас-Вегаса", "Норт-Лас-Вегасе",
        "Sparks", "sparks", "Спаркс", "Спаркса", "Спарксе",
        "Carson City", "carson city", "Карсон-Сити", "Карсон-Сити"
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
        "Stockton", "stockton", "Pleasanton", "pleasanton", "Pleasanto",
        "Fresno", "fresno", "半月湾", "Half Moon Bay",
        "伯克利", "柏克莱", "蒙特利公园", "圣克拉拉",
        "三谷", "中半岛", "半岛区",
        "Atherton", "Hercules", "Davis",
        "foster city", "east bay", "East bay", 
        "округа Сонома", "Sonoma Water", "Северной Калифорнии", "округ Сонома", "округе Сонома", 
        "Сонома", "Bay Area", " Tri-city/Tri-valley", "районе Tri-City", "Sonoma Water", "Фремонт", 
        "Сан-Франциско", "Калифорнии", "Модесто", "Плезантон", "Аламо", "Ист-Бэй", "Санта-Клара", 
        "Сан-Хосе", "Западном Окленде", "Окленде", "Окленд", "San Francisco", "Сент-Хелене", "Сент-Хелен", 
        "Сент-Хелена", "Санта-Розе", "Санта-Роза", "Алькатрас", "Ричмонде", "Ричмонд", "Пало-Альто",
        "Geary Blvd", "Geary", "Фэрфилде", "Фэрфилд", "Уолнат-Крик", "Маршалл", "САНТА-РОЗА", 
        "Маунтин-Вью", "КАЛИФОРНИИ", "Fremont", "Купертино", "Сан-Рафаэле", "Сан-Рафаэль", "Окленда",
        "Беркли", "Колледж-авеню", "Портола-Вэлли", "Портола", "Андерсоне", "Андерсон", "Marin Water",
        "Corte Madera", "авеню Пьемонт", "Аламеда", "Alameda", "Контра-Коста", "Contra Costa County", 
        "East Bay", "South Bay", "районе Уотсонвилля", "Уотсонвилл", "Уотсонвилля", "Redwood Forest",
        "Кастро-Вэлли", "94132",
        "Santa Monica", "Санта-Моника", "Санта-Моники", "Санта-Монике",
        "Beverly Hills", "Беверли-Хиллз", "Беверли-Хиллза", "Беверли-Хиллзe",
        "West Hollywood", "Западный Голливуд", "Западного Голливуда", "Западном Голливуде",
        "Hollywood", "Голливуд", "Голливуда", "Голливуде",
        "Culver City", "Калвер-Сити", "Калвер-Сити",
        "Burbank", "Бербанк", "Бербанка", "Бербанке",
        "Glendale", "Глендейл", "Глендейла", "Глендейле",
        "Torrance", "Торранс", "Торранса", "Торрансе",
        "Pasadena", "Пасадена", "Пасадены", "Пасадене",
        "Long Beach", "Лонг-Бич", "Лонг-Бича", "Лонг-Биче",
        "Santa Ana", "Санта-Ана", "Санта-Аны", "Санта-Ане",
        "Huntington Beach", "Хантингтон-Бич", "Хантингтон-Бича", "Хантингтон-Биче",
        "Newport Beach", "Ньюпорт-Бич", "Ньюпорт-Бича", "Ньюпорт-Биче",
        "Costa Mesa", "Коста-Меса", "Коста-Месы", "Коста-Месе",
        "Irvine", "Ирвайн", "Ирвайна", "Ирвайне",
        "La Jolla", "Ла-Хойя", "Ла-Хойи", "Ла-Хойе",
        "Chula Vista", "Чула-Виста", "Чула-Висты", "Чула-Висте",
        "Oceanside", "Оушенсайд", "Оушенсайда", "Оушенсайде",
        "Carlsbad", "Карлсбад", "Карлсбада", "Карлсбаде"
    ],
    "New Hampshire": [
        "NH", "新罕布什尔州", "新罕州", "新罕布什尔", "Нью-Гэмпшир", "НХ",
        "Нью-Гэмпшира", "Нью-Гэмпшире",
        "Manchester", "manchester", "Манчестер", "Манчестера", "Манчестере",
        "Nashua", "nashua", "Нашуа", "Нашуа",
        "Concord", "concord", "Конкорд", "Конкорда", "Конкорде",
        "Derry", "derry", "Дерри", "Дерри",
        "Rochester", "rochester", "Рочестер", "Рочестера", "Рочестере",
        "Dover", "dover", "Довер", "Довера", "Довере",
        "Keene", "keene", "Кин", "Кина", "Кине",
        "Portsmouth", "portsmouth", "Портсмут", "Портсмута", "Портсмуте",
        "Seacoast", "Морское побережье",
        "White Mountains", "Белые горы",
        "Lakes Region", "Озёрный край",
        "Upper Valley", "Верхняя долина"
    ],
    "New Jersey": [
        "NJ", "新泽西州", "新州", "泽西市","新泽西", "jersey city","Нью-Джерси", "НД",
        "Englewood Cliffs", "englewood cliffs",
        "East Hanover", "East Hanover East Hanover",
        "Edison", "edison",
        "Jersey City", "jersey city", "Джерси-Сити", "Джерси-Сити",
        "Newark", "newark", "Ньюарк", "Ньюарка", "Ньюарке",
        "Paterson", "paterson", "Патерсон", "Патерсона", "Патерсоне",
        "Elizabeth", "elizabeth", "Элизабет", "Элизабета", "Элизабете",
        "Edison", "edison", "Эдисон", "Эдисона", "Эдисоне",
        "Englewood Cliffs", "englewood cliffs", "Энглвуд-Клиффс", "Энглвуд-Клиффса", "Энглвуд-Клиффсе",
        "East Hanover", "east hanover", "Ист-Хановер", "Ист-Хановера", "Ист-Хановере",
        "Hoboken", "hoboken", "Хобокен", "Хобокена", "Хобокене",
        "Fort Lee", "fort lee", "Форт-Ли", "Форт-Ли",
        "Princeton", "princeton", "Принстон", "Принстона", "Принстоне",
        "North Jersey", "Северный Нью-Джерси",
        "Central Jersey", "Центральный Нью-Джерси",
        "South Jersey", "Южный Нью-Джерси",
        "Jersey Shore", "Побережье Нью-Джерси",
        "Greater New York Area", "Нью-Йоркская агломерация"
    ],
    "New Mexico": [
        "NM", "新墨西哥州", "墨州", "新墨西哥", "Нью-Мексико", "НМ",
        "Albuquerque", "albuquerque", "Альбукерке", "Альбукерке",
        "Santa Fe", "santa fe", "Санта-Фе", "Санта-Фе",
        "Las Cruces", "las cruces", "Лас-Крусес", "Лас-Крусеса", "Лас-Крусесе",
        "Rio Rancho", "rio rancho", "Рио-Ранчо", "Рио-Ранчо",
        "Roswell", "roswell", "Розуэлл", "Розуэлла", "Розуэлле",
        "Farmington", "farmington", "Фармингтон", "Фармингтона", "Фармингтоне",
        "Four Corners", "Четыре угла"
    ],
    "New York": [
        "NY", "纽约州", "Queens","纽约州", "纽约", "Ｎｙ","洛克菲勒中心", "八大道附近",
        "紐約", "長島","BRONX","Нью-Йорк", "N Y","НЙ", "曼哈顿", "法拉盛","长岛",
        "布鲁克林", "皇后区", "法盛", "曼克顿", "上州", "雪城", "布鲁", "史丹顿岛", "皇后",
        "elmhurst", "Elmhurst", "Elmhurst MY",
        "Woodhaven", "woodhaven",
        "Hempstead", "hempstead",
        "Islip", "islip",
        "BK", "Ｂｋ", "Ｂｋ Ｂｋ",
        "發拉盛",    
        "新鲜草原",  
        "大学点",   
        "小頸區",    
        "8大道",
        "Brooklyn", "Manhattan", "Queens", "Staten Island", "Kings Hwy", "Long Island", 
        "Ocean Ave. & Ave.R", "Нью-Йорке",
        "Buffalo", "buffalo", "Баффало", "Баффало",
        "Rochester", "rochester", "Рочестер", "Рочестера", "Рочестере",
        "Albany", "albany", "Олбани",
        "Yonkers", "yonkers", "Йонкерс", "Йонкерса", "Йонкерсе",
        "White Plains", "white plains", "Уайт-Плейнс", "Уайт-Плейнса", "Уайт-Плейнсе",
        "New Rochelle", "new rochelle", "Нью-Рошель", "Нью-Рошели", "Нью-Рошели",
        "Binghamton", "binghamton", "Бингемтон", "Бингемтона", "Бингемтоне",
        "Utica", "utica", "Ютика", "Ютики", "Ютике",
        "Ithaca", "ithaca", "Итака", "Итаки", "Итаке"
    ],
    "North Carolina": [
        "NC", "北卡罗来纳州", "北卡", "北卡罗来纳", "Северная Каролина", "СК", "夏洛特",
        "Durham", "durham",
        "Duke university",
        "Durham Duke university",
        "Charlotte", "charlotte", "Шарлотт", "Шарлотта", "Шарлотте",
        "Raleigh", "raleigh", "Роли", "Роли",
        "Durham", "durham", "Дарем", "Дарема", "Дареме",
        "Chapel Hill", "chapel hill", "Чапел-Хилл", "Чапел-Хилла", "Чапел-Хилле",
        "Greensboro", "greensboro", "Гринсборо", "Гринсборо",
        "Winston-Salem", "winston-salem", "Уинстон-Сейлем", "Уинстон-Сейлема", "Уинстон-Сейлеме",
        "Fayetteville", "fayetteville", "Фейетвилл", "Фейетвилла", "Фейетвилле",
        "Asheville", "asheville", "Эшвилл", "Эшвилла", "Эшвилле",
        "Research Triangle", "Исследовательский треугольник",
        "Triangle Area", "Треугольник",
        "Piedmont Triad", "Пьемонтский триад",
        "Северной Каролины", "Северной Каролине"
    ],
    "North Dakota": [
        "ND", "北达科他州", "北达州", "北达科他", "Северная Дакота", "НД",
        "Северной Дакоты", "Северной Дакоте",
        "Fargo", "fargo", "Фарго", "Фарго",
        "Bismarck", "bismarck", "Бисмарк", "Бисмарка", "Бисмарке",
        "Grand Forks", "grand forks", "Гранд-Форкс", "Гранд-Форкса", "Гранд-Форксе",
        "Minot", "minot", "Майнот", "Майнота", "Майноте"
    ],
    "Ohio": [
        "俄亥俄州", "俄州", "俄亥俄", "Огайо", "ОХ",
        "Columbus", "columbus", "Колумбус", "Колумбуса", "Колумбусе",
        "Cleveland", "cleveland", "Кливленд", "Кливленда", "Кливленде",
        "Cincinnati", "cincinnati", "Цинциннати", "Цинциннати",
        "Toledo", "toledo", "Толидо", "Толидо",
        "Akron", "akron", "Акрон", "Акрона", "Акроне",
        "Dayton", "dayton", "Дейтон", "Дейтона", "Дейтоне"
    ],
    "Oklahoma": [
        "俄克拉荷马州", "俄克州", "俄克拉荷马", "Оклахома",
        "Оклахомы", "Оклахоме",
        "Oklahoma City", "oklahoma city", "Оклахома-Сити", "Оклахома-Сити",
        "Tulsa", "tulsa", "Талса", "Талсы", "Талсе",
        "Norman", "norman", "Норман", "Нормана", "Нормане",
        "Broken Arrow", "broken arrow", "Брокен-Эрроу", "Брокен-Эрроу",
        "Edmond", "edmond", "Эдмонд", "Эдмонда", "Эдмонде"
    ],
    "Oregon": [
        "俄勒冈州", "俄勒州", "泼特兰","俄勒冈", "波特兰","Beaverton", "泼特兰","Орегон", "ОР", 
        "Орегона", "Орегоне",
        "Portland", "portland", "Портленд", "Портленда", "Портленде",
        "Beaverton", "beaverton", "Бивертон", "Бивертона", "Бивертоне",
        "Hillsboro", "hillsboro", "Хиллсборо", "Хиллсборо",
        "Eugene", "eugene", "Юджин", "Юджина", "Юджине",
        "Salem", "salem", "Сейлем", "Сейлема", "Сейлеме",
        "Bend", "bend", "Бенд", "Бенда", "Бенде",
        "Willamette Valley", "Долина Уилламетт",
        "Pacific Northwest", "Тихоокеанский Северо-Запад"
    ],
    "Pennsylvania": [
        "宾夕法尼亚州", "宾州", "宾夕法尼亚", "宾洲","Pittsburg","Пенсильвания", "ПА","滨州",
        "费城", "匹兹堡", "Пенсильвании",
        "Philadelphia", "philadelphia", "Филадельфия", "Филадельфии", "Филадельфии",
        "Pittsburgh", "pittsburgh", "Питтсбург", "Питтсбурга", "Питтсбурге",
        "Allentown", "allentown", "Аллентаун", "Аллентауна", "Аллентауне",
        "Erie", "erie", "Эри", "Эри",
        "Reading", "reading", "Рединг", "Рединга", "Рединге",
        "Scranton", "scranton", "Скрантон", "Скрантона", "Скрантоне",
        "Bethlehem", "bethlehem", "Бетлехем", "Бетлехема", "Бетлехеме",
        "Philadelphia Metro", "Филадельфийская агломерация"
    ],
    "Rhode Island": [
        "罗得岛州", "罗州", "罗德岛","罗得岛", "Род-Айленд", "РИ",
        "Род-Айленда", "Род-Айленде",
        "Providence", "providence", "Провиденс", "Провиденса", "Провиденсе",
        "Warwick", "warwick", "Уорик", "Уорика", "Уорике",
        "Cranston", "cranston", "Кранстон", "Кранстона", "Кранстоне",
        "Pawtucket", "pawtucket", "Потакет", "Потакета", "Потакете",
        "Newport", "newport", "Ньюпорт", "Ньюпорта", "Ньюпорте",
        "Aquidneck Island", "Остров Аквиднек"
    ],
    "South Carolina": [
        "SC", "南卡罗来纳州", "南卡", "南卡罗来纳", "Южная Каролина", "СК",
        "Южной Каролины", "Южной Каролине",
        "Charleston", "charleston", "Чарлстон", "Чарлстона", "Чарлстоне",
        "Columbia", "columbia", "Колумбия", "Колумбии", "Колумбии",
        "Greenville", "greenville", "Гринвилл", "Гринвилла", "Гринвилле",
        "Myrtle Beach", "myrtle beach", "Миртл-Бич", "Миртл-Бича", "Миртл-Биче",
        "Spartanburg", "spartanburg", "Спартанберг", "Спартанберга", "Спартанберге",
        "Hilton Head", "hilton head", "Хилтон-Хед", "Хилтон-Хеда", "Хилтон-Хеде",
        "Lowcountry", "Лоукантри",
        "Midlands", "Мидлендс"
    ],
    "South Dakota": [
        "SD", "南达科他州", "南达州", "南达科他", "Южная Дакота", "СД",
        "Южной Дакоты", "Южной Дакоте",
        "Sioux Falls", "sioux falls", "Су-Фолс", "Су-Фолса", "Су-Фолсе",
        "Rapid City", "rapid city", "Рапид-Сити", "Рапид-Сити",
        "Aberdeen", "aberdeen", "Абердин", "Абердина", "Абердине",
        "Brookings", "brookings", "Брукингс", "Брукингса", "Брукингсе",
        "Pierre", "pierre", "Пирр", "Пирра", "Пирре",
        "Black Hills", "Блэк-Хиллс"
    ],
    "Tennessee": [
        "TN", "田纳西州", "田州", "田纳西", "Теннесси", "ТН",
        "Nashville", "nashville", "Нэшвилл", "Нэшвилла", "Нэшвилле",
        "Memphis", "memphis", "Мемфис", "Мемфиса", "Мемфисе",
        "Knoxville", "knoxville", "Ноксвилл", "Ноксвилла", "Ноксвилле",
        "Chattanooga", "chattanooga", "Чаттануга", "Чаттануги", "Чаттануге",
        "Clarksville", "clarksville", "Кларксвилл", "Кларксвилла", "Кларксвилле",
        "Murfreesboro", "murfreesboro", "Мерфрисборо", "Мерфрисборо"
    ],
    "Texas": [
        "TX", "得克萨斯州", "德州", "得克萨斯", "Техас", "ТХ", "休斯顿", "达拉斯",
        "奥斯汀", "圣安东尼奥", "沃斯堡", "奥斯丁","休斯敦",
        "Боллинджере", "Боллинджер",
        "Houston", "houston", "Хьюстон", "Хьюстона", "Хьюстоне",
        "Dallas", "dallas", "Даллас", "Далласа", "Далласе",
        "Austin", "austin", "Остин", "Остина", "Остине",
        "San Antonio", "san antonio", "Сан-Антонио", "Сан-Антонио",
        "Fort Worth", "fort worth", "Форт-Уэрт", "Форт-Уэрта", "Форт-Уэрте",
        "El Paso", "el paso", "Эль-Пасо", "Эль-Пасо",
        "Arlington", "arlington", "Арлингтон", "Арлингтона", "Арлингтоне",
        "Plano", "plano", "Плейно", "Плейно",
        "Frisco", "frisco", "Фриско", "Фриско",
        "Техаса", "Техасе", "Hill Country", "Холмистая страна"
    ],
    "Utah": [ 
        "犹他州", "犹州", "犹他", "Юта", "ЮТ", "Солт-Лейк-Сити",
        "Юты", "Юте",
        "Salt Lake City", "salt lake city", "Солт-Лейк-Сити", "Солт-Лейк-Сити",
        "Provo", "provo", "Прово", "Прово",
        "Orem", "orem", "Орем", "Орема", "Ореме",
        "Ogden", "ogden", "Огден", "Огдена", "Огдене",
        "Park City", "park city", "Парк-Сити", "Парк-Сити",
        "St. George", "st george", "Сент-Джордж", "Сент-Джорджа", "Сент-Джордже",
        "Wasatch Front", "Фронт Уосатч"
    ],
    "Vermont": [
        "VT", "佛蒙特州", "佛蒙州", "佛蒙特", "Вермонт", "ВТ",
        "Вермонта", "Вермонте",
        "Burlington", "burlington", "Берлингтон", "Берлингтона", "Берлингтоне",
        "Montpelier", "montpelier", "Монтпилиер", "Монтпилиера", "Монтпилиере",
        "Rutland", "rutland", "Ратленд", "Ратленда", "Ратленде",
        "St. Albans", "st albans", "Сент-Олбанс", "Сент-Олбанса", "Сент-Олбансе",
        "Brattleboro", "brattleboro", "Браттлборо", "Браттлборо",
        "Green Mountains", "Зелёные горы"
    ],
    "Virginia": [
        "VA", "弗吉尼亚州", "弗州", "弗吉尼亚", "Виргиния", "ВА", "维州", "维吉尼亚", "北维",
        "Richmond", "richmond", "Ричмонд", "Ричмонда", "Ричмонде",
        "Virginia Beach", "virginia beach", "Вирджиния-Бич", "Вирджиния-Бича", "Вирджиния-Биче",
        "Norfolk", "norfolk", "Норфолк", "Норфолка", "Норфолке",
        "Chesapeake", "chesapeake", "Чесапик", "Чесапика", "Чесапике",
        "Arlington", "arlington", "Арлингтон", "Арлингтона", "Арлингтоне",
        "Alexandria", "alexandria", "Александрия", "Александрии", "Александрии",
        "Fairfax", "fairfax", "Фэрфакс", "Фэрфакса", "Фэрфаксе",
        "NoVA", "Нова",
        "Tidewater", "Тайдуотер",
        "Hampton Roads", "Хэмптон-Роудс"
    ],
    "Washington": [
        "华盛顿州", "华州", "华盛顿", "西亚图","Вашингтон", "ВАШ", "西雅图",
        "Вашингтон штат", "штат Вашингтон",
        "Bellevue", "seattle",
        "Everett", "everett",
        "Kent", "kent",
        "Lynnwood", "lynnwood",
        "Renton", "renton",
        "Bothell", "bothell",
        "塔科马", 
        "Кенте", "Спокан", "Спокане", "Вашингтоне",
        "Spokane", "spokane", "Спокан", "Спокана", "Спокане",
        "Vancouver", "vancouver", "Ванкувер", "Ванкувера", "Ванкувере",
        "Olympia", "olympia", "Олимпия", "Олимпии", "Олимпии",
        "Bellingham", "bellingham", "Беллингем", "Беллингема", "Беллингеме",
        "Yakima", "yakima", "Якима", "Якимы", "Якиме",
        "Walla Walla", "walla walla", "Уолла-Уолла", "Уолла-Уоллы", "Уолла-Уолле",
        "Richland", "richland", "Ричленд", "Ричленда", "Ричленде",
        "Kennewick", "kennewick", "Кенневик", "Кенневика", "Кенневике",
        "Pasco", "pasco", "Паско",
        "Puget Sound", "Пьюджет-Саунд",
        "Western Washington", "Западный Вашингтон",
        "Eastern Washington", "Восточный Вашингтон",
        "Tri-Cities", "Три-Сити",
        "Columbia Basin", "Колумбийская низменность",
        "Inland Northwest", "Внутренний Северо-Запад"
    ],

    "West Virginia": [ 
        "西弗吉尼亚州", "西弗州", "西弗吉尼亚", "Западная Виргиния", "ЗВ", "WV", "West Virginia",
        "Западной Виргинии", 
        "Charleston", "charleston", "Чарлстон", "Чарлстона", "Чарлстоне",
        "Huntington", "huntington", "Хантингтон", "Хантингтона", "Хантингтоне",
        "Morgantown", "morgantown", "Моргантаун", "Моргантауна", "Моргантауне",
        "Parkersburg", "parkersburg", "Паркерсберг", "Паркерсберга", "Паркерсберге",
        "Wheeling", "wheeling", "Уилинг", "Уилинга", "Уилинге",
        "Appalachia", "Аппалачи"
    ],
    "Wisconsin": [
        "威斯康星州", "威州", "威斯康星", "Висконсин", "ВС", "WI", "Wisconsin",
        "Висконсина", "Висконсине",
        "Milwaukee", "milwaukee", "Милуоки", "Милуоки",
        "Madison", "madison", "Мэдисон", "Мэдисона", "Мэдисоне",
        "Green Bay", "green bay", "Грин-Бей", "Грин-Бея", "Грин-Бее",
        "Kenosha", "kenosha", "Кеноша", "Кеноши", "Кеноше",
        "Racine", "racine", "Рейсин", "Рейсина", "Рейсине",
        "Appleton", "appleton", "Эпплтон", "Эпплтона", "Эпплтоне"
    ],
    "Wyoming": [
        "WY", "怀俄明州", "怀州", "怀俄明", "Вайоминг", "ВЙ",
        "Вайоминга", "Вайоминге", 
        "Cheyenne", "cheyenne", "Шайенн", "Шайенна", "Шайенне",
        "Casper", "casper", "Каспер", "Каспера", "Каспере",
        "Laramie", "laramie", "Ларами", "Ларами",
        "Gillette", "gillette", "Джиллетт", "Джиллетта", "Джиллетте",
        "Jackson", "jackson", "Джексон", "Джексона", "Джексоне",
        "Yellowstone", "Йеллоустон",
        "Grand Teton", "Гранд-Титон"
    ],
    "DC": [
        "华盛顿特区", "哥伦比亚特区", "华盛顿区", "Вашингтонский округ", "WD" , "DC", "Dc", "dc", "大华",
        "Вашингтон (округ Колумбия)", "Вашингтона (округа Колумбия)", "Вашингтоне (округе Колумбия)",
        "Вашингтон, округ Колумбия", "Вашингтона, округа Колумбия", "Вашингтоне, округе Колумбия",
        "Washington, DC", "Washington DC", "washington dc",
        "Capitol Hill", "capitol hill", "Капитолийский холм",
        "Downtown DC", "downtown dc", "Даунтаун Вашингтона"
    ],
    "Colorado": [
        "科罗拉多州", "科州", "科罗拉多", "Колорадо", "КО", "CO", "Colorado",
        "Denver", "denver", "Денвер", "Денвера", "Денвере",
        "Colorado Springs", "colorado springs", "Колорадо-Спрингс", "Колорадо-Спрингс",
        "Aurora", "aurora", "Аврора", "Авроры", "Авроре",
        "Fort Collins", "fort collins", "Форт-Коллинс", "Форт-Коллинса", "Форт-Коллинсе",
        "Boulder", "boulder", "Боулдер", "Боулдера", "Боулдере",
        "Front Range", "Фронт-Рейндж",
        "Rocky Mountains", "Скалистые горы"
    ],
    "Alabama": [
        "阿拉巴马州", "阿州", "阿拉巴马", "Алабама", "АЛ",
        "AL", "Alabama", "Алабамы", "Алабаме",
        "Birmingham", "birmingham", "Бирмингем", "Бирмингема", "Бирмингеме",
        "Montgomery", "montgomery", "Монтгомери", "Монтгомери",
        "Mobile", "mobile", "Мобил", "Мобила", "Мобиле",
        "Huntsville", "huntsville", "Хантсвилл", "Хантсвилла", "Хантсвилле",
        "Tuscaloosa", "tuscaloosa", "Таскалуса", "Таскалусы", "Таскалусе"
    ],
    "Alaska": [
        "阿拉斯加州", "阿拉州", "阿拉斯加", "Аляска",
        "Аляски", "Аляске", "AK", "Alaska",
        "Anchorage", "anchorage", "Анкоридж", "Анкориджа", "Анкоридже",
        "Fairbanks", "fairbanks", "Фэрбанкс", "Фэрбанкса", "Фэрбанксе",
        "Juneau", "juneau", "Джуно", "Джуно",
        "Sitka", "sitka", "Ситка", "Ситки", "Ситке"
    ],
    "Arizona": [
        "亚利桑那州", "亚利州", "亚利桑那", "Аризона", "АЗ",
        "AZ", "Arizona", "Аризоны", "Аризоне",
        "Phoenix", "phoenix", "Финикс", "Финикса", "Финиксе",
        "Tucson", "tucson", "Тусон", "Тусона", "Тусоне",
        "Mesa", "mesa", "Меса", "Месы", "Месе",
        "Scottsdale", "scottsdale", "Скоттсдейл", "Скоттсдейла", "Скоттсдейле",
        "Tempe", "tempe", "Темпе", "Темпе",
        "Flagstaff", "flagstaff", "Флагстафф", "Флагстаффа", "Флагстаффе"
    ],
    "Arkansas": [
        "阿肯色州", "阿肯州", "阿肯色", "Арканзас", "АР",
        "Арканзаса", "Арканзасе", "AR", "Arkansas",
        "Little Rock", "little rock", "Литл-Рок", "Литл-Рока", "Литл-Роке",
        "Fort Smith", "fort smith", "Форт-Смит", "Форт-Смита", "Форт-Смите",
        "Fayetteville", "fayetteville", "Фейетвилл", "Фейетвилла", "Фейетвилле",
        "Springdale", "springdale", "Спрингдейл", "Спрингдейла", "Спрингдейле",
        "Jonesboro", "jonesboro", "Джонсборо", "Джонсборо"
    ]
}




def get_state(description):
    states = []
    for state, variants in us_states.items():
        all_variants = [state] + variants
        for variant in all_variants:
            if variant.lower() in description.lower():
                states.append(state)
    return states

def get_gender_preference(description):
    pref = "No Preference"
    if "男女" in description or "男女不限" in description or ("男" in description and "女" in description):
        return "No Preference"
    elif "夫妻" in description:
        return "Couple"
    elif "男" in description or "male" in description.lower() or "man" in description.lower():
        pref = "Male"
    elif ("女" in description or "female" in description.lower() or "woman" in description.lower() ) and (not "子女" in description):
        pref = "Female"
    elif ("мужчина" in description.lower()
    or "мужчину" in description.lower()
    or "мужчины" in description.lower()
    or "мужской" in description.lower()):
        pref = "Male"
    elif ("женщина" in description.lower()
        or "женщину" in description.lower()
        or "женщины" in description.lower()
        or "женский" in description.lower()
        or "девушка" in description.lower()
        or "девушку" in description.lower()
        or "девушки" in description.lower()):
        pref = "Female"

    return pref

def label_job_type(description):
    job_type = "Other"
    description_lower = description.lower()
# Salon / Spa / Beauty
    if ("纹身" in description or "理发" in description or "发型" in description or
        "睫毛店" in description or "美睫" in description or "足疗" in description or
        "美甲" in description or "美容" in description or "美发" in description or
        "spa" in description_lower or "指甲" in description or "甲店" in description or
        # from rusrek: Парикмахерские, салоны, SPA + nails
        "парикмахерские" in description_lower or "салоны" in description_lower or
        "парикмахерская" in description_lower or "маникюр" in description_lower or
        "педикюр" in description_lower or "ногтевой" in description_lower or "salon" in description_lower):
        job_type = "Salon/Spa"
        return "Salon/Spa"
    
    elif ("前台" in description_lower or "receptionist" in description_lower or
          "企台" in description_lower or "front desk" in description_lower or
          "ресепш" in description_lower):  # Ресепшн в Медицинский СПА etc.
        job_type = "Receptionist"
        return "Receptionist"

    elif ("照顾" in description or "托管" in description or "管家" in description or "保母" in description or
          "nanny" in description_lower or "保姆" in description_lower or
          "照顾老人" in description_lower or "钟点工" in description_lower or
          "月嫂" in description_lower or "住家" in description_lower or
          "阿姨" in description_lower or "看护" in description_lower or
          # Russian nanny words
          "няня" in description_lower or "няни" in description_lower):
        job_type = "Nanny"
        return "Nanny"

    elif ("housekeeper" in description_lower or "清洁工" in description_lower or
          "家政" in description_lower or "保洁员" in description_lower or
          # rusrek: Уборка, работа по дому; Cleaning Lady!!
          "уборка" in description_lower or "работа по дому" in description_lower or
          "уборщиц" in description_lower or "cleaning lady" in description_lower):
        job_type = "Housekeeping"
        return "Housekeeping"

    elif ("司机" in description_lower or "driver" in description_lower or
          "司機" in description_lower or
          # rusrek: Водители, экспедиторы, диспетчера; CDL/Truck drivers
          "водитель" in description_lower or "водители" in description_lower or
          "диспетчер" in description_lower or "диспетчера" in description_lower or
          "cdl" in description_lower or "truck driver" in description_lower):
        job_type = "Driver"
        return "Driver"

    elif ("捐卵" in description_lower or "egg donor" in description_lower or
          "献卵" in description_lower):
        job_type = "Egg Donor"
        return "Egg Donor"

    elif ("老师" in description_lower or "辅导" in description_lower or
          "家教" in description_lower or "导师" in description_lower or
          "教师" in description_lower or
          # rusrek category: Образование, спорт; also specific teacher/tutor
          "образование" in description_lower or "учитель" in description_lower or
          "преподавател" in description_lower or "тренер" in description_lower or
          "tutor" in description_lower or "teacher" in description_lower):
        job_type = "Education"
        return "Education"

    elif ("助理" in description or "助理" in description_lower or
          "assistant" in description_lower or "ассистент" in description_lower):
        job_type = "Assistant"
        return "Assistant"

    elif ("文员" in description_lower or "clerk" in description_lower or
          "administrative" in description_lower or
          "office jobs" in description_lower or
          "office administrator" in description_lower or
          "офис" in description_lower):
        job_type = "Clerical"
        return "Clerical"

    elif ("仓库" in description_lower or "warehouse" in description_lower or
          "物流" in description_lower or
          "warehouse worker" in description_lower or
          "складской" in description_lower or "склад" in description_lower):
        job_type = "Warehouse"
        return "Warehouse"

    # Massage / Foot spa
    elif ("床店" in description or "足背店" in description or "正规店" in description or
          "推拿" in description or "massage" in description_lower or
          "按摩" in description_lower or "熟客" in description_lower or
          "技师" in description_lower or "脚店" in description_lower or
          "脚背店" in description or
          # rusrek: массажный салон, массажистка, массаж
          "массаж" in description_lower or "массажист" in description_lower or
          "массажистка" in description_lower):
        job_type = "Massage"
        return "Massage"

    elif ("analyst" in description_lower or "分析" in description_lower or
          "数据" in description_lower or "data" in description_lower):
        job_type = "Analyst"
        return "Analyst"

    elif ("采购" in description or "代购" in description or
          "buyer" in description_lower or "买手" in description_lower or
          "закуп" in description_lower):
        job_type = "Buyer/procurement"
        return "Buyer/procurement"

    if ("保险公司" in description or "金融" in description or
        # rusrek: Финансы, бухгалтерия, страхование
        "финансы" in description_lower or "страхование" in description_lower or
        "insurance" in description_lower or "brokerage" in description_lower):
        job_type = "Finance/Insurance"
        return "Finance/Insurance"

    elif ("army" in description_lower or "陆军" in description or
          "海军" in description or "空军" in description or "军事" in description or
          "вооруженные силы" in description_lower or "армия" in description_lower):
        job_type = "Military"
        return "Military"

    elif ("维修" in description or "焊工" in description or
          "Developer" in description or "Technician" in description or
          "技术员" in description or "技工" in description or "工程师" in description or
          "电工" in description_lower or "技术人员" in description_lower or "修车" in description_lower or
          # rusrek: техник, инженер, HVAC, кабельный техник
          "техник" in description_lower or "инженер" in description_lower or
          "hvac" in description_lower or "кабельный техник" in description_lower):
        job_type = "Technician/Engineer"
        return "Technician/Engineer"

    elif ("木工" in description_lower or "carpenter" in description_lower or
          "плотник" in description_lower or "carpenters" in description_lower):
        job_type = "Carpentry"
        return "Carpentry"

    elif ("会计" in description_lower or "accountant" in description_lower or
          "bookkeeper" in description_lower or "簿记" in description_lower or
          "бухгалтер" in description_lower or "cpa" in description_lower):
        job_type = "Accounting"
        return "Accounting"
    
    # Restaurant / food service
    elif ("后厨" in description or "服务生" in description or "送餐" in description or "帮厨" in description or
          "烘培" in description or "甜品" in description or "小吃店" in description or
          "sushi" in description or "厨房" in description or "川菜" in description or
          "火锅" in description or "厨师" in description_lower or
          "帮炒" in description_lower or "日餐" in description_lower or
          "茶店" in description_lower or "寿司" in description_lower or
          "炒锅" in description_lower or "洗碗" in description_lower or
          "餐馆" in description_lower or "中餐" in description_lower or
          "西餐" in description_lower or "外卖" in description_lower or
          "歺" in description_lower or "油锅" in description_lower or "酒庄" in description_lower or
          # rusrek: Рестораны, клубы, питание
          "рестораны" in description_lower or "ресторан" in description_lower or
          "клубы" in description_lower or "официант" in description_lower or
          "waitress" in description_lower or "бармен" in description_lower or
          "бариста" in description_lower):
        job_type = "Restaurant service" 
        return "Restaurant service"

    elif "设计师" in description_lower or "graphic designer" in description_lower or "дизайнер" in description_lower:
        job_type = "Designer"
        return "Designer"

    elif ("电影" in description or "影视" in description or
          "剪辑" in description_lower or "后期" in description or
          "摄影" in description or
          "фотограф" in description_lower or "videographer" in description_lower):
        job_type = "Arts/Music/Media"
        return job_type

    elif ("导购" in description_lower or "sales associate" in description_lower or
          "salesperson" in description_lower or "销售" in description_lower or
          # rusrek: Торговля, магазины, базы; продавец/кассир
          "торговля" in description_lower or "магазины" in description_lower or
          "продавец" in description_lower or "cashier" in description_lower or
          "кассир" in description_lower or "sales representative" in description_lower):
        job_type = "Sales"
        return "Sales"

    elif "运营" in description or "operations" in description_lower:
        job_type = "Operations"
        return "Operations"

    elif ("Marketing" in description or "推广" in description or "市场营销" in description or
          "маркетинг" in description_lower or "маркетолог" in description_lower or
          "реклама" in description_lower or "advertising" in description_lower):
        job_type = "Marketing"
        return "Marketing"

    elif ("escort" in description_lower or "陪侍" in description_lower or
          "陪护" in description_lower or "伴游" in description_lower):
        job_type = "Escort"
        return "Escort"

    elif ("导游" in description or "地陪" in description or
          "地接" in description or "旅行社" in description or "旅游公司" in description or
          # rusrek: Недвижимость, туризм + travel agent
          "туризм" in description_lower or "travel agent" in description_lower):
        job_type = "Tour Guide"
        return "Tour Guide"

    elif "翻译" in description or "переводчик" in description_lower or "translator" in description_lower:
        job_type = "Translator"
        return "Translator"

    elif ("model" in description_lower or "模特" in description_lower or
          "модел" in description_lower or "models needed" in description_lower):
        job_type = "Modeling"
        return "Modeling"

    elif ("电商" in description or "亚马逊" in description or
          "ebay" in description or "amazon" in description_lower or
          "e-commerce" in description_lower or "онлайн магазин" in description_lower):
        job_type = "E-commerce"
        return "E-commerce"

    elif ("dancer" in description_lower or "舞蹈" in description_lower or
          "舞女" in description_lower or
          "танцовщица" in description_lower or "танцор" in description_lower or
          # rusrek: Музыканты, певцы, танцоры, модели
          "музыкант" in description_lower or "певец" in description_lower or
          "певица" in description_lower or "singer" in description_lower):
        job_type = "Dancing"
        return "Dancing"

    elif ("server" in description_lower or "服务员" in description_lower or
          "餐厅" in description_lower or "酒吧" in description_lower or
          "饭店" in description_lower or
          "серверы" in description_lower):  # СЕРВЕРЫ (servers)
        job_type = "Server"
        return "Server"
    elif "农场" in description or "farm" in description_lower or "ферма" in description_lower or "棚" in description:
        job_type = "Farm"
        return "Farm"
    elif ("剂师" in description or "治疗" in description or "诊所" in description or
          "临床" in description_lower or "护理" in description_lower or
          "护士" in description_lower or "healthcare" in description_lower or
          "clinic" in description_lower or
          # rusrek: Медицина, аптеки, фитнес; HHA/PCA; medical office
          "медицина" in description_lower or "аптека" in description_lower or
          "аптеки" in description_lower or "медицинский офис" in description_lower or
          "medical office" in description_lower or "medical assistant" in description_lower or
          "hha" in description_lower or "pca" in description_lower or "医师" in description_lower or
          "home care" in description_lower):
        job_type = "Healthcare"
        return "Healthcare"

    elif ("肉部" in description or "超市" in description or "食品店" in description or
          "超级市场" in description or "HMart" in description or "食品公司" in description or
          "grocery" in description_lower or
          "продуктовый магазин" in description_lower or "супермаркет" in description_lower):
        job_type = "Grocery store"
        return "Grocery store"
    
    elif ("装修" in description_lower or "安装" in description or "建筑" in description or
          # rusrek: Строительство, архитектура, ремонт
          "строительство" in description_lower or "строительной компании" in description_lower or
          "ремонт" in description_lower or "construction" in description_lower):
        job_type = "Construction/Renovation"
        return "Construction/Renovation"

    # --- NEW GROUPS from rusrek data ---

    # Factory / Production / Dry cleaning
    elif ("фабрики" in description_lower or "фабрика" in description_lower or
          "производства" in description_lower or "производство" in description_lower or
          "химчистка" in description_lower or "dry cleaning" in description_lower):
        job_type = "Factory/Production"
        return "Factory/Production"

    # IT / Programming / Computers / Internet
    elif ("программирование" in description_lower or "программист" in description_lower or
          "software developer" in description_lower or "разработчик" in description_lower or
          "компьютеры" in description_lower or "it specialist" in description_lower or
          "it-специалист" in description_lower or "интернет" in description_lower):
        job_type = "IT/Programming"
        return "IT/Programming"

    # Real estate & tourism (separate from Tour Guide above for broader roles)
    elif ("недвижимость" in description_lower or "риелтор" in description_lower or
          "realtor" in description_lower or
          "туризм" in description_lower or "travel agency" in description_lower):
        job_type = "Real estate/Tourism"
        return "Real estate/Tourism"

    # Auto repair / mechanic
    elif ("авторемонт" in description_lower or "авто ремонт" in description_lower or
          "auto repair" in description_lower or "автомеханик" in description_lower or
          "mechanic" in description_lower or "body shop" in description_lower):
        job_type = "Auto repair"
        return "Auto repair"

    # Security / Guard
    elif ("охранник" in description_lower or "охрана" in description_lower or
          "security guard" in description_lower or "security" in description_lower):
        job_type = "Security"
        return "Security"

    # Legal
    elif ("юрист" in description_lower or "адвокат" in description_lower or
          "attorney" in description_lower or "lawyer" in description_lower or
          "paralegal" in description_lower or "law firm" in description_lower):
        job_type = "Legal"
        return "Legal"
    
        # NEW: customer service / call center
    elif ("客服" in description or "客服人员" in description or "客服接线员" in description or 
          "电话秘书" in description or "电话接听员" in description or 
          "call center" in description_lower or "customer service" in description_lower):
        job_type = "Customer Service"
        return "Customer Service"
    
        # NEW: performer / entertainer (musician,主播, etc.)
    elif ("民乐演奏" in description or "演奏表演" in description or "演出" in description or 
          "主播" in description or "直播" in description_lower or "歌手" in description or "演员" in description):
        job_type = "Performer/Entertainer"
        return "Performer/Entertainer"
    
        # NEW: factory / production / packaging
    elif ("工厂" in description or "厂工" in description or "生产" in description or 
          "车间" in description or "包装" in description or "胶水公司" in description or 
          "生产包装" in description or "manufactur" in description_lower or "工人" in description_lower) :
        job_type = "Factory/Manufacturing"
        return "Factory/Manufacturing"
    
        # NEW: software / programmer
    elif ("程序员" in description or "开发" in description or 
          "programmer" in description_lower or "java" in description_lower or 
          "c#" in description_lower or "android" in description_lower or "ios" in description_lower or
          "php" in description_lower or "asp.net" in description_lower):
        job_type = "Technician/Engineer"
        return "Technician/Engineer"
    
        # NEW: government jobs / training
    elif "政府工" in description or "政府工作" in description or "政府后勤" in description:
        job_type = "Government job"
        return "Government job"
    
       # NEW: real-estate specific
    elif ("地产" in description or "房地产" in description or "豪宅" in description or 
          "商业楼" in description or "公寓" in description or 
          "real estate" in description_lower or "realtor" in description_lower or "broker" in description_lower):
        job_type = "Real Estate"
        return "Real Estate"
    
        # NEW: exhibition / trade-show / convention work
    elif ("展会" in description or "展览" in description or "展台" in description or "会展" in description or 
          "展览馆" in description or "展会工人" in description or "CES展" in description or 
          "trade show" in description_lower or "convention center" in description_lower):
        job_type = "Exhibition/Trade show"
        return "Exhibition/Trade show"
    
    elif ("строитель" in description_lower or "строительная компания" in description_lower or
        "стройка" in description_lower or "ремонт" in description_lower or
        "carpenter" in description_lower or "плотник" in description_lower or
        "electrician" in description_lower or "электрик" in description_lower or
        "plumber" in description_lower or "сантехник" in description_lower or
        "roofer" in description_lower or "roofing" in description_lower or
        "hvac" in description_lower or "mechanic" in description_lower or
        "механик" in description_lower or "handyman" in description_lower or
        "разнорабочий" in description_lower or "maintenance" in description_lower or
        "техническое обслуживание" in description_lower or
        "installer" in description_lower or "монтажник" in description_lower or
        "welding" in description_lower or "сварщик" in description_lower or
        "масон" in description_lower or "mason" in description_lower or
        "concrete" in description_lower or "бетон" in description_lower):
        return "Construction/Skilled Trades"
    
    # ---------- Sewing / Tailor / Furniture Shop ----------
    elif ("швейный" in description_lower or "мебельный бизнес" in description_lower or
        "мебельный" in description_lower or "швея" in description_lower or
        "портной" in description_lower or "портниха" in description_lower or
        "seamstress" in description_lower or "tailor" in description_lower or
        "upholstery" in description_lower or "обивка" in description_lower):
        return "Sewing/Furniture"

    # ---------- Construction / Skilled Trades / Maintenance ----------
    elif ("строитель" in description_lower or "строительная компания" in description_lower or
        "стройка" in description_lower or "ремонт" in description_lower or
        "carpenter" in description_lower or "плотник" in description_lower or
        "electrician" in description_lower or "электрик" in description_lower or
        "plumber" in description_lower or "сантехник" in description_lower or
        "roofer" in description_lower or "roofing" in description_lower or
        "hvac" in description_lower or "mechanic" in description_lower or
        "механик" in description_lower or "handyman" in description_lower or
        "разнорабочий" in description_lower or "maintenance" in description_lower or
        "техническое обслуживание" in description_lower or
        "installer" in description_lower or "монтажник" in description_lower or
        "welding" in description_lower or "сварщик" in description_lower or
        "масон" in description_lower or "mason" in description_lower or
        "concrete" in description_lower or "бетон" in description_lower):
        return "Construction/Skilled Trades"

    # ---------- Cleaning / Housekeeping ----------
    elif ("清洁" in description or "cleaning" in description_lower or "housekeeping" in description_lower or
        "maid" in description_lower or "housekeeper" in description_lower or
        "уборка" in description_lower or "клининг" in description_lower or
        "limpieza" in description_lower or "лимпьеса" in description_lower or
        "domestica" in description_lower or "домработниц" in description_lower or
        "домработник" in description_lower or "good care agency" in description_lower):
        return "Housekeeping"

    # ---------- Childcare / Daycare / Nanny ----------
    elif ("детский сад" in description_lower or "садик" in description_lower or
        "daycare" in description_lower or "preschool" in description_lower or
        "after school" in description_lower or "послешкольн" in description_lower or
        "няня" in description_lower or "nanny" in description_lower or
        "babysit" in description_lower or
        "воспитател" in description_lower or "teacher assistant" in description_lower):
        return "Nanny"

    # ---------- Elderly / Home Care / Caregiving ----------
    elif ("сиделка" in description_lower or "ухо" in description_lower and "престарел" in description_lower or
        "senior care" in description_lower or "home care" in description_lower or
        "home attendant" in description_lower or "homeattend" in description_lower or
        "home health aide" in description_lower or "hha" in description_lower or
        "ihss" in description_lower or
        "agencia de cuidado" in description_lower or
        "bestcare" in description_lower or
        "caring professionals" in description_lower):
        return "Nanny"

    # ---------- Medical / Healthcare / Dental ----------
    elif ("nurse" in description_lower or "rn" in description_lower or
        "lpn" in description_lower or "lvn" in description_lower or
        "clinic" in description_lower or "клиник" in description_lower or
        "medical assistant" in description_lower or "медицинск" in description_lower or
        "pharmacy" in description_lower or "pharmacist" in description_lower or
        "аптек" in description_lower or
        "dental" in description_lower or "dentist" in description_lower or
        "stomatolog" in description_lower or "стоматолог" in description_lower or
        "therapist" in description_lower or "терапевт" in description_lower or
        "biomedical" in description_lower or "bmet" in description_lower or
        "lab tech" in description_lower or "микробиолог" in description_lower or
        "микробиолог" in description_lower or "analytical chemist" in description_lower or
        "химик" in description_lower or
        "healthcare" in description_lower or "здравоохранени" in description_lower):
        return "Healthcare"

    # ---------- Restaurant / Food / Hospitality ----------
    elif ("restaurant" in description_lower or "рестора" in description_lower or
        "cafe" in description_lower or "кафе" in description_lower or
        "barista" in description_lower or "bartender" in description_lower or
        "hostess" in description_lower or "server" in description_lower or
        "waiter" in description_lower or "waitress" in description_lower or
        "line cook" in description_lower or "cook" in description_lower or
        "повар" in description_lower or "кухня" in description_lower or
        "kitchen" in description_lower or "dishwasher" in description_lower or
        "busser" in description_lower or "пицца" in description_lower or
        "pizzeria" in description_lower or "sushi" in description_lower or
        "гостиниц" in description_lower or "hotel" in description_lower or
        "марафон" in description_lower and "hotel" in description_lower):
        return "Restaurant service"

    # ---------- Driving / Delivery / Logistics ----------
    elif ("driver" in description_lower or "drivers" in description_lower or
        "truck" in description_lower or "trucking" in description_lower or
        "дальнобойщик" in description_lower or "грузовик" in description_lower or
        "доставк" in description_lower or "courier" in description_lower or
        "delivery" in description_lower or "fedex" in description_lower or
        "ups" in description_lower or
        "lyft" in description_lower or "uber" in description_lower or
        "car service" in description_lower or "такси" in description_lower or
        "tlc машины" in description_lower or
        "owner-operator" in description_lower or "владелец-оператор" in description_lower):
        return "Driving/Logistics"

    # ---------- Security / Law Enforcement ----------
    elif ("保安" in description or "security" in description_lower or "охран" in description_lower or
        "офицер безопасности" in description_lower or
        "officer" in description_lower and "security" in description_lower or
        "loss prevention" in description_lower or
        "patrol" in description_lower or "patrol officer" in description_lower or
        "armed guard" in description_lower or
        "unarmed guard" in description_lower or
        "police" in description_lower or "офицер полиции" in description_lower):
        return "Security/Law Enforcement"

    # ---------- IT / Tech / Programming ----------
    elif ("software" in description_lower or "программ" in description_lower or
        "developer" in description_lower or "engineer" in description_lower or
        "программист" in description_lower or "coding" in description_lower or
        "программирование" in description_lower or
        "it support" in description_lower or "help desk" in description_lower or
        "cybersecurity" in description_lower or "кибербезопасност" in description_lower or
        "data analyst" in description_lower or "analyst" in description_lower and "data" in description_lower or
        "qa tester" in description_lower or "quality assurance" in description_lower or
        "младший it" in description_lower or
        "начните онлайн-курс по программированию" in description_lower or
        "запишитесь на курс по кодированию" in description_lower):
        return "Technician/Engineer"

    # ---------- Sales / Insurance / Finance ----------
    elif ("业务" in description_lower or "sales" in description_lower or "продаж" in description_lower or
        "менеджер по продажам" in description_lower or
        "telesales" in description_lower or "telemarketer" in description_lower or
        "insurance" in description_lower or "страхован" in description_lower or
        "life insurance" in description_lower or
        "финансовый менеджер" in description_lower or
        "financial advisor" in description_lower or "финансовый консультант" in description_lower or
        "real estate" in description_lower or "недвижимост" in description_lower or
        "broker" in description_lower or "риэлтор" in description_lower or
        "mortgage" in description_lower or "ипотек" in description_lower):
        return "Sales/Insurance/Finance"

    # ---------- Admin / Office / Clerical ----------
    elif ("office manager" in description_lower or "офис-менеджер" in description_lower or
        "secretary" in description_lower or "секретар" in description_lower or
        "administrative assistant" in description_lower or
        "административный помощник" in description_lower or
        "receptionist" in description_lower or "front desk" in description_lower or
        "клерк" in description_lower or "офис" in description_lower and "assistant" in description_lower):
        return "Admin/Office"

    # ---------- Education / Tutoring / Instruction ----------
    elif ("teacher" in description_lower or "учитель" in description_lower or
        "instructor" in description_lower or "инструктор" in description_lower or
        "tutor" in description_lower or "репетитор" in description_lower or
        "professor" in description_lower or "преподаватель" in description_lower or
        "школа" in description_lower or "school" in description_lower or
        "after school" in description_lower or "послешкольн" in description_lower or
        "инструктор по вождени" in description_lower or
        "dance instructor" in description_lower or "инструктор по танцам" in description_lower):
        return "Education"

    # ---------- Research Studies / Focus Groups / Clinical Trials ----------
    elif ("focus group" in description_lower or "фокус-группа" in description_lower or
        "участники для платной фокус-группы" in description_lower or
        "clinical study" in description_lower or "клиническое исследование" in description_lower or
        "участники исследования" in description_lower or
        "платное исследование" in description_lower or
        "research study" in description_lower or
        "opinio" in description_lower and "research" in description_lower or
        "исследование депрессии" in description_lower or
        "исследование диабета" in description_lower or
        "участие в исследовании" in description_lower):
        return "Research/Study"

    # ---------- Arts / Music / Media / Content ----------
    elif ("гитарист" in description_lower or "барабанщик" in description_lower or
        "vocalist" in description_lower or "вокалист" in description_lower or
        "musician" in description_lower or "music video" in description_lower or
        "группа" in description_lower and ("рок" in description_lower or "джаз" in description_lower) or
        "video editor" in description_lower or "видеооператор" in description_lower or
        "videographer" in description_lower or
        "content creator" in description_lower or "создатель контента" in description_lower or
        "social media" in description_lower or "социальных сетей" in description_lower or
        "smm" in description_lower or
        "voice over" in description_lower or "закадрового голоса" in description_lower or
        "artist" in description_lower or "художник" in description_lower or
        "caricaturist" in description_lower or "карикатурист" in description_lower):
        return "Arts/Music/Media"

    # ---------- Legal / Law / Paralegal ----------
    elif ("юридическ" in description_lower or "legal" in description_lower or
        "paralegal" in description_lower or
        "public defender" in description_lower or "окружной советник" in description_lower or
        "law firm" in description_lower or "юридическая фирма" in description_lower or
        "attorney" in description_lower or "адвокат" in description_lower):
        return "Legal"

    # ---------- Pet / Animal Care ----------
    elif ("ветеринар" in description_lower or "veterinary" in description_lower or
        "pet sitter" in description_lower or "нянь для домашних животных" in description_lower or
        "выгульщик собак" in description_lower or "дрессировщик" in description_lower or
        "animal shelter" in description_lower or "приют для животных" in description_lower):
        return "Pet/Animal Care"

    # ---------- Adult / Companionship / Modeling-ish ----------
    # (use this cautiously – mostly for very explicit "работа для девушек" style ads)
    elif (("работа для девушек" in description_lower or
         "работа для девочек" in description_lower or
         "работа для девушек с высоким доходом" in description_lower or
         "ищу девушку для приятного времяпровождения" in description_lower or
         "ищу музу" in description_lower or
         "фильмы для взрослых" in description_lower or
         "adult film" in description_lower or
         "escort" in description_lower)):
        return "Escort"


    return job_type

if __name__ == "__main__":
    path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df.csv"
    df = pd.read_csv(path)
    df = df[~df["job_description"].isna() & (df["job_description"].str.strip() != "")]
    locations = df["location"].tolist()
    jd = df["job_description"].tolist()
    job_type = df["job type"].tolist()
    doamin = df["domain"].tolist()  
    gender_pref = []
    count_missing = 0
    count_unknown = 0
    all = 0
    

    for i in range(len(locations)):
        gender_pref.append(get_gender_preference(jd[i]))

        #if pd.isna(jd[i]) or jd[i].strip() == "":
        #    continue
        all += 1
        if pd.isna(locations[i]) or locations[i].strip() == "" or "other" in locations[i].lower()  or "其他" in locations[i]:
            description = jd[i].replace("联系时请一定说明是在洛杉矶华人资讯网看到的，谢谢！", "").replace("联系时请一定说明是在西雅图华人资讯网看到的，谢谢", "").replace("联系时请一定说明是在大华府华人资讯网看到的，谢谢", "")
            states = get_state(description)
            states2 = list(set(states))
            if len(states) == 0:
                locations[i] = ""
            else:

                locations[i] = ", ".join(states2)
            #if state == "":
                #with open("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/missing_states.txt", "a", encoding="utf-8") as f:
                #    f.write(description + "\n")
                #count_missing += 1
        if job_type[i] == "Manicure":
            job_type[i] = "Salon/Spa"
        if job_type[i] == "Cook":
            job_type[i] = "Restaurant service"
        if job_type == "Clinic":
            job_type[i] = "Healthcare"
        if job_type == "Tutor":
            job_type[i] = "Education"
        if job_type[i] =="Video/photography Production":
            job_type[i] = "Arts/Music/Media"
        if pd.isna(job_type[i]) or job_type[i].strip() == "" or "其他" in job_type[i] or "Other" in job_type[i]:
            # Debug: check if this description contains 美
            label = label_job_type(jd[i])
            job_type[i] = label
            if label == "Other":
                count_unknown += 1
                with open("/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/unknown_job_types.txt", "a", encoding="utf-8") as f:
                    f.write(jd[i] + "\n")
        if job_type[i] == "Finance/Insurance" or job_type[i] == "Sales":
            job_type[i] = "Sales/Insurance/Finance"
        if job_type[i] == "Renovation":
            job_type[i] = "Construction/Skilled Trades"
    df["location"] = locations
    df["gender preference"] = gender_pref
    df["job type"] = job_type
    output_path = "/Users/d22admin/Documents/human-trafficking/ContentAnalysis/Data/combined_job_data_df_2.0.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print("Total with job description:", all)
    print("Count missing location:", count_missing)
    print("Count unknown job type:", count_unknown)