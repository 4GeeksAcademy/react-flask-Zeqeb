"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Blueprint('api', __name__)
#CORS(api)

@api.route('/signup', methods=['POST'])
def signup_user():
    body = request.get_json()
    if not body or 'email' not in body or 'password' not in body or 'username' not in body:
        return jsonify({"msg": "Por favor complete todos los campos"}), 400
    if User.query.filter_by(email=body['email']).first() is not None:
        return jsonify({"msg": "El usuario ya existe"}), 400
    
    hashed_password = bcrypt.generate_password_hash(body['password']).decode('utf-8')
    user = User(email=body['email'], password=hashed_password, is_active=True)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado con éxito", "user": user.serialize()}), 201

@api.route('/login', methods=['POST'])
def user_login():
    body = request.get_json()
    if not body or 'email' not in body or 'password' not in body:
        return jsonify({"msg": "Por favor complete todos los campos"}), 400

    user = User.query.filter_by(email=body['email']).first()
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 401

    valid_user = bcrypt.check_password_hash(user.password, body['password'])
    if not valid_user:
        return jsonify({"msg": "Contraseña inválida"}), 401
    token = create_access_token(identity=user.id, additional_claims={"role": "admin"})

    return jsonify({"msg": "Inicio de sesión exitoso", "token": token}), 200

@api.route("/logout", methods=["POST"])
@jwt_required()
def user_logout():
   token_data=get_jwt()
   token_blocked=TokenBlockedList(jti=token_data["jti"])
   db.session.add(token_blocked)
   db.session.commit()
   return jsonify({"msg":"Session cerrada"})

@api.route('/userinfo', methods=['GET'])
@jwt_required()
def user_info():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "userInfo": user.serialize(),
        "role": "admin"
    }), 200

