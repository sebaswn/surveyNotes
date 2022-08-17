from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify
from flask import Response
from flask import Flask, request, jsonify, make_response
import random
import json
import pytz
import os

app = Flask(__name__)

#https://www.youtube.com/watch?v=cYWiDiIUxQc&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=4
#Database configuraiton
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database structure
class LastUpdate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, nullable = False, default = datetime.now(tz=pytz.utc))
    def __repr__(self):
        return f"Last Update('{self.id}','{self.date}')"
    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'date'  : self.date,
        }


class Sensore(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    marca = db.Column(db.String(40), nullable = False)
    modello = db.Column(db.String(40), nullable = False)
    nrSeriale = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Sensor('{self.id}','{self.marca}','{self.modello}','{self.nrSeriale}')"

    @property
    def serialize(self):
        return {
            'id'    : self.id,
        }

class Stazione(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40), nullable = False)
    location = db.Column(db.Integer, nullable = True)  #https://stackoverflow.com/questions/37233116/point-type-in-sqlalchemy
    tipo = db.Column(db.Integer, nullable = False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensore.id'), nullable = True)
    lastNote = db.Column(db.DateTime, nullable = True)
    avvisi = db.Column(db.Text(100), default = "")
    dismesso = db.Column(db.Boolean, default = False, nullable = False)
    #notes = db.Column(db.Integer, db.ForeignKey('note.id'), nullable = True)
    #notes = db.relationship('Note', backref='note', lazy = True)
    #sensor_id = db.relationship('Sensore', backref='sensore', lazy = True)

    def __repr__(self):
        return f"Stazione('{self.id}','{self.name}','{self.tipo}','{self.location}')"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def serialize(self):
           return {
               'id'         : self.id,
               'name'       : self.name,
               'location'   : self.location,
               'tipo'       : self.tipo,
               'sensor_id'  : self.sensor_id,
               'lastNote'   :self.lastNote,
               'avvisi'     :self.avvisi,
               'dismesso'   :self.dismesso,
           }

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, nullable = False, default =  datetime.now(tz=pytz.utc))
    operatori = db.Column(db.String(40), nullable = False)
    osservazioni = db.Column(db.Text, nullable = True)
    lavoriSvolti = db.Column(db.Text, nullable = True)
    statoAltriSensori = db.Column(db.String(100), nullable = True)
    foto = db.Column(db.String(20), nullable = True)
    stazione_id = db.Column(db.Integer, db.ForeignKey('stazione.id'), nullable = False)

    def __repr__(self):
        return f"Nota('{self.id}','{self.date}','{self.operatori}','{self.lavoriSvolti}')"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'date'    : self.date,
            'operatori'    : self.operatori,
            'osservazioni'    : self.osservazioni,
            'lavoriSvolti'    : self.lavoriSvolti,
            'statoAltriSensori'    : self.statoAltriSensori,
            'foto'    : self.foto,
            'stazione_id'    : self.stazione_id,
        }


class NoteMeteo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable = False)
    statoPluviometro = db.Column(db.String(30), nullable = False)
    malfunzionamenti = db.Column(db.Text, nullable = True)
    calibrazione = db.Column(db.Boolean, default = False, nullable = False)
    calRisoluzione = db.Column(db.Float, nullable = True)
    calVolumeAcqua = db.Column(db.Float, nullable = True)
    calSuperficieBocca = db.Column(db.Float, nullable = True)
    calNozzle = db.Column(db.Float, nullable = True)
    calNoImpulsiDovuti = db.Column(db.Float, nullable = True)
    calNoImpulsiMisurati = db.Column(db.Float, nullable = True)
    calPercentualeErrore = db.Column(db.Float, nullable = True)


    def __repr__(self):
        return f"Nota Meteo ('{self.statoPluviometro}')"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'note_id'    : self.note_id,
            'statoPluviometro'    : self.statoPluviometro,
            'malfunzionamenti'    : self.malfunzionamenti,
            'calRisoluzione'    : self.calRisoluzione,
            'calVolumeAcqua'    : self.calVolumeAcqua,
            'calSuperficieBocca'    : self.calSuperficieBocca,
            'calNozzle'    : self.calNozzle,
            'calNoImpulsiDovuti'    : self.calNoImpulsiDovuti,
            'calNoImpulsiMisurati'    : self.calNoImpulsiMisurati,
            'calPercentualeErrore'    : self.calPercentualeErrore,
            'calibrazione': self.calibrazione,

        }

