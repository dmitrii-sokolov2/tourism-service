from flask import Blueprint, request, jsonify
from services.auth_service import register_user, login_user
from schemes.user import UserRegisterSchema
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return {"error": "No data"}, 400

    try:
        user_data = UserRegisterSchema(**data)
        result = register_user(user_data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"message": "User has been created", "data": result}), 201 #or jsonify(result)
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data"}), 400

    try:
        result = login_user(
            data["email"],
            data["password"]
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 401