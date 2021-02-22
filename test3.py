import timeit


def load_level(filename):
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        global tileset
        tileset = mapFile.readline().strip()
        level_map = []
        chests_data = []

        line = mapFile.readline().strip()
        while 'end' not in line:
            level_map.append(line)
            line = mapFile.readline().strip()

        line = mapFile.readline().strip()
        while line.startswith('c'):
            chests_data.append(line.strip()[2:])
            line = mapFile.readline().strip()

        other_data = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map)), chests_data


def found(pathArr, finPoint):
    weight = 1
    for i in range(len(pathArr) * len(pathArr[0])):
        weight += 1
        for y in range(len(pathArr)):
            for x in range(len(pathArr[y])):
                if pathArr[y][x] == (weight - 1):
                    if y > 0 and pathArr[y - 1][x] == 0:
                        pathArr[y - 1][x] = weight
                    if y < (len(pathArr) - 1) and pathArr[y + 1][x] == 0:
                        pathArr[y + 1][x] = weight
                    if x > 0 and pathArr[y][x - 1] == 0:
                        pathArr[y][x - 1] = weight
                    if x < (len(pathArr[y]) - 1) and pathArr[y][x + 1] == 0:
                        pathArr[y][x + 1] = weight

                    if (abs(y - finPoint[0]) + abs(x - finPoint[1])) == 1:
                        pathArr[finPoint[0]][finPoint[1]] = weight
                        return True
    return False


def printPath(pathArr, finPoint):
    y = finPoint[0]
    x = finPoint[1]
    weight = pathArr[y][x]
    result = list(range(weight))
    while (weight):
        weight -= 1
        if y > 0 and pathArr[y - 1][x] == weight:
            y -= 1
            result[weight] = 'down'
        elif y < (len(pathArr) - 1) and pathArr[y + 1][x] == weight:
            result[weight] = 'up'
            y += 1
        elif x > 0 and pathArr[y][x - 1] == weight:
            result[weight] = 'right'
            x -= 1
        elif x < (len(pathArr[y]) - 1) and pathArr[y][x + 1] == weight:
            result[weight] = 'left'
            x += 1

    return result[1:]


def main():
    # Выход из лабиринта .Волновой алгоритм
    labirint = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 0, 1, 1, 0, 0, 0, 1, 1, 1],
        [1, 0, 1, 1, 0, 1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    labirint = [[0 if a in '.@b' else 1 for a in i] for i in load_level('map3.txt')[0]]
    # Координаты входа [2,0], координаты выхода [7,0]. В которой 1 - это стена, 0 - это путь.
    # координаты входа
    pozIn = (14, 38)
    pozOut = (1, 3)

    path = [[x if x == 0 else -1 for x in y] for y in labirint]
    path[pozIn[0]][pozIn[1]] = 1

    if not found(path, pozOut):
        print("Путь не найден!")
        return

    result = printPath(path, pozOut)

    for i in path:
        for line in i:
            print("{:^3}".format(line), end=",")
        print("")
    print(result)
    print()


if __name__ == '__main__':
    # timeit.timeit('main()', number=1)
    main()
