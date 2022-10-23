"""Seperates all subject codes in parentheses"""

def main():
    """Processes subjectList into subject codes"""

    majors = []
    with open("subjectList.txt", "r") as file:
        data = file.read()
        data = data.split(")")
        for i in data:
            try:
                i = i.split("(")
                majors.append(i[1])
            except IndexError:
                pass

    print(majors)

if __name__ == "__main__":
    main()
