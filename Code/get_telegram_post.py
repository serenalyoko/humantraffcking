import json
import pandas as pd
import os
import sqlite3

def get_label(labels):
    if ("job_board" in labels or "social_media" in labels) and ("escort" in labels):
        return "risk"
    else:
        return "safe"
def get_filepath(access_file, jobAdsPaths):
    for path in jobAdsPaths:
        if access_file in path:
            return path
    return None

def get_telegram_key(access_key, all_number_info):
    print(all_number_info)
    with open(all_number_info, "r") as file:
        all_number_data = json.load(file)
    item = all_number_data[access_key]
    telegram_keys = set()
    for i in range(len(item["platform"])):
        if item["platform"][i] == "telegram":
            telegram_keys.add(item["original"][i])
    return telegram_keys
    
def retrieve_telegram(access_file, access_key, retrievePath, all_number_info):
    telegram_keys = get_telegram_key(access_key, all_number_info)
    with open(access_file, "r") as f:
        data = json.load(f)
    for key in telegram_keys:
        channels = data[key]["channel"]
        message_ids = data[key]["message_id"]
        for i in range(len(channels)):
            message_id = message_ids[i]
            dbpath = retrievePath + channels[i]+ ".db"
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Database: {dbpath}")
            for table_name in tables:
                #print(table_name)
                #print(f"Table: {table_name[0]}")
                cursor.execute(f"PRAGMA table_info({table_name[0]});")
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                #print(f"Columns: {column_names}")
                cursor.execute(f"SELECT COUNT(*) FROM {table_name[0]};")
                total_rows = cursor.fetchone()[0]
                #print(f"Total rows in table {table_name[0]}: {total_rows}")
                if 'message_id' in column_names and 'content' in column_names:
                    cursor.execute(f"SELECT content FROM {table_name[0]} WHERE message_id = ?", (message_id,))
                    result = cursor.fetchone()
                    if result:
                        content = result[0]
                        # Now you can 'save' the content. For example, print it:
                        print(f"Found content for message_id {message_id}: {content}")
                        # Or append it to a list to use later.
                print(f"Columns in table {table_name[0]}: {column_names}")
                #rows = cursor.fetchall()
                #for row in rows:
                #    content =row[column_names.index("content")]
        



if __name__ == "__main__":
    retrievePath = "/project2/emiliofe_74/blasurru/telegram/ht_data_distilled/"
    telegram_keyPath = "/scratch1/zhousiyi/human_trafficking/Data/telegram_phone_numbers.json"
    all_number_keyPath = "/scratch1/zhousiyi/human_trafficking/Data/all_number_info.json"
    labelPath = "/scratch1/zhousiyi/human_trafficking/Data/phone_num_network_meta_0825_cleaned_finalized.json"
    all_files = os.listdir(retrievePath)

    with open(labelPath, 'r') as f:
        metadata = json.load(f)
    
    print("start going through phone numbers")
    for phone_number in metadata.keys():
        #print(metadata[phone_number].keys())
        access_files = metadata[phone_number]['access_file']
        access_ids = metadata[phone_number]['access_key']
        #print(phone_number, access_files, access_ids)
        labels = metadata[phone_number]['label']
        label = get_label(labels)
        #print(label)
        print(phone_number)
        for i in range(len(access_files)):
            if "telegram" not in access_files[i]:
                continue
            access_key = access_ids[i]
            retrieve_telegram(telegram_keyPath, access_key, retrievePath, all_number_keyPath)
