from flask import Flask, request, render_template, abort, jsonify
import json
import datetime
from config import *
import gemocard_api
from medsenger_api import AgentApiClient, prepare_binary
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)

app = Flask(__name__)
db_string = "postgresql://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
db = SQLAlchemy(app)


def gts():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    login = db.Column(db.String(255), default='')
    patient = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(255), default='')
    device_type = db.Column(db.String(32), default='gsm')


try:
    db.create_all()
except:
    print('cant create structure')


def send_init_message(contract):
    answer = medsenger_api.get_agent_token(contract.id)
    medsenger_api.send_message(contract.id,
                               'Если у вас есть тонометр Гемодин / Гемокард, данные от давлении и ЭКГ могут '
                               'автоматически поступать врачу. Для этого Вам нужно скачать приложение '
                               '<strong>Medsenger АКСМА</strong>, а затем нажать на кнопку "Подключить тонометр" ниже.',
                               action_link=f"https://gemocard.medsenger.ru/app?agent_token={answer.get('agent_token')}&"
                                           f"contract_id={contract.id}&type=connect",
                               action_type='url', action_name='Подключить тонометр')


@app.route('/status', methods=['POST'])
def status():
    data = request.json

    if data['api_key'] != API_KEY:
        return 'invalid key'

    contract_ids = [l[0] for l in db.session.query(Contract.id).filter_by(active=True).all()]

    answer = {
        "is_tracking_data": True,
        "supported_scenarios": ['heartfailure', 'stenocardia', 'fibrillation'],
        "tracked_contracts": contract_ids
    }
    print(answer)

    return json.dumps(answer)


@app.route('/order', methods=['POST'])
def order():
    data = request.json

    if data['api_key'] != API_KEY:
        print('invalid key')
        return 'invalid key'

    if data.get('order') in ('gemocard_request_pressure', 'gemocard_request_ecg', 'gemocard_request_pressure_ecg'):
        try:
            contract_id = data['contract_id']
            query = Contract.query.filter_by(id=contract_id, active=True)

            if query.count() != 0:
                agent_token = medsenger_api.get_agent_token(contract_id)

                if data.get('order') == 'gemocard_request_ecg':
                    link = f"https://gemocard.medsenger.ru/app?contract_id={contract_id}&" \
                           f"agent_token={agent_token.get('agent_token')}&type=ecg"
                    medsenger_api.send_message(contract_id,
                                               "Пожалуйста, сделайте ЭКГ с помощью тонометра Гемокард в приложении и "
                                               "отправьте результат врачу.",
                                               link, "Сделать ЭКГ", only_patient=True, action_type="url")
                elif data.get('order') == 'gemocard_request_pressure_ecg':
                    link = f"https://gemocard.medsenger.ru/app?contract_id={contract_id}&" \
                           f"agent_token={agent_token.get('agent_token')}&type=pressure_ecg"
                    medsenger_api.send_message(contract_id,
                                               "Пожалуйста, сделайте ЭКГ с измерением давления с помощью тонометра "
                                               "Гемокард в приложении и отправьте результат врачу.",
                                               link, "Сделать ЭКГ с измерением давления", only_patient=True,
                                               action_type="url")
                else:
                    link = f"https://gemocard.medsenger.ru/app?contract_id={contract_id}&" \
                           f"agent_token={agent_token.get('agent_token')}&type=pressure"
                    medsenger_api.send_message(contract_id,
                                               "Пожалуйста, измерьте давление с помощью тонометра Гемодин / Гемокард "
                                               "в приложении и отправьте результат врачу.",
                                               link, "Измерить давление", only_patient=True, action_type="url")
                return 'ok'
            else:
                print('contract not found')

        except Exception as e:
            print(e)
        return "error"

    return "not supported"


