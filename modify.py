import sqlite3
from datetime import date, datetime, timedelta
from random import randint
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET

from orjson import loads, dumps

PETS_FRUIT = [
    1000,
    1000,
    1000,
    10,
    1000,
    5000,
    10000,
    15000,
    20000,
    50000
]

def run_modify(
        target_level: int = 5,
        pets: str = "",
        fruit: int = "-1",
        custom_bg: int = 0,
        random_f: bool = False,
        column: bool = True,
        full: bool = False,
        toggle_rate: int = 10,
        error_rate: int = 15
    ) -> int:
    db = sqlite3.connect("wordcool_user.db")
    cursor = db.cursor()

    dt = [1, 2, 4, 8, 14]
    e = [1, 2, 4, 8, 16]
    
    start_date = date(2023, 3, 1)
    start_datetime = datetime.combine(start_date, datetime.now().time())

    target_date: date = datetime.now().date()

    if type(target_date) == str:
        target_date = datetime.strptime(target_date, "%Y%m%d").date()
    if type(target_level) == str:
        target_level = int(target_level) - 1

    total_days = (target_date - start_date).days + 1

    farms = [0] * 5 + list(range(1, 96))

    if full:
        pre_day_farm = 100 // (total_days - 30)
        farms = []
        for i in range((total_days - 30)):
            farms += [i] * (pre_day_farm + (i % 3))
        empty_num = 100 - len(farms)
        if empty_num > 0:
            farms += [total_days - 31] * empty_num
        farms = farms[:100]
    elif random_f:
        farms.sort(key=lambda x: randint(1, 1000))
    elif column:
        new_farms = []
        for i in range(100):
            new_farms.append(farms[5 * (i % 20) + (i // 20)])
        farms = new_farms
    else:
        farms = list(map(lambda farm: max(0, farm + randint(-2, 2)), farms))

    # 登入紀錄
    days_str = ["1"] * total_days
    for i in range(5):
        s = randint(0, total_days - 1)
        for j in range(s, s + randint(1, 3)):
            days_str[j] = "0"
    days_str = "".join(days_str)
    if cursor.execute("SELECT * FROM User WHERE key='loginDays'").fetchone():
        cursor.execute("UPDATE 'User' SET 'value'=? WHERE key='loginDays'", (days_str,))
    else:
        cursor.execute("INSERT INTO 'User' ('key', 'value') VALUES ('loginDays', ?)", (days_str,))

    # 註冊日期
    if cursor.execute("SELECT * FROM User WHERE key='startDate'").fetchone():
        cursor.execute("UPDATE 'User' SET 'value'='2023/03/01' WHERE key='startDate'")
    else:
        cursor.execute("INSERT INTO 'User' ('key', 'value') VALUES ('startDate', '2023/03/01')")

    # 顯示教學
    if cursor.execute("SELECT * FROM User WHERE key='hasShowStartIntro'").fetchone():
        cursor.execute("UPDATE 'User' SET 'value'='1' WHERE key='hasShowStartIntro'")
    else:
        cursor.execute("INSERT INTO 'User' ('key', 'value') VALUES ('hasShowStartIntro', '1')")

    # 起始果園
    if cursor.execute("SELECT * FROM User WHERE key='startOrchardID'").fetchone():
        cursor.execute("UPDATE 'User' SET 'value'=? WHERE key='startOrchardID'", (target_level,))
    else:
        cursor.execute("INSERT INTO 'User' ('key', 'value') VALUES ('startOrchardID', ?)", (target_level,))

    # 果園背景
    bg = ["0"] * 15
    bg[target_level] = str(custom_bg)
    bg = "".join(bg)
    if cursor.execute("SELECT * FROM User WHERE key='orchardSceneBG'").fetchone():
        cursor.execute("UPDATE 'User' SET 'value'=? WHERE key='orchardSceneBG'", (bg,))
    else:
        cursor.execute("INSERT INTO 'User' ('key', 'value') VALUES ('orchardSceneBG', ?)", (bg,))

    # 烏龜紀錄
    cursor.execute("DELETE FROM PetDataRecord")
    pets: list = list(map(int, set(pets)))
    for i in pets:
        cursor.execute("""
            INSERT INTO "PetDataRecord"
            ("db_id", "satiety_val", "reduce_timestamp", "play_num", "play_timestamp", "content", "content_timestamp") VALUES
            (?, "24", ?, "0", "0", "", "0")
        """, (target_level * 100 + i, int((datetime.now() + timedelta(days=30)).timestamp())))

    # 種植紀錄
    cursor.execute("DELETE FROM StatsDataRecord")
    cursor.execute("DELETE FROM PlotDataRecord")
    cursor.execute("DELETE FROM LearningRecord")
    nts = lambda: int(datetime.now().timestamp())

    total_seed = 0
    total_fruit = 0

    pet_double = 8 in pets
    pet_add = 6 in pets
    fruit_offset = 10
    fruit_multiple = 1
    for day in range(total_days):
        seed, water, blue = 0, 0, 0
        ts = lambda x: int((start_datetime + timedelta(days=day+x)).timestamp())

        # 結算前一天 (當天的未收成)
        if pet_double and total_fruit >= 20000:
            pet_double = False
            total_fruit -= PETS_FRUIT[8]
            pets.remove(8)
            fruit_multiple = 2

        if pet_add and total_fruit >= 10000:
            pet_add = False
            total_fruit -= PETS_FRUIT[6]
            pets.remove(6)
            fruit_offset = 12
        total_fruit += fruit_offset * fruit_multiple * total_seed

        for i, farm in enumerate(farms):
            offset = day - farm
            if offset == 0:
                seed += 1
                total_seed += 1
                cursor.execute("""
                    INSERT INTO "PlotDataRecord"
                    ("db_id", "plot_id", "status", "level", "next_water_timestamp", "next_fruit_timestamp", "has_fruit", "speed_up", "fruit_show_timestamp") VALUES
                    (?, ?, "1", "1", ?, "0", "0", "0", "0")
                """, (target_level * 100 + i, i, ts(1)))

                for void in range(10):
                    cursor.execute("""
                        INSERT INTO "LearningRecord"
                        ("id", "is_toggled", "correct_answer", "incorrect_answer", "unsure_answer", "learn_time") VALUES
                        (?, '0', '0', '0', '0', ?);
                    """, (target_level * 1000 + i * 10 + void, nts()))
            elif offset == 30:
                blue += 1
                cursor.execute("""
                    UPDATE "PlotDataRecord"
                    SET status=3, level=7, next_water_timestamp=0
                    WHERE plot_id=?
                """, (i,))
                cursor.execute("""
                    UPDATE "LearningRecord"
                    SET correct_answer=6, learn_time=?
                    WHERE id BETWEEN ? AND ?
                """, (nts(), target_level * 1000 + i * 10, target_level * 1000 + i * 10 + 9))
            elif offset in e:
                water += 1
                ind = e.index(offset)
                cursor.execute("""
                    UPDATE "PlotDataRecord"
                    SET level=?, next_water_timestamp=?
                    WHERE plot_id=?
                """, (ind + 2, ts(dt[ind]), i))
                cursor.execute("""
                    UPDATE "LearningRecord"
                    SET correct_answer=?, learn_time=?
                    WHERE id BETWEEN ? AND ?
                """, (ind + 1, nts(), target_level * 1000 + i * 10, target_level * 1000 + i * 10 + 9))
                # """, (randint(1, 10), nts(), target_level * 1000 + i * 10, target_level * 1000 + i * 10 + 9))
            
            if offset >= 0:
                cursor.execute("""
                    UPDATE "PlotDataRecord"
                    SET next_fruit_timestamp=0, has_fruit=1, fruit_show_timestamp=?, speed_up=?
                    WHERE plot_id=?
                """, (int((datetime.now() - timedelta(hours=1)).timestamp()), fruit_multiple - 1, i))
        
        cursor.execute("""
            INSERT INTO "StatsDataRecord"
            ("date_id", "seed_count", "water_count", "review_count", "blue_count", "session_num", "correct_num", "incorrect_num", "unsure_num") VALUES
            (?, ?, ?, "0", ?, ?, ?, "0", "0");
        """, (start_date.strftime("%Y%m%d"), seed, water, blue, seed+water, water * 10))
        start_date += timedelta(days=1)
    
    for i in range(len(farms) * 10):
        cursor.execute("""
            UPDATE "LearningRecord"
            SET is_toggled=?, incorrect_answer=?
            WHERE id=?
        """, ("1" if randint(0, 99) < toggle_rate else "0", "6" if randint(0, 99) < error_rate else "0", target_level * 1000 + i))

    db.commit()
    cursor.close()
    db.close()

    # 更新字彙果
    fruit = total_fruit - sum(map(lambda pet: PETS_FRUIT[pet], pets)) if fruit == -1 else fruit

    with open("com.EnglishCool.Vocab.v2.playerprefs.xml") as xml_file:
        raw_data = xml_file.read()
    raw_str = ET.fromstring(raw_data).find("string[@name='data']").text

    base_data = ["0"] * 15
    base_data[target_level] = str(max(0, fruit))

    data = loads(unquote(raw_str))
    data["Currency"]["seed"] = "0"
    data["Currency"]["fruit"] = base_data
    new_str = dumps(data).decode("utf-8")
    new_str = quote(new_str)

    with open("com.EnglishCool.Vocab.v2.playerprefs.xml", mode="w") as xml_file:
        xml_file.write(raw_data.replace(raw_str, new_str))
    
    return fruit
