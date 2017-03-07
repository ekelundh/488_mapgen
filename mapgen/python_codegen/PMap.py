class PMap():
    def __init__(self, height, width, default_actor=" "):
        self.map_repr = [[default_actor for x in range(width)] for y in range(height)]
        self.height = height
        self.width = width
        self.default_actor = default_actor

    def write_lay_file(self, output_path):
        f = open(output_path, "w")
        for i, row in enumerate(self.map_repr):
            for x in row:
                f.write(x)
            if i != self.height - 1:
                f.write("\n")
        f.close()

    def get(self, y, x):
        return self.map_repr[y][x]

    def assign(self, y, x, value):
        """
        assign value to all locations in map[x1:x2][y1:y2].
        it generally follows slicing operation; x1,y1 are inclusive; x2, y2 are exclusive.
        y, x are list. if it contains only one element, it means simple access; if it has 2 elements, it is slicing
        """
        y1 = y[0]
        if len(y) == 1:
            if y1 < 0:
                y1 = self.height + y1
            y2 = y1 + 1
        else:
            y2 = y[1]

        x1 = x[0]
        if len(x) == 1:
            if x1 < 0:
                x1 = self.width + x1
            x2 = x1 + 1
        else:
            x2 = x[1]

        self.assign_slice(y1, y2, x1, x2, value)
        return

    def assign_slice(self, y1, y2, x1, x2, value):
        """
        assign value to all locations in map[x1:x2][y1:y2].
        it generally follows slicing operation; x1,y1 are inclusive; x2, y2 are exclusive.
        """
        if y1 < 0:
            y1 = self.height + y1
        if y2 < 0:
            y2 = self.height + y2
        if x1 < 0:
            x1 = self.width + x1
        if x2 < 0:
            x2 = self.width + x2

        for y in range(y1, y2):
            for x in range(x1, x2):
                self.map_repr[y][x] = value
        return
