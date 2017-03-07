from PMap import *
blueFood = "b"
energizer = "e"
pacman = "p"
map_options = {}
def generator():
    myMap = PMap(3, 4)
    myMap.assign([2], [One()], pacman)
    if (myMap.get(2, 1) == pacman):
        myMap.assign([2], [2], blueFood)
    return myMap
def One():
    return 1
generator().write_lay_file("./out/test1.lay")
