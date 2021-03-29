import os
import json


def process_rooms():
    rooms = os.getenv("ROOMS", "{}")
    raw_rooms_dict = json.loads(rooms)
    return {int(k): int(v) for k, v in raw_rooms_dict.items()}


class Permissions:
    rooms = process_rooms()

    @staticmethod
    def user_enter_video_channel(author):
        pass
