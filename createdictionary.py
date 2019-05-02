
def create_dictionary():
    combos = {}
    for outer in range(50, 300):
        for inner in range(15, 200):
            if(outer > inner):
                a = lcm(outer, inner) / inner
                if a in combos:
                    combos[a] += [[outer, inner]]
                else:
                    combos[a] = [[outer,inner]]
    return combos

def lcm(x, y):
    greater = x
    while(True):
        if((greater % x == 0) and (greater % y == 0)):
            lcm = greater
            break
        greater += 1
    return lcm
        
#point_combos = create_dictionary()

f = open("pointcombos.txt","w")
f.write(str(create_dictionary()))
f.close()
