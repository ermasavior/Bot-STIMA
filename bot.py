import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0


def main(player_key):
    global map_size
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
    else:
        fire_shot(state['OpponentMap']['Cells'])


def output_shot(choose, x, y):
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # Punya kita!
	find_hit(opponent_map)
	if state['Round'] == 1 or hit == []:
		targets = []
		for cell in opponent_map:
			if not cell['Damaged'] and not cell['Missed']:
				valid_cell = cell['X'], cell['Y']
				targets.append(valid_cell)
		target = choice(targets)
		output_shot(1,*target)
	else:
		target = choice(hit)
		double_shot(target)
		if not(tembak):
			diagonal_cross(target)
			if not(tembak):
				seeker(target)
				if not(tembak):
					targets = []
					greedy_targets = []
					for cell in opponent_map:
						if cell['Damaged']:
							A=cell
							if cell['X']!=map_size-1:
							#cek cell ke kanan
								cell['X']+=1
								if not cell['Damaged'] and not cell['Missed']:
									valid_cell = cell['X'], cell['Y']
									greedy_targets.append(valid_cell)
							cell=A
							#cek cell ke kiri
							if cell['X']!=0:
								cell['X']-=1
								if not cell['Damaged'] and not cell['Missed']:
									valid_cell = cell['X'], cell['Y']
									greedy_targets.append(valid_cell)
							cell=A
							#cek cell ke atas
							if cell['Y']!=map_size-1:
								cell['Y']+=1
								if not cell['Damaged'] and not cell['Missed']:
									valid_cell = cell['X'], cell['Y']
									greedy_targets.append(valid_cell)
							cell=A
							#cek cell ke bawah
							if cell['Y']!=0:
								cell['Y']-=1
								if not cell['Damaged'] and not cell['Missed']:
									valid_cell = cell['X'], cell['Y']
									greedy_targets.append(valid_cell)                                
						if not cell['Damaged'] and not cell['Missed']:
							valid_cell = cell['X'], cell['Y']
							targets.append(valid_cell)
					if greedy_targets!=[]:
						target=choice(greedy_targets)
					else:
						target = choice(targets)
					output_shot(*target)
	return

def energyround():
	if map_size == 7:
		enperround = 2
	elif map_size == 10:
		enperround = 3
	else:
		enperround = 4;
	return enperround


def double_shot(cell):
	global tembak
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Destroyer" and ship['Destroyed'] == False:
			bisa = True
	if bisa == True:
		if (cell['X'] == 0) or (cell['X'] == map_size-1):
			if cell['Y'] != 0 and cell['Y'] != map_size-1:
				if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
					output_shot(2,cell['X'],cell['Y'])	
		else:
			if (cell['Y'] == 0) or (cell['Y'] == map_size-1):
				if cell['X'] != 0 and cell['X'] != map_size-1:
					if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
						output_shot(2,cell['X'],cell['Y'])	
						tembak = True
				
def diagonal_cross(cell):
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Cruiser" and ship['Destroyed'] == False:
			bisa = True
	if bisa == True:
		if state['PlayerMap']['Owner']['Energy'] >= 14*energyround():
			if kosong_plus(cell):
				output_shot(6,cell['X'],cell['Y'])	
				tembak = True

def seeker(cell):
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Submarine" and ship['Destroyed'] == False:
			bisa = True
	if bisa == True:
		if state['PlayerMap']['Owner']['Energy'] >= 10*energyround():
			if kosong_plus(cell):
				output_shot(7,cell['X'],cell['Y'])	
				tembak = True

def kosong3x3(cell):
	kosong = kosong_plus(cell)
	if kosong:
		A = cell
		A['X'] += 1
		A['Y'] += 1
		if A['Damaged']:
			kosong = False
		A['X'] -=2
		if A['Damaged']:
			kosong = False
		A['Y'] -=2
		if A['Damaged']:
			kosong = False
		A['X'] += 2
		if A['Damaged']:
			kosong = False
		A['X'] -=1
		A['Y'] +=1
	return kosong
	


def kosong_plus(cell):
	kosong = True
	cell['X']+=1
	if cell['Damaged']:
		kosong = False
	cell['X']-=2
	if cell['Damaged']:
		kosong = False
	cell['X'] += 1
	cell['Y'] += 1
	if cell['Damaged']:
		kosong = False
	cell['Y'] -=2
	if cell['Damaged']:
		kosong = False
	cell['Y'] +=1
	return kosong
	

def myfire_shot(opponent_map):
	find_hit(opponent_map)
	tempat = hit[0]
	x,y = tempat
	# if x+1,y belum damaged mka coba
	# kalau sudah damaged, hapus dari hit 
	# if x-1, y belum damaged mka coba
	# if x, y+1 belum damaged mka coba
	# if x, y-1 belum damaged mka coba
	return
	
def find_hit(opponent_map):
	global hit
	hit = []
	for cell in opponent_map:
		if cell['Damaged']:
			valid = cell['X'], cell['Y']
			hit.append(valid)
	
		
		#cek apakah disekitarnya ada hit...
			

def hitung_hit(opponent_map):
	hitung = 0;
	for cell in opponent_map:
		if cell['Damaged']:
			hitung+=1
	return hitung
			

def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    ships = ['Battleship 1 0 north',
             'Carrier 3 1 East',
             'Cruiser 4 2 north',
             'Destroyer 7 3 north',
             'Submarine 1 8 East'
             ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
