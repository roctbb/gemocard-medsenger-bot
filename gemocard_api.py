from config import *
import requests


def subscribe(login, patient, uid):
    data = {
        "login": login,
        "patient": patient,
        "id": uid
    }

    try:
        requests.post(GEMOCARD_HOST + '/subscribe', json=data)

        return True
    except Exception as e:
        return False


def unsubscribe(uid):
    data = {
        "id": uid,
    }

    try:
        requests.post(GEMOCARD_HOST + '/unsubscribe', json=data)

        return True
    except Exception as e:
        return False

# # Gemocard POST HOST + /subscribe
# {
#     "login": "roctbb",
#     "patient": 0
# }
#
# # Gemocard POST HOST + /unsubscribe
# {
#     "login": "roctbb"
# }
#
# # Medsenger https://medsenger.ru:9105/receive
# {
#     "login": "roctbb",
#     "data": {
#         "systolic": 120,
#         "diastolic": 80,
#         "pulse": 80,
#         # ????
#     }
# }