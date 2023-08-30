import csv

with open('my.csv', newline='') as csvfile:
    r = csv.reader(csvfile)

    for row in r:
        print(row[0])
        print(type(row[1]))
