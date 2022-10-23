#read the "tobecleaned.txt" file and store everything between a ( and a ) in a list, then print the list
majors = []
with open("tobecleaned.txt", "r") as f:
    data = f.read()
    data = data.split(")")
    for i in data:
        try:
            i = i.split("(")
            majors.append(i[1])
        except:
            pass

print(majors)

    