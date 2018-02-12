import argparse
import json
import os
import time
import prevstate
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
shotOrient = ""
FirstHitCell = ""

def main(player_key):
	global map_size, state, shotOrient, FirstHitCell, OpponentMap
    # Retrieve current game state
	with open(os.path.join(output_path, game_state_file), 'r') as f_in:
		state = json.load(f_in)
	map_size = state['MapDimension']
	OpponentMap = state['OpponentMap']
	FirstHitCell = prevstate.initPrevState(OpponentMap)
	if state['Phase'] == 1:
		place_ships()
		prevstate.ClearPrevState()
	else:
		shotOrient = prevstate.CheckShotOrientation()
		fire_shot(OpponentMap['Cells'])

def output_shot(choose, x, y):
	time.sleep(1)
	if choose==1:
		prevstate.updateCurrentState(OpponentMap, x, y)
	with open(os.path.join(output_path, command_file), 'w') as f_out:
		f_out.write('{},{},{}'.format(choose, x, y))
		f_out.write('\n')
	pass

def find_cell(X, Y):
	return state['OpponentMap']['Cells'][X*map_size + Y]

def fire_shot(opponent_map):
    # Punya kita!
	hit = find_hit(opponent_map)
	global tembak
	tembak = False
	if state['Round'] == 1 or hit == []:
		targets = []
		for cell in opponent_map:
			if not cell['Damaged'] and not cell['Missed']:
				targets.append(cell)
		target = choice(targets)
		output_shot(1,target['X'],target['Y'])
	else:
		#shield()
		if not tembak:
			target = choice(hit)
			seeker(target)
			if not(tembak):
				diagonal_cross(target)
				if not(tembak):
					double_shot(target)
					if not(tembak):
						targets = SelectGreedyTarget(hit)  
						if targets != []:
							target = choice(targets)
							greedy_targets = []
							cell = find_cell(target['X']+1, target['Y'])
							if cell['X'] <= map_size-1:
								if not cell['Damaged'] and not cell['Missed']:
									greedy_targets.append(cell)
							#cek cell ke kiri
							cell = find_cell(target['X']-1, target['Y'])
							if cell['X'] >= 0:
								if not cell['Damaged'] and not cell['Missed']:
									greedy_targets.append(cell)
							#cek cell ke atas
							cell = find_cell(target['X'], target['Y']+1)
							if cell['Y'] <= map_size-1:
								if not cell['Damaged'] and not cell['Missed']:
									greedy_targets.append(cell)
							#cek cell ke bawah
							cell = find_cell(target['X'], target['Y']-1)
							if cell['Y']>=0:
								if not cell['Damaged'] and not cell['Missed']:
									greedy_targets.append(cell)     
							targetnow = choice(SelectTarget(greedy_targets))
						else:
							targets = []
							for cell in opponent_map:
								if not cell['Damaged'] and not cell['Missed'] and ((cell['X']%2 == 0 and cell['Y']%2 == 0) or (cell['X']%2 != 0 and cell['Y']%2 != 0)):
									targets.append(cell)
							targetnow = choice(targets)
						output_shot(1, targetnow['X'], targetnow['Y'])
	return

def SelectTarget(hitList):
	hitTarget = []
	if shotOrient != "" and FirstHitCell != "":
		for cell in hitList:		
			if shotOrient == "v":
				if cell['X'] == FirstHitCell[0]:
					hitTarget.append(cell)
			else:
				if cell['Y'] == FirstHitCell[1]:
					hitTarget.append(cell)
		if hitTarget != []:
			return hitTarget
		else:
			return hitList
	else:
		return hitList

