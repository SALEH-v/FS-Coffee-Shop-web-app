import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import *
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add('Allow-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Allow-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')

    return response


# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    # print(drinks)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks = Drink.query.all()

    detailed_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': detailed_drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    drink_body = request.get_json()
    if drink_body is None:
        abort(400)

    try:
        title = drink_body.get('title')
        recipe = json.dumps(drink_body.get('recipe'))

        if (title is None) or (recipe is None):
            abort(400)

        drink = Drink(title=title, recipe=recipe)

        drink.insert()


    except Exception as e:
        print(e)
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    drink_body = request.get_json()
    if drink_body is None:
        abort(400)

    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    try:
        title = drink_body.get('title')
        recipe = json.dumps(drink_body.get('recipe'))

        drink.title = title
        drink.recipe = recipe

        drink.update()


    except Exception as e:
        print(e)
        abort(500)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)

    if not drink:
        abort(404)

    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(500)

    return jsonify({
        'success': True,
        'deleted': drink.id
    }), 200


# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "resource not found"
    }), 404


@app.errorhandler(AuthError)
def authError(error):
    errorCode = error.status_code
    messageDescription = error.error['description']

    return jsonify({
        'success': False,
        'error': errorCode,
        'message': messageDescription
    }), 401
