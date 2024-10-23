import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from api.utils import APIException, generate_sitemap
from api.models import db, User, Favorites
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import JWTManager


ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["JWT_SECRET_KEY"] = os.getenv("ARNALDO_BIRTHDAY")
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    token_blocked=TokenBlockedList.query.filter_by(jti=jwt_payload["jti"]).first()
    return token is not None



# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# Agregar administrador y comandos
setup_admin(app)
setup_commands(app)

# Registrar el blueprint de la API
app.register_blueprint(api, url_prefix='/api')

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # Evitar caché
    return response

@app.route('/user/<int:user_id>', methods=["GET"])
def get_user_by_id(user_id):
    user=User.query.get(user_id)
    favorites=Favorites.query.filter_by(user_id=user_id).all()
    print(favorites)
    return jsonify(user.serialize())

@app.route('/favorites/<int:favorite_id>', methods=["GET"])
def get_favorite_by_id(favorite_id):
    favorite=Favorites.query.get(favorite_id)
    print(favorite.user.serialize())
    favorite_dict= favorite.serialize()
    return jsonify({"msg": "OK"})


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
