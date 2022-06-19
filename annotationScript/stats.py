import os
rootdir = '/home/federico/Desktop/tesis/HateEval'

total_tw = 0
colective = []
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        #get only data files
        if(file.split(".")[1] == "ann"):
            total_tw = total_tw + 1
            f = open(os.path.join(subdir, file), "r")
            content = f.readlines()
            for line in content:
                #get only the line with collective data
                if "Collective" in line:
                    x = line.split()
                    #delete not important data
                    for i in range(4):
                        del x[0]
                    #pass array of data to str
                    if(len(x) > 1):
                        x = [" ".join(x)]
                    colective.append(x[0])
#count element
data = {i:colective.count(i) for i in colective}
print(data)
print "tuits:",total_tw
print "tuists sin colectivo:", total_tw - len(colective) 
