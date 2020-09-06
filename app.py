# python3 -m flask db migrate
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

if __name__ == '__main__':
    app.run(debug=False)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@35.240.83.220:5432/insurance"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class WhiteList(db.Model):
    __tablename__ = 'whitelist'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String())

    def __init__(self, domain):
        self.domain = domain

class Agency(db.Model):
    __tablename__ = 'agency'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String())
    title = db.Column(db.String())
    address = db.Column(db.String())

    def __init__(self, domain,title,address):
        self.domain = domain
        self.title = title
        self.address = address

class Broker(db.Model):
    __tablename__ = 'broker'

    id = db.Column(db.Integer, primary_key=True)
    agencyId = db.Column(db.Integer, ForeignKey('agency.id'))
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    address = db.Column(db.String())
    email = db.Column(db.String(), unique= True)

    def __init__(self, agencyId, firstname,lastname,address,email):
        self.agencyId = agencyId
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.email = email

@app.route('/brokers', methods=['GET'])
def brokers():
    if request.method == 'GET':
        brokers = Broker.query.all()
        results = []
        for broker in brokers:
            agency = Agency.query.get_or_404(broker.agencyId)
            result = {
                "id": broker.id,
                "domain": agency.domain,
                "title": agency.title,
                "agencyId": broker.agencyId,
                "firstname": broker.firstname,
                "lastname": broker.lastname,
                "email": broker.email,
                "address": broker.address,
            }
            results.append(result)
        return {"count": len(results), "brokers": results}

@app.route('/signUp', methods=['POST'])
def signUp():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if data['email'] is None or  '@' not in data['email']:
                return "valid email",422
            domain = data['email'].split("@")[1]
            agencyList = Agency.query.filter_by(domain=domain)
            domainList = WhiteList.query.filter_by(domain=domain).first()
            if domainList is None or agencyList is None :
                return "this domain not found",422
            agency = agencyList.order_by(Agency.id).first()
            new_broker = Broker(agencyId=agency.id,firstname=data['firstname'],lastname=data['lastname'],email=data['email'],address=data['address'])
            db.session.add(new_broker)
            db.session.commit()
            return "broker has been created successfully.",200
        else:
            return "The request payload is not in JSON format",404

@app.route('/broker/<broker_id>', methods=['GET'])
def broker(broker_id):
    broker = Broker.query.get_or_404(broker_id)
    agency = Agency.query.get_or_404(broker.agencyId)

    if request.method == 'GET':
        result = {
                "id": broker.id,
                "domain": agency.domain,
                "title": agency.title,
                "agencyId": broker.agencyId,
                "firstname": broker.firstname,
                "lastname": broker.lastname,
                "email": broker.email,
                "address": broker.address,
            }

        return {"broker": result}