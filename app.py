from flask import Flask, render_template, request, redirect

import random

app = Flask(__name__)

cursor = 'X'
hit = 'HIT'
miss = 'MISS'
maxShots = 20
currentShots = 0
currentShotsAI = 0
currentAI = False
score = 0
AIscore = 0

target_mode = False
target_stack = []
sunk_ships = 0


# Memory
hits_memory = []  
available_ships = {4: 1, 3: 2, 2: 3, 1: 4}
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

positionsDisplayAI = [ ['','A','B','C','D','E','F','G','H','I','J'], 
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

shotsDisplayAI = [ ['','A','B','C','D','E','F','G','H','I','J'], 
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

# Functions

def is_valid_position(x, y, rotation, ship_size, positionsDisplay):
    max_index = len(positionsDisplay) - 1

    # Jeśli statek jest długości 1, wystarczy sprawdzić, czy pole jest wolne
    if ship_size == 1:
        return positionsDisplay[x][y] == 0 and is_surrounding_area_free(x, y, positionsDisplay)

    try:
        if rotation == 1:  # Left
            if y - ship_size < 1: return False  
            for i in range(ship_size):
                if positionsDisplay[x][y - i] != 0 or not is_surrounding_area_free(x, y - i, positionsDisplay):
                    return False

        elif rotation == 2:  # Up
            if x - ship_size < 1: return False 
            for i in range(ship_size):
                if positionsDisplay[x - i][y] != 0 or not is_surrounding_area_free(x - i, y, positionsDisplay):
                    return False

        elif rotation == 3:  # Down
            if x + ship_size > max_index: return False 
            for i in range(ship_size):
                if positionsDisplay[x + i][y] != 0 or not is_surrounding_area_free(x + i, y, positionsDisplay):
                    return False

        elif rotation == 4:  # Right
            if y + ship_size > max_index: return False 
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

def place_ships_for_player():
    for ship_size, quantity in available_ships.items():
        placed_ships = 0
        while placed_ships < quantity:
            x = random.randint(1, len(positionsDisplay) - 1)
            y = random.randint(1, len(positionsDisplay[0]) - 1)
            rotation = random.choice([1, 2, 3, 4])
            if is_valid_position(x, y, rotation, ship_size, positionsDisplay):
                add_ship(x, y, rotation, ship_size, positionsDisplay)
                placed_ships += 1

# AI

def place_ai_ships():
    for ship_size, quantity in available_ships.items():
        placed_ships = 0
        while placed_ships < quantity:
            x = random.randint(1, len(positionsDisplayAI) - 1)
            y = random.randint(1, len(positionsDisplayAI[0]) - 1)
            rotation = random.choice([1, 2, 3, 4])
            if is_valid_position(x, y, rotation, ship_size, positionsDisplayAI):
                add_ship(x, y, rotation, ship_size, positionsDisplayAI)
                placed_ships += 1


def ai_shoots():
    global currentShotsAI, AIscore, shotsDisplayAI, positionsDisplay, target_mode, target_stack, sunk_ships

    for x in range(len(shotsDisplayAI)):
        for y in range(len(shotsDisplayAI[0])):  # Iterujemy po kolumnach w wierszach
            if shotsDisplayAI[x][y] == cursor:  # Jeśli AI widzi kursor
                make_ai_shot(x, y)  # AI strzela w tę pozycję
                currentShotsAI += 1  # Zwiększamy licznik po każdym strzale
                if shotsDisplayAI[x][y] == hit:
                    target_mode = True
                    target_stack.append((x, y))  # Rozpoczęcie śledzenia celu
                return

    # Jeśli AI nie śledzi celu i radar jest naładowany, użyj radaru
    if not target_mode and currentShotsAI >= 3:
        rx, ry = random.randint(1, 10), random.randint(1, 10)
        use_radar(rx, ry, shotsDisplayAI, positionsDisplay)
        currentShotsAI = 0

    # Jeśli AI nie śledzi celu, strzela losowo
    if not target_mode:
        while True:
            x, y = random.randint(1, 10), random.randint(1, 10)
            if shotsDisplayAI[x][y] == 0:
                make_ai_shot(x, y)
                currentShotsAI += 1  # Zwiększamy licznik po każdym strzale
                if shotsDisplayAI[x][y] == hit:
                    target_mode = True
                    target_stack.append((x, y))  # Rozpoczęcie śledzenia celu
                return

    # Jeśli AI nie śledzi celu, strzela losowo
    if not target_mode:
        while True:
            x, y = random.randint(1, 10), random.randint(1, 10)
            if shotsDisplayAI[x][y] == 0:
                make_ai_shot(x, y)
                if shotsDisplayAI[x][y] == hit:
                    target_mode = True
                    target_stack.append((x, y))  # Rozpoczynamy śledzenie nowego celu
                return

    # Tryb "śledzenia celu" - jeśli mamy co najmniej dwa trafienia, dedukujemy kierunek
    if len(target_stack) >= 2:
        x_last, y_last = target_stack[-1]
        x_prev, y_prev = target_stack[-2]
        dx = x_last - x_prev
        dy = y_last - y_prev

        # Próba kontynuowania strzału w tym samym kierunku
        nx = x_last + dx
        ny = y_last + dy
        if 1 <= nx <= 10 and 1 <= ny <= 10 and shotsDisplayAI[nx][ny] == 0:
            make_ai_shot(nx, ny)
            if shotsDisplayAI[nx][ny] == hit:
                target_stack.append((nx, ny))
            else:
                # Otrzymano pudło poza ciągiem trafień - sprawdzenie zatopienia statku
                check_if_sunk(x_last, y_last)
            return
        else:
            # Próba w przeciwnym kierunku
            x_first, y_first = target_stack[0]
            nx = x_first - dx
            ny = y_first - dy
            if 1 <= nx <= 10 and 1 <= ny <= 10 and shotsDisplayAI[nx][ny] == 0:
                make_ai_shot(nx, ny)
                if shotsDisplayAI[nx][ny] == hit:
                    target_stack.insert(0, (nx, ny))
                else:
                    # Otrzymano pudło poza ciągiem trafień w przeciwnym kierunku
                    check_if_sunk(x_first, y_first)
                return

    # Jeśli nie ma wystarczającej liczby trafień lub nie udało się kontynuować w ustalonym kierunku,
    # przechodzimy do przeszukiwania sąsiadów ostatniego trafienia
    while target_stack:
        x, y = target_stack[-1]
        found = False
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= 10 and 1 <= ny <= 10 and shotsDisplayAI[nx][ny] == 0:
                make_ai_shot(nx, ny)
                found = True
                if shotsDisplayAI[nx][ny] == hit:
                    target_stack.append((nx, ny))
                return
        if not found:
            target_stack.pop()

    # Jeśli stos się opróżnił, resetujemy tryb śledzenia i wracamy do losowego strzelania
    target_mode = False
    ai_shoots()

def make_ai_shot(x, y):
    global AIscore, shotsDisplayAI, positionsDisplay

    if positionsDisplay[x][y] == 'X':  # Trafienie
        shotsDisplayAI[x][y] = hit
        positionsDisplay[x][y] = hit
        AIscore += 100
        # Usunięto wywołanie check_if_sunk tutaj
    else:
        shotsDisplayAI[x][y] = miss
        positionsDisplay[x][y] = miss

def check_if_sunk(x, y):
    global target_mode, target_stack, shotsDisplayAI, positionsDisplay, sunk_ships
    stack = [(x, y)]
    visited = set()
    is_sunk = True

    # Przeszukiwanie połączonych trafień (DFS)
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx <= 10 and 1 <= ny <= 10:
                if positionsDisplay[nx][ny] == 'X':  # Nie trafiona część statku
                    is_sunk = False
                elif positionsDisplay[nx][ny] == hit and (nx, ny) not in visited:
                    stack.append((nx, ny))

    # Jeśli cały statek został zatopiony
    if is_sunk:
        sunk_ships += 1
        for (sx, sy) in visited:
            mark_surrounding_area(sx, sy)  # Oznacz otaczające pola jako MISS
        target_mode = False
        target_stack.clear()

def mark_surrounding_area(x, y):
    global shotsDisplayAI, positionsDisplay
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 1 <= nx <= 10 and 1 <= ny <= 10 and shotsDisplayAI[nx][ny] == 0:
            shotsDisplayAI[nx][ny] = miss
            positionsDisplay[nx][ny] = miss

# POWER-UPS

def use_radar(x, y, display, positions):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            radar_x, radar_y = x + dx, y + dy
            if 1 <= radar_x <= 10 and 1 <= radar_y <= 10:  
                if positions[radar_x][radar_y] == 0:  
                    display[radar_x][radar_y] = 'NO'
                    positions[radar_x][radar_y] = 'NO'
                elif positions[radar_x][radar_y] == cursor and display[radar_x][radar_y] != hit:
                    display[radar_x][radar_y] = cursor
                    positions[radar_x][radar_y] = cursor
                else:
                    pass


# Routing

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/position', methods=['GET', 'POST'])
def position():
    global currentAI
    if active_ships == available_ships:
        if currentAI == False:
            #place_ships_for_player()
            place_ai_ships()
            currentAI = True
            return redirect('/battlefield')
    else:
        return render_template('position.html', positionsDisplay=positionsDisplay, shotsDisplay=shotsDisplay, positionsDisplayAI=positionsDisplayAI, shotsDisplayAI=shotsDisplayAI)


@app.route('/auto_setup', methods=['GET'])
def auto_setup():
    global positionsDisplay
    place_ships_for_player()  # Automatyczne ustawianie statków gracza
    place_ai_ships()  # Ustawianie statków AI
    return redirect('/battlefield')  # Przejście do strony rozgrywki


@app.route('/position/add', methods=['POST'])
def add_position():
    x = int(request.form['x_position'])
    y = int(request.form['y_position'])
    rotation = int(request.form['rotation'])
    ship_size = int(request.form['ship_size'])

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


@app.route('/battlefield', methods=['GET', 'POST'])
def battlefield():

    return render_template('battlefield.html', positionsDisplay=positionsDisplay, shotsDisplay=shotsDisplay, positionsDisplayAI=positionsDisplayAI, shotsDisplayAI=shotsDisplayAI, score=score, AIscore=AIscore, currentShots=currentShots, currentShotsAI=currentShotsAI)

@app.route('/battlefield/shot', methods=['POST'])
def add_shot():
    x = int(request.form['x_position'])
    y = int(request.form['y_position'])
    global score, AIscore, currentShots

    if shotsDisplay[x][y] != 0 and shotsDisplay[x][y] != 'NO' and shotsDisplay[x][y] != 'X' :
        return 'You already shot at these coordinates!'
    else:
        if positionsDisplayAI[x][y] != 0:
            shotsDisplay[x][y] = hit
            score += 100
            currentShots += 1
            if score >= 2000:
                return redirect('/winner')
            else:
                ai_shoots()
                if AIscore >= 2000:
                    return redirect('/loser')
                else:
                    return redirect('/battlefield')
        else:
            shotsDisplay[x][y] = miss
            currentShots += 1
            ai_shoots()
            if AIscore >= 2000:
                return redirect('/loser')
            else:
                return redirect('/battlefield')
                    
@app.route('/battlefield/radar', methods=['POST'])
def radar():
    global currentShots
    x = int(request.form['x_position'])
    y = int(request.form['y_position'])

    if currentShots >= 5:
        use_radar(x, y, shotsDisplay, positionsDisplayAI)  
        currentShots = 1
        return redirect('/battlefield')
    else:
        return 'It takes 5 shots to charge the radar!', 403

@app.route('/winner', methods=['GET','POST'])
def winner():
    return render_template('winner.html')

@app.route('/loser', methods=['GET','POST'])
def loser():
    return render_template('loser.html')

@app.route('/reset', methods=['GET'])
def reset_game():
    global active_ships_count, currentShots, currentAI, score
    active_ships_count = {4: 0, 3: 0, 2: 0, 1: 0}
    currentShots = 0
    currentAI = False
    score = 0


    for i in range(1, len(positionsDisplay)):
        for j in range(1, len(positionsDisplay[0])):
            positionsDisplay[i][j] = 0
            positionsDisplayAI[i][j] = 0
            shotsDisplay[i][j] = 0
            shotsDisplayAI[i][j] = 0

    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)
