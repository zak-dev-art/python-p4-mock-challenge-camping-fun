#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        return jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers])
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            camper = Camper(name=data.get('name'), age=data.get('age'))
            db.session.add(camper)
            db.session.commit()
            return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 201
        except (ValueError, Exception):
            return jsonify({"errors": ["validation errors"]}), 400

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter_by(id=id).first()
    
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    
    if request.method == 'GET':
        return jsonify(camper.to_dict())
    
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 202
        except (ValueError, Exception):
            return jsonify({"errors": ["validation errors"]}), 400

@app.route('/activities', methods=['GET'])
def activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities])

@app.route('/activities/<int:id>', methods=['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter_by(id=id).first()
    
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    db.session.delete(activity)
    db.session.commit()
    return '', 204

@app.route('/signups', methods=['POST'])
def signups():
    data = request.get_json()
    try:
        signup = Signup(
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id'),
            time=data.get('time')
        )
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    except (ValueError, Exception):
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
