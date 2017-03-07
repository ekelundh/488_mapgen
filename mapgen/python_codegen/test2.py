from PMap import *
blueFood = "b"
energizer = "e"
monster = "m"
pacman = "p"
wall = "w"
space = " "
map_options = {"player" : pacman, "border" : [wall, pacman], "playerReachable" : [monster, energizer]}
def generator():
    myMap = PMap(3, 4)
    fillWalls(myMap)
    myMap.assign([2], [2], pacman)
    if (myMap.get(2, 1) == pacman):
        myMap.assign([2], [2], blueFood)
    else:
        myMap.assign([2], [1], energizer)
    return myMap
def fillWalls(curMap):
    i = 0
    wallActor = wall
    while (i < curMap.width):
        curMap.assign([0], [i], wallActor)
        curMap.assign([curMap.height - 1], [i], wallActor)
        i += 1
    curMap.assign([0, -1], [0], wallActor)
    curMap.assign([0, -1], [curMap.width - 1], wallActor)
generator().write_lay_file("./out/test2.lay")
