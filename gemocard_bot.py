from flask import Flask, request, render_template
import json
import datetime
from config import *
import gemocard_api
from medsenger_api import AgentApiClient
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import timezone

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)

app = Flask(__name__)
db_string = "postgres://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
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


try:
    db.create_all()
except:
    print('cant create structure')


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
            if data.get('params', {}).get('gemocard_login'):
                contract.login = data['params']['gemocard_login']

            contract.patient = 0
            if data.get('params', {}).get('gemocard_patient'):
                try:
                    contract.patient = int(data.get('params', {}).get('gemocard_patient'))
                except:
                    pass


        if contract.login and contract.patient:
            if gemocard_api.subscribe(contract.login, contract.patient, contract.uuid):
                print(gts(), "Subscribed {}".format(contract.uuid))
            else:
                print(gts(), "Not subscribed {}".format(contract.uuid))

        medsenger_api.add_record(data.get('contract_id'), 'doctor_action',
                                 'Подключен прибор "Гемокард" (логин {}).'.format(contract.login))

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

            if contract.login and contract.patient:
                if gemocard_api.unsubscribe(contract.uuid):
                    print("{}: Unsubscribed {}".format(gts(), contract.uuid))
                else:
                    print("{}: Not unsubscribed {}".format(gts(), contract.uuid))

            print("{}: Deactivate contract {}".format(gts(), contract.id))

            medsenger_api.add_record(data.get('contract_id'), 'doctor_action',
                                     'Отключен прибор "Гемокард" (логин {}).'.format(contract.login))

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

                    medsenger_api.send_message(contract.id, text, only_doctor=True, attachments=[["ecg.pdf", "application/pdf", filedata]])


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
            return "<strong>Ошибка. Контракт не найден.</strong> Попробуйте отключить и снова подключить интеллектуальный агент к каналу консультирвоания.  Если это не сработает, свяжитесь с технической поддержкой."

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
            contract.patient = int(request.form.get('patient', 0))
            contract.login = request.form.get('login', 0)

            if not contract.login:
                gemocard_api.unsubscribe(contract.uuid)
            elif not gemocard_api.subscribe(contract.login, contract.patient, contract.uuid):
                return render_template('settings.html', contract=contract, error='Логин не найден')
            db.session.commit()
        else:
            return "<strong>Ошибка. Контракт не найден.</strong> Попробуйте отключить и снова подключить интеллектуальный агент к каналу консультирвоания.  Если это не сработает, свяжитесь с технической поддержкой."

    except Exception as e:
        print(e)
        return "error"

    return """
        <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>
        """


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']

    if key != API_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    return "ok"

if __name__ == "__main__":
    app.run(port=PORT, host=HOST)
