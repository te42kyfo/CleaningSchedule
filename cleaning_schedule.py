#!/bin/python
# -*- coding: utf-8 -*-

from datetime import date, timedelta
from random import randint, seed

people = ["Anna", "Bea", "Dominik", "Sofia", "Philipp"]
printFrom = 1
printTo = 10
tasks = [("KüAuf", 1, 0),
         ("KüKe", 4, 0),
         ("KüWi", 4, 2),
         ("GaKe", 6, 0),
         ("GaWi", 6, 3),
         ("Klos", 2, 0),
         ("WaBe", 2, 0)]

startDate = date(2015, 10, 12)
weekDelta = timedelta(weeks=1)
assignedTasks = {}
taskBalance = {}
seed(1)

for p in people:
    assignedTasks[p] = [""] * printTo
    taskBalance[p] = {}
    for task in tasks:
        taskBalance[p][task[0]] = 1

def cmpBalance(p1, p2, task):
    if taskBalance[p1][task[0]] > taskBalance[p2][task[0]]:
        return p1
    if taskBalance[p1][task[0]] < taskBalance[p2][task[0]]:
        return p2
    totalBalance1 = 0
    totalBalance2 = 0
    for t in tasks:
        totalBalance1 += taskBalance[p1][t[0]]
        totalBalance2 += taskBalance[p2][t[0]]
    if totalBalance1 > totalBalance2:
        return p1
    if totalBalance1 < totalBalance2:
        return p2
    if randint(0,1) == 0:
        return p2
    return p1


for w in range(1, printTo):
    for task in tasks:
        if (w+task[2]) % task[1] == 0:
            duePerson = "Anna"
            for p in people:
                duePerson = cmpBalance(p, duePerson, task)
            assignedTasks[duePerson][w] = assignedTasks[duePerson][w] + task[0] + " "
            taskBalance[duePerson][task[0]] = 0
        for p in people:
            taskBalance[p][task[0]] += 1





print("<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>")
print("<style> td{border:1px solid black; padding:15px;}</style>")
print("</head><body><h1>WG-Putzplan</h1><table>")

print("<tr><td></td>")
for p in people:
    print("<td><b>" + p + "<b></td>");
print("</tr>")


currentDate = startDate
for w in range(1,printTo):
    if w >= printFrom:
        print( "<tr><td>" + currentDate.strftime("KW%W, %d.%b") + " </td>")
        for p in people:
            print("<td> " + assignedTasks[p][w] + "</td>")
        print("</tr>")
    currentDate += weekDelta

print("</table></body></html>")
