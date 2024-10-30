from flask import Flask, request, jsonify
from models import db, User, Game
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
db.init_app(app)


# Crearea unui utilizator
@app.route('/user_create', methods=['POST'])
def user_create():
    data = request.json
    username = data.get('username')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(username=username)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created', 'user_id': user.id})


# Începerea unui joc nou
@app.route('/start', methods=['GET'])
def start_game():
    user_id = request.args.get('user_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    game = Game(user_id=user.id)
    db.session.add(game)
    db.session.commit()

    return jsonify({'message': 'Game started', 'game_id': game.id})


# Mutare în joc (piatra, hartie, foarfeca)
@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id')
    user_move = data.get('move')  # 'piatra', 'hartie', 'foarfeca'

    game = Game.query.get(game_id)
    if not game:
        return jsonify({'message': 'Game not found'}), 404

    ai_move = random.choice(['piatra', 'hartie', 'foarfeca'])
    result = determine_winner(user_move, ai_move)

    if result == 'player':
        game.score_player += 1
    elif result == 'ai':
        game.score_ai += 1

    db.session.commit()

    if game.score_player == 2:
        return jsonify({'message': 'Player won!', 'final_score': {'player': game.score_player, 'ai': game.score_ai}})
    elif game.score_ai == 2:
        return jsonify({'message': 'AI won!', 'final_score': {'player': game.score_player, 'ai': game.score_ai}})

    return jsonify({'message': 'Round played', 'ai_move': ai_move,
                    'current_score': {'player': game.score_player, 'ai': game.score_ai}})


# Funcția care determină câștigătorul
def determine_winner(player_move, ai_move):
    if player_move == ai_move:
        return 'draw'
    if (player_move == 'piatra' and ai_move == 'foarfeca') or \
            (player_move == 'hartie' and ai_move == 'piatra') or \
            (player_move == 'foarfeca' and ai_move == 'hartie'):
        return 'player'
    return 'ai'


if __name__ == "__main__":
    app.run(debug=True)
