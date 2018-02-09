import json
import bot
from random import choice

prevshot_file = "prevshot.json"
ShipLength = [3, 2, 4, 5, 3]

# for debugging
def debugPrevShot(Input):
    global prev_shot
    with open("debugging.json", 'r+') as f:
        prev_shot = json.load(f)
        prev_shot["Debug"].append(Input)
        f.seek(0)
        json.dump(prev_shot, f, indent=4)

def initPrevState():
    readPrevState()
    LastShot = prev_shot["LastShotTarget"]
    if (LastShot != []):
        if (LastShot['Damaged']):
            prev_shot["HitShot"].append(LastShot)
        prev_shot["LastShotTarget"] = ""
    updatePrevState()

def ClearPrevState():
    global prev_shot
    prev_shot["ShotTarget"] = []
    prev_shot["DeadShipType"] = [False, False, False, False, False]
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

def isPrevShipDead(idx):
# Check if a ship has died in previous round
    DeadShipType = prev_shot['DeadShipType']
    return (DeadShipType[idx])

def enumDestroyedShip():
# enumerate all destroyed ships in current round (in type number)
    global prev_shot
    DestroyedShip = []
    ShipList = bot.state['OpponentMap']['Ships']
    for i in range(0, 5):
        if ShipList[i]['Destroyed'] and not isPrevShipDead(i):
            DestroyedShip.append(i)
            prev_shot['DeadShipType'][i] = True
    updatePrevState()
    return DestroyedShip

# urutan nomor kapal (0,1,2,3,4)
# submarine, destroyer, battleship, carrier, cruiser

def isvalidCoor(X, Y):
    return X>=0 and X<bot.map_size and Y>=0 and Y<bot.map_size

# stlah ternyata ada yg ketembak, ngecek cell yg barusan ketembak dan selidikin plus
def seekDeadShipCells(cell, lenDeadShip):
    X, Y = cell['X'], cell['Y']
    DamagedCells = []
    #seek horizontal right
    i = 0
    while (i<lenDeadShip):
        if (isvalidCoor(X-i, Y)):
            cell = bot.find_cell(X+i, Y)
            if cell['Damaged'] and not isDeadShipCell(cell):
                DamagedCells.append(cell)
            else:
                break
        i += 1
    #seek horizontal left
    i = 0
    while (i<lenDeadShip):
        if (isvalidCoor(X+i, Y)):
            cell = bot.find_cell(X+i, Y)
            if cell['Damaged'] and not isDeadShipCell(cell):
                DamagedCells.append(cell)
            else:
                break
        i -= 1
    if DamagedCells == []:
        #seek vertical up
        i = 0
        while (i<lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = bot.find_cell(X+i, Y)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)
                else:
                    break
            i += 1
        #seek vertical down
        i = 0
        while (i<lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = bot.find_cell(X+i, Y)
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)
                else:
                    break
            i -= 1
    return DamagedCells

def updateDeadShipCells(Cell):
    for ShipType in enumDestroyedShip():
        lenDeadShip = ShipLength[ShipType]
        prev_shot['DeadShipCells'] += seekDeadShipCells(Cell, lenDeadShip)
    updatePrevState()

def isDeadShipCell(Cell):
# is a coordinate belongs to a dead ship
    DeadShipCells = prev_shot['DeadShipsCells']
    return (Cell in DeadShipCells)

def updateLastShot(X, Y):
    global prev_shot
    targetcell = bot.find_cell(X, Y)
    prev_shot["LastShotTarget"] = targetcell
    updatePrevState()

'''
def noteTarget(choose, X, Y):
# yg udh ditarget simpen di file
    if choose==1: #fireshot
        Coor = X, Y
        prev_shot['ShotTarget'].append(Coor)
    elif choose==2:
        Coor1 = X+1, Y
        Coor2 = X-1, Y
        prev_shot['ShotTarget'].append(Coor1) 
        prev_shot['ShotTarget'].append(Coor2) 
    elif choose==3:
        Coor1 = X, Y+1
        Coor2 = X, Y-1
        prev_shot['ShotTarget'].append(Coor1) 
        prev_shot['ShotTarget'].append(Coor2) 
    updatePrevState()

def isCurrentTarget(Cell):
# boolean target fireshot
    if Cell['Damaged']:
        ShotCell = prev_shot['ShotTarget']
        coorCell = Cell['X'], Cell['Y']
        if ShotCell != []:
            return (coorCell in ShotCell)
        else:
            return isDeadShipCoor(coor)
    else:
        return False

def chooseTarget(greedy_targets):
    global map_size
    chosen = choice(greedy_targets)
    for target in greedy_targets:
        temp = target['X']-2
        target['X'] -= 2
        if (target['X'] >= 0 and target['X'] <= map_size-1 and target['Damaged']):
            chosen == target['X']
    return chosen
'''