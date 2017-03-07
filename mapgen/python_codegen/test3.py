from PMap import *
pacman = "p"
map_options = {}
def generator():
    myMap = PMap(3, 4)
    myMap.assign([0], [0], pacman)
    return myMap
generator().write_lay_file("./out/test3.lay")
