def shield():
	pelindung = state['PlayerMap']['Owner']['Shield']
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
		

def double_shot(cell):
	global tembak
	bisa = False
	ships = state['PlayerMap']['Owner']['Ships']
	for ship in ships:
		if ship['ShipType'] == "Destroyer" and ship['Destroyed'] == False:
			bisa = True
	if bisa == True:
	#~ if (cell['X'] == 0) or (cell['X'] == map_size-1):
	#~ if cell['Y'] != 0 and cell['Y'] != map_size-1:
		if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
			output_shot(2,cell['X'],cell['Y'])	
			tembak = True
	else:
	#~ if (cell['Y'] == 0) or (cell['Y'] == map_size-1):
	#~ if cell['X'] != 0 and cell['X'] != map_size-1:
		if state['PlayerMap']['Owner']['Energy'] >= 8*energyround():
			output_shot(2,cell['X'],cell['Y'])	
			tembak = True