@app.route('/init', methods=['POST'])
def init():
    data = request.json

    if data['api_key'] != API_KEY:
        return 'invalid key'

    try:
        contract_id = int(data['contract_id'])
        query = Contract.query.filter_by(id=contract_id)
        if query.count() != 0:
            contract = query.first()
            contract.active = True

            print("{}: Reactivate contract {}".format(gts(), contract.id))
        else:
            contract = Contract(id=contract_id, uuid=str(uuid4()))
            db.session.add(contract)

            print("{}: Add contract {}".format(gts(), contract.id))

        if 'params' in data:
            if data.get('params', {}).get('gemocard_device_type', '') == 'bluetooth' or data.get('params', {}).get(
                    'gemocard_bluetooth', ''):
                print(gts(), "Device type set to bluetooth for {}".format(contract.uuid))
                contract.device_type = 'bluetooth'

            if data.get('params', {}).get('gemocard_login'):
                contract.login = data['params']['gemocard_login']

            contract.patient = 0
            if data.get('params', {}).get('gemocard_patient'):
                try:
                    contract.patient = int(data.get('params', {}).get('gemocard_patient'))
                except:
                    pass

        if contract.login:
            if contract.device_type == 'bluetooth':
                try:
                    gemocard_api.unsubscribe(contract.uuid)
                except:
                    pass
            else:
                if gemocard_api.subscribe(contract.login, contract.patient, contract.uuid):
                    print(gts(), "Subscribed {}".format(contract.uuid))
                else:
                    print(gts(), "Not subscribed {}".format(contract.uuid))

        medsenger_api.add_record(data.get('contract_id'), 'doctor_action',
                                 'Подключен прибор "Гемокард / Гемодин" (логин {}).'.format(contract.login))

        if contract.device_type == 'bluetooth':
            send_init_message(contract)
        db.session.commit()

    except Exception as e:
        print(e)
        return "error"

    print('sending ok')
    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    data = request.json

    if data['api_key'] != API_KEY:
        print('invalid key')
        return 'invalid key'

    try:
        contract_id = str(data['contract_id'])
        query = Contract.query.filter_by(id=contract_id)

        if query.count() != 0:
            contract = query.first()
            contract.active = False
            db.session.commit()

            if contract.login:
                if gemocard_api.unsubscribe(contract.uuid):
                    print("{}: Unsubscribed {}".format(gts(), contract.uuid))
                else:
                    print("{}: Not unsubscribed {}".format(gts(), contract.uuid))

            print("{}: Deactivate contract {}".format(gts(), contract.id))

            medsenger_api.add_record(data.get('contract_id'), 'doctor_action',
                                     'Отключен прибор "Гемокард / Гемодин" (логин {}).'.format(contract.login))

        else:
            print('contract not found')

    except Exception as e:
        print(e)
        return "error"

    return 'ok'


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/receive', methods=['POST'])
def receive():
    data = request.json
    print("{}: Got {}".format(gts(), data))

    uid = data.get('id', '')
    rec_type = data.get('dataType', 'adRec')

    if uid:

        contract = Contract.query.filter_by(uuid=uid).first()

        if contract:

            date = data.get('data', {}).get('date')
            if date:
                timestamp = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
                timestamp += datetime.timedelta(hours=3)
                timestamp = timestamp.timestamp()
            else:
                timestamp = None

            if rec_type == 'adRec':
                print("Got ad")
                systolic_pressure = data.get('data', {}).get('systolic')
                diastolic_pressure = data.get('data', {}).get('diastolic')
                pulse = data.get('data', {}).get('pulse')

                medsenger_api.add_records(contract.id, [
                    ['systolic_pressure', systolic_pressure, {}],
                    ['diastolic_pressure', diastolic_pressure, {}],
                    ['pulse', pulse, {}],
                ], timestamp, {})

            if rec_type == 'ecgRec':
                print("Got ecg")

                text = data.get('data', {}).get('conclusion', {}).get('text', '')
                filedata = data.get('data', {}).get('fileData')

                if filedata:

                    if text:
                        text = "Заключение ЭКГ: {}".format(text)
                        medsenger_api.add_record(contract.id, "information", text)

                    medsenger_api.send_message(contract.id, text, only_doctor=True,
                                               attachments=[["ecg.pdf", "application/pdf", filedata]])

        else:
            print("Contract {} not found!".format(uid))
    else:
        print("Contract {} not found!".format(uid))

    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    key = request.args.get('api_key', '')

    if key != API_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    try:
        contract_id = int(request.args.get('contract_id'))
        query = Contract.query.filter_by(id=contract_id)
        if query.count() != 0:
            contract = query.first()
        else:
            return "<strong>Ошибка. Контракт не найден.</strong> Попробуйте отключить и снова подключить " \
                   "интеллектуальный агент к каналу консультирования.  Если это не сработает, свяжитесь с " \
                   "технической поддержкой."

    except Exception as e:
        print(e)
        return "error"

    return render_template('settings.html', contract=contract, error='')


