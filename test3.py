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

print(load_level('map3.txt')[1])
