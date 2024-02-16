from flask import Flask, render_template, request, redirect

app = Flask(__name__)

cursor = 'X'
hit = 'HIT'
miss = 'MISS'

# Memory
positions = []
shots = []
ships = []
available_ships = {4:1, 3:2, 2:3, 1:4}
active_ships_count = {4: 0, 3: 0, 2: 0, 1: 0} 
ships_required_count = {4: 1, 3: 2, 2: 3, 1: 4} 

# Display
positionsDisplay = [ ['','A','B','C','D','E','F','G','H','I','J'], 
    [1,0,0,0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,0,0,0,0,0],
    [4,0,0,0,0,0,0,0,0,0,0],
    [5,0,0,0,0,0,0,0,0,0,0],
    [6,0,0,0,0,0,0,0,0,0,0],
    [7,0,0,0,0,0,0,0,0,0,0],
    [8,0,0,0,0,0,0,0,0,0,0],
    [9,0,0,0,0,0,0,0,0,0,0],
    [10,0,0,0,0,0,0,0,0,0,0],
    ]
shotsDisplay = [ ['','A','B','C','D','E','F','G','H','I','J'], 
    [1,0,0,0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,0,0,0,0,0],
    [4,0,0,0,0,0,0,0,0,0,0],
    [5,0,0,0,0,0,0,0,0,0,0],
    [6,0,0,0,0,0,0,0,0,0,0],
    [7,0,0,0,0,0,0,0,0,0,0],
    [8,0,0,0,0,0,0,0,0,0,0],
    [9,0,0,0,0,0,0,0,0,0,0],
    [10,0,0,0,0,0,0,0,0,0,0],
    ]

active_ships = {length: 0 for length in available_ships}

def is_valid_position(x, y, rotation, ship_size, positionsDisplay):
    # Zakładając, że plansza jest kwadratowa i indeksy zaczynają się od 1
    max_index = len(positionsDisplay) - 1

    try:
        if rotation == 1:  # Left
            if y - ship_size < 1: return False  # Sprawdzenie, czy nie wychodzimy poza lewą krawędź
            for i in range(ship_size):
                if positionsDisplay[x][y - i] != 0 or not is_surrounding_area_free(x, y - i, positionsDisplay):
                    return False

        elif rotation == 2:  # Up
            if x - ship_size < 1: return False  # Sprawdzenie, czy nie wychodzimy poza górną krawędź
            for i in range(ship_size):
                if positionsDisplay[x - i][y] != 0 or not is_surrounding_area_free(x - i, y, positionsDisplay):
                    return False

        elif rotation == 3:  # Down
            if x + ship_size > max_index: return False  # Sprawdzenie, czy nie wychodzimy poza dolną krawędź
            for i in range(ship_size):
                if positionsDisplay[x + i][y] != 0 or not is_surrounding_area_free(x + i, y, positionsDisplay):
                    return False

        elif rotation == 4:  # Right
            if y + ship_size > max_index: return False  # Sprawdzenie, czy nie wychodzimy poza prawą krawędź
            for i in range(ship_size):
                if positionsDisplay[x][y + i] != 0 or not is_surrounding_area_free(x, y + i, positionsDisplay):
                    return False

    except IndexError:
        return False

    return True

def is_surrounding_area_free(x, y, positionsDisplay):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = x + dx, y + dy
            # Pomiń sprawdzanie poza planszą i na oznaczeniach
            if nx < 1 or ny < 1 or nx > len(positionsDisplay) - 1 or ny > len(positionsDisplay[0]) - 1:
                continue
            if positionsDisplay[nx][ny] != 0:
                return False
    return True

def can_add_ship(size):
    if size in available_ships and active_ships[size] < available_ships[size]:
        return True
    return False

def add_ship(x, y, rotation, ship_size, positionsDisplay):
    try:
        if rotation == 1:
            for i in range(ship_size):
               positionsDisplay[x][y - i] = cursor
        elif rotation == 2:
            for i in range(ship_size):
                positionsDisplay[x - i][y] = cursor
        elif rotation == 3:
            for i in range(ship_size):
                positionsDisplay[x + i][y] = cursor
        elif rotation == 4:
            for i in range(ship_size):
                positionsDisplay[x][y + i] = cursor
    except IndexError:  
        return False

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/position', methods=['GET', 'POST'])
def position():
    if active_ships == available_ships:
        return render_template('battlefield.html', positionsDisplay=positionsDisplay, shotsDisplay=shotsDisplay)
    else:
        return render_template('position.html', positionsDisplay=positionsDisplay, shotsDisplay=shotsDisplay)

@app.route('/position/add', methods=['POST'])
def add_position():
    x = int(request.form['x_position'])
    y = int(request.form['y_position'])
    rotation = int(request.form['rotation'])
    ship_size = int(request.form['ship_size'])

    # Sprawdzamy, czy wybrane pole jest puste
    if positionsDisplay[x][y] == 0:
        if can_add_ship(ship_size):
            if is_valid_position(x, y, rotation, ship_size, positionsDisplay):
                add_ship(x, y, rotation, ship_size, positionsDisplay)
                active_ships[ship_size] += 1
                return redirect('/position')
            else:
                return 'There are obstacles in the way!'
        else:
            return 'You used all ships of this type!'
    else:
        return 'Position is already taken!'

    return redirect('/position')


@app.route('/battlefield', methods=['POST'])
def battlefield():
    return render_template('battlefield.html', positionsDisplay=positionsDisplay, shotsDisplay=shotsDisplay)

@app.route('/battlefield/shot', methods=['POST'])
def add_shot():
    if request.method == 'POST':
        shot_data = request.form['shot']
        x, y = map(int, shot_data.split('-'))  # Konwertujemy dane formularza na współrzędne x, y
        if shotsDisplay[x][y] == 0:  # Sprawdzamy, czy wybrane pole jest puste
            shotsDisplay[x][y] = hit  # Zakładamy, że każdy strzał to trafienie (dla uproszczenia)
            shots.append({'x': x, 'y': y})  # Dodajemy strzał do listy
            return redirect('/battlefield')
        else:
            return 'Shot already made in this position!'
    return redirect('/battlefield')


if __name__ == "__main__":
    app.run(debug=True)