def SelectGreedyTarget(hits):
	HitwG = []
	for hit in hits:
		greedy_targets = []
		#cek cell ke kanan
		cell = find_cell(hit['X']+1, hit['Y'])
		if cell['X'] <= map_size-1:
			if not cell['Damaged'] and not cell['Missed']:
				greedy_targets.append(cell)
		#cek cell ke kiri
		cell = find_cell(hit['X']-1, hit['Y'])
		if cell['X'] >= 0:
			if not cell['Damaged'] and not cell['Missed']:
				greedy_targets.append(cell)
		#cek cell ke atas
		cell = find_cell(hit['X'], hit['Y']+1)
		if cell['Y'] <= map_size-1:
			if not cell['Damaged'] and not cell['Missed']:
				greedy_targets.append(cell)
		#cek cell ke bawah
		cell = find_cell(hit['X'], hit['Y']-1)
		if cell['Y']>=0:
			if not cell['Damaged'] and not cell['Missed']:
				greedy_targets.append(cell)      
		if greedy_targets != []:
			HitwG.append(hit)
	return HitwG

def energyround():
	if map_size == 7:
		enperround = 2
	elif map_size == 10:
		enperround = 3
	else:
		enperround = 4
	return enperround

def shield():
	global tembak
	pelindung = state['PlayerMap']['Owner']['Shield']
	if pelindung['CurrentCharges'] > 0:
		ships = state['PlayerMap']['Owner']['Ships']
		for ship in ships:
			if ship['ShipType'] == "Destroyer":
				tempat_kapal = ship['Cells']
				protect = []
				for sel in tempat_kapal:
					if pelindung['CurrentCharges'] > 0:
						ships = state['PlayerMap']['Owner']['Ships']
		for ship in ships:
			if ship['ShipType'] == "Destroyer":
				tempat_kapal = ship['Cells']
				protect = []
				for sel in tempat_kapal:
					protect.append(sel)
		protect_now = choice(protect)
		output_shot(8,protect_now['X'], protect_now['Y'])	
		tembak = True		

def double_shot(cell):
	global tembak
	bisa = False
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Destroyer" and ship['Destroyed'] == False:
			bisa = True
	if bisa:
		if kosong_double(cell,'v'):
			if cell['Y'] != 0 and cell['Y'] != map_size-1:
				if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
					output_shot(2,cell['X'],cell['Y'])	
					tembak = True
		else:
			if kosong_double(cell,'h'):
				if cell['X'] != 0 and cell['X'] != map_size-1:
					if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
						output_shot(2,cell['X'],cell['Y'])	
						tembak = True
				
def diagonal_cross(cell):
	global tembak
	bisa = False
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Cruiser" and ship['Destroyed'] == False:
			bisa = True
	if bisa:
		if state['PlayerMap']['Owner']['Energy'] >= 14*energyround():
			if kosong_plus(cell):
				output_shot(6,cell['X'],cell['Y'])	
				tembak = True

def seeker(cell):
	bisa = False
	global tembak
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Submarine" and ship['Destroyed'] == False:
			bisa = True
	if bisa:
		if state['PlayerMap']['Owner']['Energy'] >= 10*energyround():
			if kosong_plus(cell):
				output_shot(7,cell['X'],cell['Y'])	
				tembak = True

def kosong3x3(cell):
	kosong = kosong_plus(cell)
	if kosong:
		A = cell
		B = find_cell(A['X']+1,A['Y'])
		if B['Damaged']:
			kosong = False
		B = find_cell(A['X']-1,A['Y'])
		if B['Damaged']:
			kosong = False
		B = find_cell(A['X'],A['Y']+1)
		if B['Damaged']:
			kosong = False
		B = find_cell(A['X'],A['Y']-1)
		if B['Damaged']:
			kosong = False
	return kosong

def kosong_double(cell,c):
	kosong = True
	if c == 'v':
		A = find_cell(cell['X'], cell['Y']+1)
		if A['Damaged']:
			kosong = False
		A = find_cell(cell['X'], cell['Y']-1)
		if A['Damaged']:
			kosong = False
	else:
		A = find_cell(cell['X']+1, cell['Y'])
		if A['Damaged']:
			kosong = False
		A = find_cell(cell['X']-1, cell['Y'])
		if A['Damaged']:
			kosong = False
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
	
	
def find_hit(opponent_map):
	global hit
	nextTarget = prevstate.chooseNextTarget(opponent_map)
	hit = []
	if nextTarget == "":
		for cell in opponent_map:
			if cell['Damaged'] and not prevstate.isDeadShipCell(cell):
				hit.append(cell)
	else:
		hit.append(nextTarget)
	return hit
	

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
