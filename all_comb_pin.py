
all_comb = []
for i in range(0,10):
    string = ""
    string = string + str(i)
    for j in range(0, 10):
        string = string + str(j)
        for k in range(0, 10):
            string = string + str(k)
            for l in range(0, 10):
                string = string + str(l)
    all_comb.append(string)
print(len(all_comb))