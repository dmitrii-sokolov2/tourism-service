from flask import Blueprint, request, jsonify, abort
from services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        abort(400, description="JSON body required")

    user = register_user(data)

    return jsonify({"message": "user has been created", "data": user}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        abort(400, description="JSON body required")

    result = login_user(
        data["email"].lower(),
        data["password"]
    )

    return jsonify(result), 200