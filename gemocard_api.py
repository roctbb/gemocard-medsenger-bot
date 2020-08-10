from config import *
import requests


def subscribe(login, patient, uid):
    data = {
        "login": login,
        "patient": patient,
        "id": uid
    }

    print("Send to {}: {}".format(GEMOCARD_HOST + '/subscribe', data))

    try:
        try:
            unsubscribe(uid)
        except:
            pass

        answer = requests.post(GEMOCARD_HOST + '/subscribe', json=data)
        print(answer.text)

        if answer.text != "OK":
            print('Answer not OK')
            return False

        return True
    except Exception as e:
        print(e)
        return False


def unsubscribe(uid):
    data = {
        "id": uid,
    }

    print("Send to {}: {}".format(GEMOCARD_HOST + '/unsubscribe', data))

    try:
        answer = requests.post(GEMOCARD_HOST + '/unsubscribe', json=data)
        print(answer.text)

        if answer.text != "OK":
            print('Answer not OK')
            return False

        return True
    except Exception as e:
        print(e)
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