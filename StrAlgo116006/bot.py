import argparse
import json
import os
#import time
import prevstate
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
shotOrient = ""
FirstHitCell = ""

## INISIALISASI PERMAINAN ##
def main(player_key):
# Inisialisasi Game
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
	#time.sleep(1) untuk keperluan time delay
	prevstate.debugPrevShot(choose)
	if choose!=8:
		prevstate.updateCurrentState(OpponentMap, x, y)
	with open(os.path.join(output_path, command_file), 'w') as f_out:
		f_out.write('{},{},{}'.format(choose, x, y))
		f_out.write('\n')
	pass

def fire_shot(opponent_map):
# Mengatur pilihan tembakan dan target
	global tembak
	hit = find_hit(opponent_map)
	tembak = False
	if hit == []:
		targets = []
		for cell in opponent_map:
			if not cell['Damaged'] and not cell['Missed'] and ((cell['X']%2 == 0 and cell['Y']%2 == 0) or (cell['X']%2 != 0 and cell['Y']%2 != 0)):
				targets.append(cell)
		target = choice(targets)
		seeker(target)
		diagonal_cross(target)
		double_shot(target)
		if not tembak:
			output_shot(1,target['X'],target['Y'])
	else:
		shield()
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
					if not cell['Damaged'] and not cell['Missed']:
						targets.append(cell)
				targetnow = choice(targets)
			output_shot(1, targetnow['X'], targetnow['Y'])
	return

## UTILITAS TAMBAHAN ##
def find_hit(opponent_map):
# Mengenumerasikan semua kandidat cell yang menjadi target tembakan selanjutnya
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

def find_cell(X, Y):
# Mencari cell dengan koordinat X,Y
	return state['OpponentMap']['Cells'][X*map_size + Y]

def energyround():
# Menghasilkan nilai penambahan energi tiap round
	if map_size == 7:
		enperround = 2
	elif map_size == 10:
		enperround = 3
	else:
		enperround = 4
	return enperround

def SelectTarget(hitList):
# Mengenumerasikan target sesuai orientasi tembakan (jika terdefinisi)
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
# Menseleksi target hits yang memenuhi kondisi
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

## Jenis Command Tembakan dan Shield ##
def double_shot(cell):
# Menembakkan dua cell secara vertikal(depan-belakang) atau horizontal (kanan-kiri)
	global tembak
	if not tembak:
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
# Menembakkan cell engan fire shot diagonal secara diagonal
	global tembak
	if not tembak:
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
# Melakukan tembakan fire seeker missile
	global tembak
	bisa = False
	if not tembak:
		ships = state['PlayerMap']['Owner']['Ships']
		for ship in ships:
			if ship['ShipType'] == "Submarine" and ship['Destroyed'] == False:
				bisa = True
		if bisa:
			if state['PlayerMap']['Owner']['Energy'] >= 10*energyround():
				if kosong_plus(cell):
					output_shot(7,cell['X'],cell['Y'])	
					tembak = True

def shield():
# Menginisialisasi pemasangan shield
	global tembak
	pelindung = state['PlayerMap']['Owner']['Shield']
	if pelindung['CurrentCharges'] > 5:
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

## Cek cell sebelum memilih jenis tembakan ##
def kosong3x3(cell):
# Mengecek apakah cell 3x3 kosong sebelum ditembakkan dengan seeker
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
# Mengecek apakah cell atas-bawah atau kanan-kiri kosong sebelum ditembakkan dengan double shot	
	kosong = True
	if c == 'v':
		if cell['Y'] < map_size-1:
			A = find_cell(cell['X'], cell['Y']+1)
			if A['Damaged']:
				kosong = False
		else:
			kosong = False
		if cell['Y'] > 0:
			A = find_cell(cell['X'], cell['Y']-1)
			if A['Damaged']:
				kosong = False
		else:
			kosong = False
	else:
		if cell['X'] < map_size -1:
			A = find_cell(cell['X']+1, cell['Y'])
			if A['Damaged']:
				kosong = False
		else:
			kosong = False
		if cell['X'] > 0:
			A = find_cell(cell['X']-1, cell['Y'])
			if A['Damaged']:
				kosong = False
		else:
			kosong = False
	return kosong

def kosong_plus(cell):
# Mengecek apakah cell atas-bawah-kanan-kiri kosong sebelum ditembakkan
	kosong = True
	if cell['X'] < map_size-1:
		A = find_cell(cell['X']+1,cell['Y'])
		if A['Damaged']:
			kosong = False
	else: 
		kosong = False
	if cell['X'] > 0 :
		A = find_cell(cell['X']-1,cell['Y'])
		if A['Damaged']:
			kosong = False
	else:
		kosong = False
	if cell['Y'] < map_size -1:
		A = find_cell(cell['X'],cell['Y']+1)
		if A['Damaged']:
			kosong = False
	else:
		kosong = False
	if cell['Y'] > 0 :
		A = find_cell(cell['X'],cell['Y']-1)
		if A['Damaged']:
			kosong = False
	else:
		kosong = False
	return kosong	

## Peletakan kapal ##	
def place_ships():
# Please place your ships in the following format <Shipname> <x> <y> <direction>
# Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
# Directions: north east south west
	nomor=[1,2,3]
	pilih=choice(nomor)
	if map_size==7:
		if pilih==1:
			ships = [
				'Battleship 6 0 north', 
				'Carrier 0 3 east', 
				'Cruiser 2 1 east', 
				'Submarine 5 4 north', 
				'Destroyer 2 6 east']
		elif pilih==2:
			ships = [
				'Battleship 6 1 west', 
				'Carrier 1 4 east', 
				'Cruiser 0 6 east', 
				'Submarine 6 6 west', 
				'Destroyer 2 2 west' ]
		elif pilih==3:
			ships = [
				'Battleship 5 3 north', 
				'Carrier 1 0 east', 
				'Cruiser 1 2 east', 
				'Submarine 0 5 east', 
				'Destroyer 2 4 east']
	elif map_size==10:
		if pilih==1:
			ships = [
				'Battleship 2 2 east', 
				'Carrier 2 7 east', 
				'Cruiser 7 2 south', 
				'Submarine 8 9 south', 
				'Destroyer 3 4 north']
		elif pilih==2:
			ships = [
				'Battleship 1 0 north', 
				'Carrier 3 4 north', 
				'Cruiser 5 2 north', 
				'Submarine 8 9 south', 
				'Destroyer 7 1 east']
		elif pilih==3:
			ships = [
				'Battleship 1 1 north', 
				'Carrier 3 1 east', 
				'Cruiser 4 3 north', 
				'Submarine 7 6 north', 
				'Destroyer 1 8 east']
	elif map_size==14:
		if pilih==1:
			ships = [
				'Battleship 13 6 south', 
				'Carrier 5 0 east', 
				'Cruiser 0 6 east', 
				'Submarine 8 13 south', 
				'Destroyer 3 10 north']
		elif pilih==2:
			ships = [
				'Battleship 1 5 north', 
				'Carrier 3 13 east', 
				'Cruiser 9 11 east', 
				'Submarine 7 4 south', 
				'Destroyer 13 5 north']
		elif pilih==3:
			ships = [
				'Battleship 1 5 north', 
				'Carrier 4 13 south', 
				'Cruiser 12 8 north', 
				'Submarine 6 2 north', 
				'Destroyer 11 1 east']

	with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
		for ship in ships:
			f_out.write(ship)
			f_out.write('\n')
	return

### MAIN PROGRAM ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
