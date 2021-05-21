import os
from typing import List

from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.watch import DocumentChange


def get_db():
    reference = os.getenv('REFERENCE', None)
    if reference is None:
        return None
    return firestore.Client().collection(u'servers').document(reference).collection('queueup-bot')


class FbDb:
    db: firestore.DocumentReference = None
    snapshot: firestore.Watch = None

    @staticmethod
    def init():
        FbDb.db = get_db()

    @staticmethod
    def on_request(item):
        print(item)

    @staticmethod
    def on_snapshot(document_snapshot, changes: List[DocumentChange], read_time):
        for doc in document_snapshot:
            to_dict = doc.to_dict()
            if to_dict and 'requests' in to_dict:
                FbDb.on_request(to_dict['requests'])

    @staticmethod
    def listen():
        if not FbDb.db:
            return
        FbDb.snapshot = FbDb.db.on_snapshot(FbDb.on_snapshot)

    @staticmethod
    def kill():
        if FbDb.snapshot:
            # FbDb.snapshot.close()
            FbDb.snapshot = None
