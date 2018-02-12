import json
import bot
import math
from random import choice

prevshot_file = "prevshot.json"
ShipLength = [3, 2, 4, 5, 3]
debugFile = "debugging.json"

# for debugging
def debugPrevShot(Input):
    global prev_shot
    with open(debugFile, 'r+') as f:
        debug = json.load(f)
        debug["Debug"].append(Input)
        f.seek(0)
        json.dump(debug, f, indent=4)

def initPrevState(OpponentMap):
    global prev_shot, map_size, coorNextTarget
    readPrevState()
    map_size = int(math.sqrt(len(OpponentMap["Cells"])))
    FirstHitCell = ""
    coorNextTarget = ""
    LastShot = prev_shot["LastShotTarget"]
    if (LastShot != ""):
        cell = find_cell(OpponentMap, LastShot[0], LastShot[1])
        if cell["Damaged"]:
            if prev_shot["FirstHitShot"] == "":
                prev_shot["FirstHitShot"] = LastShot
                FirstHitCell = LastShot
            else:
                prev_shot["LatestHitShot"] = LastShot
                FirstHitCell = prev_shot["FirstHitShot"]
            coorNextTarget = LastShot
            #cek apakah ada kapal mati?
            updateOpponentShipCells(OpponentMap, cell)
        else:
            coorNextTarget = prev_shot["FirstHitShot"]
    updatePrevState()
    return FirstHitCell

def chooseNextTarget(opponent_map):
    if coorNextTarget == "":
        return ""
    else:
        return opponent_map[coorNextTarget[0]*map_size + coorNextTarget[1]]

def CheckShotOrientation():
# ngehasilin vertical or horizontal (v/h)
    FirstHitShot = prev_shot["FirstHitShot"]
    LatestHitShot = prev_shot["LatestHitShot"]
    if FirstHitShot != "" and LatestHitShot != "":
        if FirstHitShot[0] == LatestHitShot[0]:
            return "v"
        elif FirstHitShot[1] == LatestHitShot[1]:
            return "h"
        else:
            return ""
    else:
        return ""

def ClearPrevState():
    global prev_shot
    prev_shot["LastShotTarget"] = ""
    prev_shot["LatestHitShot"] = ""
    prev_shot["FirstHitShot"] = ""
    prev_shot["ShipsType"] = [False, False, False, False, False]
    prev_shot["DeadShipsCells"] = []
    updatePrevState()

def readPrevState():
# read prevshot file
    global prev_shot
    with open(prevshot_file, 'r') as f:
        prev_shot = json.load(f)
        
def updatePrevState():
# update and rewrite prevshot file
    global prev_shot
    with open(prevshot_file, 'r+') as f:
        f.seek(0)
        json.dump(prev_shot, f, indent=4)
        f.truncate()

def enumDestroyedShip(OpponentMap):
# enumerate all destroyed ships in current round (in type number)
# if no dead ships, return []
    global prev_shot
    ShipState = []
    DestroyedShip = []
    ShipList = OpponentMap['Ships']
    PrevShipState = prev_shot['ShipsType']
    i = 0
    for Ship in ShipList:
        ShipState.append(Ship['Destroyed'])
        if (Ship['Destroyed'] != PrevShipState[i]):
            DestroyedShip.append(i)
        i += 1
    prev_shot['ShipsType'] = ShipState
    return DestroyedShip

# urutan nomor kapal (0,1,2,3,4)
# submarine, destroyer, battleship, carrier, cruiser
def isvalidCoor(X, Y):
    return X>=0 and X<map_size and Y>=0 and Y<map_size

def find_cell(OpponentMap, X, Y):
	return OpponentMap['Cells'][X*map_size + Y]

# stlah ternyata ada yg ketembak, ngecek cell yg barusan ketembak dan selidikin di radius panjang kapal mati
def seekDeadShipCells(cell, lenDeadShip, OpponentMap):
    X, Y = cell['X'], cell['Y']
    DamagedCells = []
    shotOrient = CheckShotOrientation()
    #seek horizontal right
    if shotOrient == "h":
        i = 1
        while (i<lenDeadShip):
            if (isvalidCoor(X+i, Y)):
                cell = find_cell(OpponentMap, X+i, Y)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)
                    i += 1
                else:
                    break
            else:
                break
        #seek horizontal left
        i = 0
        while (i>-1*lenDeadShip):
            if (isvalidCoor(X+i, Y)):
                cell = find_cell(OpponentMap, X+i, Y)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)          
                    i -= 1
                else:
                    break
            else:
                break
    else:
        #seek vertical up
        i = 1
        while (i<lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = find_cell(OpponentMap, X, Y+i)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)                
                    i += 1
                else:
                    break
            else:
                break
        #seek vertical down
        i = 0
        while (i>-1*lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = find_cell(OpponentMap, X, Y+i)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)                 
                    i -= 1
                else:
                    break
            else:
                break 
    debugPrevShot(DamagedCells)
    return DamagedCells

# used in bot.py
def updateCurrentState(OpponentMap, X, Y):
    updateLastShot(X, Y)
    updatePrevState()

def updateOpponentShipCells(OpponentMap, Cell):
    destroyedShip = enumDestroyedShip(OpponentMap)
    if (destroyedShip != []):
        #ada kapal yang mati
        for ShipType in destroyedShip:
            lenDeadShip = ShipLength[ShipType]
            prev_shot['DeadShipsCells'] += seekDeadShipCells(Cell, lenDeadShip, OpponentMap)
        prev_shot["FirstHitShot"] = ""
        prev_shot["LatestHitShot"] = ""

def isDeadShipCell(Cell):
# is a coordinate belongs to a dead ship
    DeadShipCells = prev_shot['DeadShipsCells']
    if DeadShipCells != []:
        return (Cell in DeadShipCells)
    else:
        return False

def updateLastShot(X, Y):
    global prev_shot
    prev_shot["LastShotTarget"] = (X, Y)