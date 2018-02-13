import json
import bot
import math
from random import choice

prevshot_file = "prevshot.json"     #all previous state saved in prevshot_file
# debugFile = "debugging.json" for debugging
ShipLength = [3, 2, 4, 5, 3]
# urutan indeks nomor kapal 0..4: submarine, destroyer, battleship, carrier, cruiser

## INITIALIZATION ##
def initPrevState(OpponentMap):
# initialize and read previous state from prevshot_file in json
# calls orientation checker, sets and returns FirstHitCell from file, and LastHitCell from previous shot
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
            else:
                prev_shot["LatestHitShot"] = LastShot
                if prev_shot["FirstHitShot"] == prev_shot["LatestHitShot"]:
                    prev_shot["LatestHitShot"] = ""
            coorNextTarget = LastShot
            #cek apakah ada kapal mati?
            updateOpponentShipCells(OpponentMap, cell)
            FirstHitCell = prev_shot["FirstHitShot"]
        else:
            ShieldHit = cell["ShieldHit"]
            if not ShieldHit:
                coorNextTarget = prev_shot["FirstHitShot"]
    updatePrevState()
    return FirstHitCell

def ClearPrevState():
# Clear prevshot_file datas on first phase
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
        
def CheckShotOrientation():
# returns shot target orientation, vertical or horizontal (v/h)
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

## CELL PICKER AND CHECKER ##
def chooseNextTarget(opponent_map):
# returns NextTarget cell
    if coorNextTarget == "":
        return ""
    else:
        return opponent_map[coorNextTarget[0]*map_size + coorNextTarget[1]]

def find_cell(OpponentMap, X, Y):
# return cell with coordinate X,Y
	return OpponentMap['Cells'][X*map_size + Y]

def isvalidCoor(X, Y):
# check is a pair of absis ordinate is valid
    return X>=0 and X<map_size and Y>=0 and Y<map_size

def isDeadShipCell(Cell):
# check if a coordinate belongs to a dead ship
    DeadShipCells = prev_shot['DeadShipsCells']
    if DeadShipCells != []:
        return (Cell in DeadShipCells)
    else:
        return False

## DEAD SHIP CELLS MANAGER ##
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

def seekDeadShipCells(cell, lenDeadShip, OpponentMap):
# stlah ternyata ada yg ketembak, mengecek cell yg barusan ketembak dan selidikin di radius panjang kapal mati
# mengecek cell yang barusan ketembak dan selidiki atas kanan kiri bawa
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
    return DamagedCells

## PREVSTATE UPDATER ##
def updateCurrentState(OpponentMap, X, Y):
# Memanggil semua prosedur updater
    updateLastShot(X, Y)
    updatePrevState()

def updatePrevState():
# update and rewrite prevshot file
    global prev_shot
    with open(prevshot_file, 'r+') as f:
        f.seek(0)
        json.dump(prev_shot, f, indent=4)
        f.truncate()

def updateOpponentShipCells(OpponentMap, Cell):
# Mengecek apakah ada kapal lawan yang mati akibat tembakan pada ronde sebelumnya
# Jika ada, mengenumerasikan semua cell yang mengandung kapal mati
    destroyedShip = enumDestroyedShip(OpponentMap)
    if (destroyedShip != []):
        #ada kapal yang mati
        for ShipType in destroyedShip:
            lenDeadShip = ShipLength[ShipType]
            prev_shot['DeadShipsCells'] += seekDeadShipCells(Cell, lenDeadShip, OpponentMap)
        prev_shot["FirstHitShot"] = ""
        prev_shot["LatestHitShot"] = ""

def updateLastShot(X, Y):
# Mengambil data lokasi tembakan terakhir pada file
    global prev_shot
    prev_shot["LastShotTarget"] = (X, Y)

## For debugging Only##
'''
def debugPrevShot(Input):
# Menampilkan sesuatu pada file debugging
    global prev_shot
    with open(debugFile, 'r+') as f:
        debug = json.load(f)
        debug["Debug"].append(Input)
        f.seek(0)
        json.dump(debug, f, indent=4)
        '''