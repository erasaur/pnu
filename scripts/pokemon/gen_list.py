import csv, os 
dir_path = os.path.dirname(os.path.realpath(__file__))

with open("{}/pokemon.csv".format(dir_path), "r") as f:
    reader = csv.reader(f)
    names = list(reader)

    res = {}
    ind = 1
    for name in names:
        name = name[0]
        res[name] = ind
        ind += 1

    print(res)
