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
    global prev_shot
    readPrevState()
    '''
    LastShot = prev_shot["LastShotTarget"]
    if (LastShot != []):
        cell = CheckLastShot(state, LastShot[0], LastShot[1])
        if (cell["Damaged"]):
            prev_shot["HitShot"].append(LastShot)
    '''

def ClearPrevState():
    global prev_shot
    prev_shot["LastShotTarget"] = []
    prev_shot["DeadShipType"] = [False, False, False, False, False]
    prev_shot["DeadShipsCells"] = []
    prev_shot["HitShot"] = []
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

def isPrevShipDead(idx):
# Check if a ship has died in previous round
    DeadShipType = prev_shot['DeadShipType']
    return (DeadShipType[idx])

def enumDestroyedShip(OpponentMap):
# enumerate all destroyed ships in current round (in type number)
    global prev_shot
    DestroyedShip = []
    ShipList = OpponentMap['Ships']
    for i in range(0, 5):
        if ShipList[i]['Destroyed'] and not isPrevShipDead(i):
            DestroyedShip.append(i)
            prev_shot['DeadShipType'][i] = True
    return DestroyedShip

# urutan nomor kapal (0,1,2,3,4)
# submarine, destroyer, battleship, carrier, cruiser

def isvalidCoor(X, Y):
    return X>=0 and X<map_size and Y>=0 and Y<map_size

# stlah ternyata ada yg ketembak, ngecek cell yg barusan ketembak dan selidikin plus
def seekDeadShipCells(cell, lenDeadShip, OpponentMap):
    X, Y = cell['X'], cell['Y']
    DamagedCells = []
    #seek horizontal right
    i = 0
    while (i<lenDeadShip):
        if (isvalidCoor(X+i, Y)):
            cell = OpponentMap["Cells"][(X+i)*10+Y]
            if cell['Damaged'] and not isDeadShipCell(cell):
                DamagedCells.append(cell)
            else:
                break
            i += 1
        else:
            break
    #seek horizontal left
    i = 0
    while (i>-1*lenDeadShip):
        if (isvalidCoor(X+i, Y)):
            cell = OpponentMap["Cells"][(X+i)*10 + Y]
            if cell['Damaged'] and not isDeadShipCell(cell):
                DamagedCells.append(cell)
            else:
                break
            i -= 1
        else:
            break
    if DamagedCells == []:
        #seek vertical up
        i = 0
        while (i<lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = OpponentMap["Cells"][(X+i)*10 + Y]
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)
                else:
                    break
                i += 1
            else:
                break
        #seek vertical down
        i = 0
        while (i>-1*lenDeadShip):
            if (isvalidCoor(X, Y+i)):
                cell = OpponentMap["Cells"][(X+i)*10 + Y]
                if cell['Damaged'] and not isDeadShipCell(cell):
                    DamagedCells.append(cell)
                else:
                    break
                i -= 1
            else:
                break
    return DamagedCells

# used in bot.py
def updateAll(OpponentMap, X, Y):
    updateLastShot(X, Y)
    cell = OpponentMap["Cells"][X*10+Y]
    updateDeadShipCells(OpponentMap, cell)

def updateDeadShipCells(OpponentMap, Cell):
    global map_size
    destroyedShip = enumDestroyedShip(OpponentMap)
    if (destroyedShip != []):
        map_size = len(OpponentMap["Cells"])/2
        for ShipType in destroyedShip:
            lenDeadShip = ShipLength[ShipType]
            prev_shot['DeadShipsCells'] += seekDeadShipCells(Cell, lenDeadShip, OpponentMap)
    updatePrevState()

def isDeadShipCell(Cell):
# is a coordinate belongs to a dead ship
    DeadShipCells = prev_shot['DeadShipsCells']
    return (Cell in DeadShipCells)

def updateLastShot(X, Y):
    global prev_shot
    prev_shot["LastShotTarget"] = (X, Y)

def CheckLastShot(state, X, Y):
    return state["OpponentMap"]["Cells"][X*10+Y]

def find_hit(opponent_map):
    hitList = []
    hitCoor = prev_shot["HitShot"]
    for coor in hitCoor:
        X = coor[0]
        Y = coor[1]
        cell = opponent_map[X*10+Y]
        hitList.append(cell)
    return hitList

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