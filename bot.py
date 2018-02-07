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
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    targets = []
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
    target = choice(targets)
    output_shot(1,*target)
    return

def energyround():
	if map_size == 7:
		enperround = 2;
	elif map_size == 10:
		enperround = 3;
	else:
		enperround = 4;
	return enperround;


def double_shot(cell):
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
				
def diagonal_cross(cell):
	

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
