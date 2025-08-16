from flask import Blueprint, jsonify, request
from sqlalchemy import select, delete
from models import db, User, Characters, Vehiculo, favorites_table

api = Blueprint("api", __name__)

# Listar todos los personajes
@api.route('/people', methods=['GET'])
def get_people():
    people = Characters.query.all()
    return jsonify([p.serialize() for p in people]), 200

# Obtener un personaje por ID
@api.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Characters.query.get_or_404(people_id)
    return jsonify(person.serialize()), 200

# Listar todos los vehículos
@api.route('/vehiculo', methods=['GET'])
def get_vehiculos():
    vehiculos = Vehiculo.query.all()
    return jsonify([v.serialize() for v in vehiculos]), 200

# Obtener un vehículo por ID
@api.route('/vehiculo/<int:vehiculo_id>', methods=['GET'])
def get_vehiculo(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    return jsonify(vehiculo.serialize()), 200

# Listar todos los usuarios
@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# Listar los favoritos de un usuario
@api.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "Debes proporcionar user_id como parámetro"}), 400

    # Verificamos que el usuario exista
    User.query.get_or_404(user_id)

    favorites = []

    # Favoritos de personajes
    char_rows = db.session.execute(
        select(favorites_table.c.character_id).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.character_id.isnot(None)
        )
    ).scalars().all()
    for char_id in char_rows:
        character = Characters.query.get(char_id)
        if character:
            favorites.append({"type": "people", **character.serialize()})

    # Favoritos de vehículos
    veh_rows = db.session.execute(
        select(favorites_table.c.vehiculo_id).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.vehiculo_id.isnot(None)
        )
    ).scalars().all()
    for veh_id in veh_rows:
        vehiculo = Vehiculo.query.get(veh_id)
        if vehiculo:
            favorites.append({"type": "vehiculo", **vehiculo.serialize()})

    return jsonify(favorites), 200

# Añadir un personaje favorito
@api.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "Falta user_id en el cuerpo"}), 400

    User.query.get_or_404(user_id)
    Characters.query.get_or_404(people_id)

    # Verificar si ya existe ese favorito
    exists = db.session.execute(
        select(favorites_table).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.character_id == people_id
        )
    ).first()

    if not exists:
        db.session.execute(
            favorites_table.insert().values(
                user_id=user_id, character_id=people_id, vehiculo_id=None
            )
        )
        db.session.commit()
        return jsonify({"message": "Personaje añadido a favoritos"}), 201

    return jsonify({"message": "El personaje ya está en favoritos"}), 200

# Añadir un vehículo favorito
@api.route('/favorite/vehiculo/<int:vehiculo_id>', methods=['POST'])
def add_favorite_vehiculo(vehiculo_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "Falta user_id en el cuerpo"}), 400

    User.query.get_or_404(user_id)
    Vehiculo.query.get_or_404(vehiculo_id)

    exists = db.session.execute(
        select(favorites_table).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.vehiculo_id == vehiculo_id
        )
    ).first()

    if not exists:
        db.session.execute(
            favorites_table.insert().values(
                user_id=user_id, character_id=None, vehiculo_id=vehiculo_id
            )
        )
        db.session.commit()
        return jsonify({"message": "Vehículo añadido a favoritos"}), 201

    return jsonify({"message": "El vehículo ya está en favoritos"}), 200

# Eliminar un personaje favorito
@api.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "Falta user_id en el cuerpo"}), 400

    # Verificamos que el usuario y el personaje existen
    User.query.get_or_404(user_id)
    Characters.query.get_or_404(people_id)

    result = db.session.execute(
        delete(favorites_table).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.character_id == people_id
        )
    )
    if result.rowcount > 0:
        db.session.commit()
        return jsonify({"message": "Personaje eliminado de favoritos"}), 200

    return jsonify({"error": "Personaje no encontrado en favoritos"}), 404

# Eliminar un vehículo favorito
@api.route('/favorite/vehiculo/<int:vehiculo_id>', methods=['DELETE'])
def delete_favorite_vehiculo(vehiculo_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "Falta user_id en el cuerpo"}), 400

    User.query.get_or_404(user_id)
    Vehiculo.query.get_or_404(vehiculo_id)

    result = db.session.execute(
        delete(favorites_table).where(
            favorites_table.c.user_id == user_id,
            favorites_table.c.vehiculo_id == vehiculo_id
        )
    )
    if result.rowcount > 0:
        db.session.commit()
        return jsonify({"message": "Vehículo eliminado de favoritos"}), 200

    return jsonify({"error": "Vehículo no encontrado en favoritos"}), 404
