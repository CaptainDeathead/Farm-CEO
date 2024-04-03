import main

PADDOCK_SIZES = {
    1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: (), 9: ()
}

for pdk in main.PADDOCKS:
    maxX = 0
    maxY = 0
    minX = 0
    minY = 0
    for point in main.PADDOCKS[pdk]:
        if point[0] > maxX: maxX = point[0]
        elif point[0] < minX: minX = point[0]
        if point[1] > maxY: maxY = point[1]
        elif point[1] < minY: minY = point[1]
    PADDOCK_SIZES[pdk] = (maxX-minX, maxY-minY)
print(str(PADDOCK_SIZES))