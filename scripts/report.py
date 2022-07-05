#!/usr/bin/python3
"""
1. Google Drive Report Feature is temporary stopped for scalability. Feature will be read added once built for scale
"""

"""
import gspread
import sqlite3
import heapq

import pytz as pytz
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from bot264.discord_wrapper import Db, create_server_db
from datetime import datetime

if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv

    load_dotenv()


create_server_db()


def upload_to_google_sheets():
    file_name = os.getenv("GOOGLE_ACCOUNT_KEY_FILE")
    if file_name is None:
        return
    gc = gspread.service_account(filename=file_name)
    sh = gc.open("students")
    database_file = os.getenv("DATABASE")

    history_command = "SELECT * FROM history;"
    student_command = "SELECT * FROM students;"

    con = sqlite3.connect(database_file)
    cur = con.cursor()

    student_header = ["username / name", "number of requests", "time (mins)"]
    student_document = [student_header]
    student_heap = []
    for row in cur.execute(student_command):
        reference = Db.get_name_by_id(row[0], default_value=row[1])
        number_requests = row[2]
        total_duration = row[3] / 60
        copy_row = [reference, number_requests, total_duration]
        heapq.heappush(student_heap, (-total_duration, copy_row))

    while len(student_heap) > 0:
        _, item = heapq.heappop(student_heap)
        student_document.append(item)

    student_worksheet = sh.get_worksheet(0)
    student_worksheet.update('A1', student_document)

    history_header = ["student name", "ta name", "request time", "start time",
                      "session duration", "wait duration"]
    history_document = [history_header]
    for row in cur.execute(history_command):
        student_reference = Db.get_name_by_id(row[1], default_value=row[3])
        ta_reference = Db.get_name_by_id(row[2], default_value=row[4])
        request_time = str(datetime.fromtimestamp(row[5]).astimezone(pytz.timezone("America/Indiana/Indianapolis")))
        start_time = str(datetime.fromtimestamp(row[6]).astimezone(pytz.timezone("America/Indiana/Indianapolis")))
        session_duration = (row[6] - row[5]) / 60
        if (row[6] - row[5]) != row[7]:
            command = f"UPDATE history set total_time={row[6] - row[5]} where id={row[0]}"
            cur.execute(command)
        wait_duration = row[8] / 60
        copy_row = [student_reference, ta_reference, request_time, start_time, session_duration, wait_duration]
        history_document.append(copy_row)
    history_worksheet = sh.get_worksheet(1)
    history_worksheet.update('A1', history_document)

    con.commit()
    cur.close()
    con.close()


scheduler = BlockingScheduler()
upload_to_google_sheets()
scheduler.add_job(upload_to_google_sheets, 'interval', hours=1)
scheduler.start()
"""