@app.route('/settings', methods=['POST'])
def setting_save():
    key = request.args.get('api_key', '')

    if key != API_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    try:
        contract_id = int(request.args.get('contract_id'))
        query = Contract.query.filter_by(id=contract_id)

        if query.count() != 0:
            # TODO: check login
            contract = query.first()

            if contract.device_type == 'bluetooth' and request.form.get('device_type') == 'gsm':
                contract.device_type = 'gsm'
                db.session.commit()
                return render_template('settings.html', contract=contract)
            elif contract.device_type == 'gsm' and request.form.get('device_type') == 'bluetooth':
                contract.device_type = 'bluetooth'
                gemocard_api.unsubscribe(contract.uuid)
                contract.login = ''
                send_init_message(contract)
            else:
                contract.patient = int(request.form.get('patient', 0))
                contract.login = request.form.get('login', '')

            if not contract.login:
                gemocard_api.unsubscribe(contract.uuid)
            elif not gemocard_api.subscribe(contract.login, contract.patient, contract.uuid):
                return render_template('settings.html', contract=contract, error='Логин не найден')
            db.session.commit()
        else:
            return "<strong>Ошибка. Контракт не найден.</strong> Попробуйте отключить и снова подключить " \
                   "интеллектуальный агент к каналу консультирования.  Если это не сработает, свяжитесь с " \
                   "технической поддержкой."

    except Exception as e:
        print(e)
        return "error"

    return """
    <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>
        """


@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json

    if not data:
        abort(422, "No json")

    contract_id = data.get('contract_id')

    if not contract_id:
        abort(422, "No contract_id")

    contract = Contract.query.filter_by(id=contract_id).first()
    if not contract or not contract.active:
        abort(422, "Contract not found")

    agent_token = data.get('agent_token')
    if not agent_token:
        abort(422, "No agent_token")

    answer = medsenger_api.get_agent_token(contract_id)

    if not answer or answer.get('agent_token') != agent_token:
        abort(422, "Incorrect token")

    medsenger_api.send_message(contract.id,
                               "Тонометр успешно подключен. Чтобы отправить давление или ЭКГ врачу, включите тонометр, "
                               "зайдите в приложение Medsenger Аксма и сделайте измерение.")
    return "ok"


@app.route('/api/receive', methods=['POST'])
def receive_data_from_app():
    data = request.json

    if not data:
        abort(422, "No json")

    contract_id = data.get('contract_id')

    if not contract_id:
        abort(422, "No contract_id")

    agent_token = data.get('agent_token')
    if not agent_token:
        abort(422, "No agent_token")

    timestamp = int(data.get('timestamp'))
    if not agent_token:
        abort(422, "No timestamp")

    answer = medsenger_api.get_agent_token(contract_id)

    if not answer or answer.get('agent_token') != agent_token:
        abort(422, "Incorrect token")

    if 'measurement' in data:
        package = []
        for category_name, value in data['measurement'].items():
            package.append((category_name, value))
        medsenger_api.add_records(contract_id, package, timestamp)
        return "ok"
    else:
        abort(422, "No measurement")


@app.route('/api/receive_ecg', methods=['POST'])
def receive_ecg():
    contract_id = request.form.get('contract_id')

    if not contract_id:
        abort(422, "No contract_id")

    agent_token = request.form.get('agent_token')

    if not agent_token:
        abort(422, "No agent_token")

    answer = medsenger_api.get_agent_token(contract_id)

    if not answer or answer.get('agent_token') != agent_token:
        abort(422, "Incorrect token")

    if 'ecg' in request.files:
        file = request.files['ecg']
        filename = file.filename
        data = file.read()

        if not filename or not data:
            abort(422, "No filename")
        else:
            medsenger_api.send_message(contract_id, "Результаты снятия ЭКГ.", send_from='patient', need_answer=True,
                                       attachments=[prepare_binary(filename, data)])
            return 'ok'

    else:
        abort(422, "No file")


@app.route('/api/receive_ecg', methods=['GET'])
def receive_ecg_test():
    return """
    <form method="POST" enctype="multipart/form-data">
        contract_id <input name="contract_id"><br>
        agent_token <input name="agent_token"><br>
        ecg <input name="ecg" type="file"><br>
        <button>go</button>
    </form>
    """


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']

    if key != API_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    return "ok"


@app.route('/app', methods=['GET'])
def app_page():
    return render_template('get_app.html')


@app.route('/.well-known/apple-app-site-association')
def apple_deeplink():
    return jsonify(
        {"applinks": {"apps": [], "details": [{"appID": "CRF22TKXX5.ru.medsenger.gemocard", "paths": ["*"]}]}})


@app.route('/.well-known/assetlinks.json')
def android_deeplink():
    return jsonify([
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "ru.medsenger.acsma",
                "sha256_cert_fingerprints":
                    ["2D:70:5C:6F:C7:C7:CE:E1:2C:79:3B:F9:BE:EB:C9:7F:E8:9A:D1:C0:7D:CC:9D:80:93:01:2D:51:EA:3F:FA:57"]
            }
        }
    ])


if __name__ == "__main__":
    app.run(port=PORT, host=HOST)
