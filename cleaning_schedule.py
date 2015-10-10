#!/bin/python
# -*- coding: utf-8 -*-

from datetime import date, timedelta
from random import randint, seed

class Task:
    def __init__(self, name, period, offset, desc):
        self.name = name
        self.period = period
        self.offset = offset
        self.desc = desc


people = ["Anna", "Bea", "Dominik", "Sophia", "Philipp"]
printFrom = 1
printTo = 13
tasks = [Task("KüAuf", 1, 0, ("Küche Aufräumen. "
                              "Flächen, Herd und Tisch "
                              "aufräumen und abwischen. Mülleimer leeren")),
         Task("KüKe", 4, 1, ("Küche Kehren")),
         Task("KüWi", 4, 3, ("Küche Wischen")),
         Task("GaKe", 8, 1, ("Gang Kehren/Staubstaugen")),
         Task("GaWi", 8, 5, ("Gang Wischen")),
         Task("Klos", 2, 0, ("Beide Klos putzen")),
         Task("WaBe", 2, 1, ("Waschbecken in beiden Toiletten putzen")),
         Task("GlaMü", 6, 2,("Glas Müll wegbringen") ),
         Task("Surp", 2, 0, ("Surprise Task. Putze irgendetwas das dreckig ist, und nicht"
                             " von einem anderen Task abgedeckt wird"))]


startDate = date(2015, 10, 12)
weekDelta = timedelta(weeks=1)
assignedTasks = {}
taskBalance = {}
seed(1)

for p in people:
    assignedTasks[p] = [""] * printTo
    taskBalance[p] = {}
    for task in tasks:
        taskBalance[p][task] = 0

def cmpBalance(p1, p2, task, w):
    if taskBalance[p1][task] > taskBalance[p2][task]:
        return p1
    if taskBalance[p1][task] < taskBalance[p2][task]:
        return p2
    totalBalance1 = 0
    totalBalance2 = 0

    if len(assignedTasks[p1][w]) > len(assignedTasks[p2][w]):
        return p2
    if len(assignedTasks[p1][w]) < len(assignedTasks[p2][w]):
        return p1
    for t in tasks:
        totalBalance1 += taskBalance[p1][t]
        totalBalance2 += taskBalance[p2][t]
    if totalBalance1 > totalBalance2:
        return p1
    if totalBalance1 < totalBalance2:
        return p2
    if randint(0,1) == 0:
        return p2
    return p1


for w in range(1, printTo):
    for task in tasks:
        if (w+task.offset) % task.period == 0:
            duePerson = "Anna"
            for p in people:
                duePerson = cmpBalance(p, duePerson, task, w)
            assignedTasks[duePerson][w] = assignedTasks[duePerson][w] + task.name + " "
            taskBalance[duePerson][task] -= len(people)*task.period
        for p in people:
            taskBalance[p][task] += 1






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

print("</table>")

for task in tasks:
    print("<p><h4 style=\"display:inline\">" + task.name + "</h4> - " + task.desc + "</p>")

print("</body></html>")