class NoteDeflussiMinimi(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable = False)
    asta = db.Column(db.Float, nullable = True)
    dl = db.Column(db.Float, nullable = True)
    portata = db.Column(db.Float, nullable = True)
    deflussoRispettato = db.Column(db.String(10), nullable = False)
    batteria = db.Column(db.Float, nullable = True)
    misuraDiPortataStrumento = db.Column(db.String(20), nullable = True)
    misuraDiPortataPortata = db.Column(db.Float, nullable = True)

    def __repr__(self):
        return f"Nota Deflusso Minimo ('{self.portata}')"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @property
    def serialize(self):
        return {
            'id'    : self.id,
        }

class NoteLimnimetri(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable = False)
    asta = db.Column(db.Float, nullable = True)
    dlA = db.Column(db.Float, nullable = True)
    dlB = db.Column(db.Float, nullable = True)
    dlRadar = db.Column(db.Float, nullable = True)
    batteriaA = db.Column(db.Float, nullable = True)
    BatteriaB = db.Column(db.Float, nullable = True)
    misuraDiPortataStrumento = db.Column(db.String(20), nullable = True)
    misuraDiPortataPortata = db.Column(db.Float, nullable = True)
    controlloTemperaturaRiferimento = db.Column(db.Float, nullable = True)
    controlloTemperaturaDLA = db.Column(db.Float, nullable = True)
    controlloTemperaturaDLB = db.Column(db.Float, nullable = True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __repr__(self):
        return f"Nota Deflusso Minimo ('{self.portata}')"

    @property
    def serialize(self):
        return {
            'id'    : self.id,
        }

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/rand")
def hello():
    return str(random.randint(0, 100))

@app.route('/stazioni', methods=['GET'])
def stazioni():
    return jsonify(stazioni=[i.serialize for i in Stazione.query.all()])

@app.route('/stazioni', methods=['POST'])
def addStazione():
    content = request.json

    staz = Stazione(name=content["name"], tipo=content["type"])
    db.session.add(staz)
    db.session.commit()
    setLastUpdate()
    return jsonify(Stazione.query.filter_by(id=staz.id).first().serialize)

@app.route('/sensori', methods=['GET'])
def sensori():
    return jsonify(sensori=[i.serialize for i in Sensore.query.all()])

@app.route('/note', methods=['GET'])
def note():
    return jsonify(note=[i.serialize for i in Note.query.all()])

@app.route('/noteDeflussiMinimi', methods=['GET'])
def noteDeflussiMinimi():
    return jsonify(noteDeflussiMinimi=[i.serialize for i in NoteDeflussiMinimi.query.all()])

@app.route('/noteLimnimetri', methods=['GET'])
def noteLimnimetri():
    return jsonify(noteLimnimetri=[i.serialize for i in NoteLimnimetri.query.all()])

@app.route('/noteMeteo', methods=['GET'])
def noteMeteo():
    return jsonify(noteMeteo=[i.serialize for i in NoteMeteo.query.all()])

@app.route('/noteMeteo', methods=['POST'])
def newNoteMeteo():
    content = request.json
    print('This is the input for the post note meteo', content)
    if('dataToSend' in content):
        content = content["dataToSend"]
    print('This is the input for the post note meteo', content)
    note = Note()
    if ('date' in content["note"]):

        note.date = datetime.strptime(content["note"]["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
        print("NOTE ID ", note.id)
    if('operatori' in content["note"]):
        note.operatori= content["note"]["operatori"]
    if('statoAltriSensori' in content["note"]):
        note.statoAltriSensori = content["note"]["statoAltriSensori"]
    if('osservazioni' in content["note"]):
        note.osservazioni = content["note"]["osservazioni"]
    if('lavoriSvolti' in content["note"]):
        note.lavoriSvolti = content["note"]["lavoriSvolti"]
    if('foto' in content["note"]):
        note.foto = content["note"]["foto"]

    note.stazione_id = content["note"]["stazione_id"]

    staz = Stazione.query.filter_by(id=note.stazione_id).first()
    if(staz.lastNote is None):
        staz.lastNote = datetime.strptime(content["note"]["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
    elif(staz.lastNote < datetime.strptime(content["note"]["date"], '%Y-%m-%dT%H:%M:%S.%fZ')):
        staz.lastNote = datetime.strptime(content["note"]["date"], '%Y-%m-%dT%H:%M:%S.%fZ')

    db.session.add(note)
    db.session.commit()
    print("NOTE ID ", note.id)

    noteMeteo = NoteMeteo(note_id=note.id)
    noteMeteo.statoPluviometro = content["noteMeteo"]["statoPluviometro"]
    if('malfunzionamenti' in content["noteMeteo"]):
        noteMeteo.malfunzionamenti = content["noteMeteo"]["malfunzionamenti"]
    if(content["noteMeteo"]["calibration"] == True):
        noteMeteo.calibrazione = content["noteMeteo"]["calibration"]
        noteMeteo.calRisoluzione = content["noteMeteo"]["calRisoluzione"]
        noteMeteo.calVolumeAcqua = content["noteMeteo"]["calVolumeAcqua"]
        noteMeteo.calSuperficieBocca = content["noteMeteo"]["calSuperficieBocca"]
        noteMeteo.calNozzle = content["noteMeteo"]["calNozzle"]
        noteMeteo.calNoImpulsiDovuti = content["noteMeteo"]["calNoImpulsiDovuti"]
        noteMeteo.calNoImpulsiMisurati = content["noteMeteo"]["calNoImpulsiMisurati"]
        noteMeteo.calPercentualeErrore = content["noteMeteo"]["calPercentualeErrore"]

    db.session.add(note)
    db.session.add(noteMeteo)
    db.session.commit()
    result = {"note": ""}
    result["note"] = ((Note.query.filter_by(id=note.id).first().serialize)) # add temp_result to the final result
    result["noteMeteo"] = ((NoteMeteo.query.filter_by(id=noteMeteo.id).first().serialize)) # add temp_result to the final result

    setLastUpdate()
    return json.dumps(result,indent=4, sort_keys=True, default=str)

@app.route('/avviso', methods=['POST'])
def updateAvviso():
    content = request.json
    print(content)
    staz = Stazione.query.filter_by(id=content["id"]).first()
    staz.avvisi = content["avvisi"]
    db.session.commit()

    setLastUpdate()
    return jsonify(staz.serialize)

@app.route('/lastUpdate', methods=['GET'])
def lastUpdate():
    return jsonify(LastUpdate.query.order_by(LastUpdate.id.desc()).first().serialize)

@app.route('/testOnline', methods=['GET'])
def testOnline():
    return jsonify(True)

@app.route('/lastUpdate', methods=['POST'])
def setLastUpdate():
    update = LastUpdate(date=datetime.now(pytz.utc))
    db.session.add(update)
    db.session.commit()
    return jsonify(lastUpdate=[i.serialize for i in LastUpdate.query.all()])

if __name__ == "__main__":
    #FOR DOCKER
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

    #FOR LOCAL
    #app.run(debug=True)
    #WINDOWS WITH SECURE
    #app.run(debug=True,ssl_context='adhoc')
    #app.run(host="0.0.0.0",ssl_context='adhoc')
