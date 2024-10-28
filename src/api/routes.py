from flask import Flask, request, jsonify, url_for, Blueprint
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from api.models import db, User, TokenBlockedList
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api)

app = Flask(__name__)
bcrypt = Bcrypt(app)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {"message": "Welcome! Please create an account or log into your existing one to continue."}
    return jsonify(response_body), 200

@api.route('/signup', methods=['POST'])
def signup_user():
    body = request.get_json()
    if body['email'] is None:
        return jsonify({"msg":"Por favor ingrese su usuario"}),400
    if body['password'] is None:
        return jsonify({"msg":"Por favor ingrese su contraseña"}), 400
    body['password'] = bcrypt.generate_password_hash(body['password']).decode('utf-8')
    user = User(email=body['email'], password=body['password'], is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"Usuario creado con éxito", "user": user.serialize()})

@api.route("/login", methods=["POST"])
def user_login():
    body = request.get_json()
    if body["email"] is None:
        return jsonify({"msg": "Debe especificar un email"}), 400
    if body["password"] is None:
        return jsonify({"msg": "Debe especificar una contraseña"}), 400
    user = User.query.filter_by(email=body["email"]).first()
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 401
    valid_password = bcrypt.check_password_hash(user.password, body["password"])
    if not valid_password:
        return jsonify({"msg": "Clave inválida"}), 401
    token = create_access_token(identity=user.id, additional_claims={"role": "admin"})
    return jsonify({"token": token})

@api.route("/private", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.serialize()), 200

@api.route("/logout", methods=["POST"])
@jwt_required()
def user_logout():
    token_data = get_jwt()
    token_blocked = TokenBlockedList(jti=token_data["jti"])
    db.session.add(token_blocked)
    db.session.commit()
    return jsonify({"msg":"Session cerrada"}), 200
