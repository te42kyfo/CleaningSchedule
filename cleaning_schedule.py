#!/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date, timedelta
from random import randint, seed

class Task:
    def __init__(self, name, period, offset, desc):
        self.name = name
        self.period = period
        self.offset = offset
        self.desc = desc


people = ["Anna", "Bea", "Dominik", "Sophia", "Philipp"]
printFrom = 11
printTo = 20
tasks = [Task("KüAuf", 1, 0, ("Küche Aufräumen. "
                              "Flächen, Herd und Tisch "
                              "aufräumen und abwischen. Mülleimer leeren")),
         Task("KüKe", 4, 1, ("Küche Kehren")),
         Task("KüWi", 4, 3, ("Küche Wischen")),
         Task("GaKe", 8, 1, ("Gang Kehren/Staubstaugen")),
         Task("GaWi", 8, 5, ("Gang Wischen")),
         Task("Klos", 2, 0, ("Beide Klos putzen")),
         Task("WaBe", 2, 1, ("Waschbecken + Spiegel in beiden Toiletten putzen")),
         Task("GlaMü", 6, 2,("Glas Müll wegbringen") ),
         Task("Surp", 2, 0, ("Surprise Task. Putze irgendetwas das dreckig ist, und nicht"
                             " von einem anderen Task abgedeckt wird"))]

excludeWeeks = [11]
transitions = {}
transitions[12] =("Bea", "Benni")

nameToTask = {}
for t in tasks:
    nameToTask[t.name] = t

startDate = date(2015, 10, 12)
weekDelta = timedelta(weeks=1)
planName = (startDate + printFrom*weekDelta).strftime("%WY%y") + "-" + (startDate + printTo*weekDelta).strftime("%WY%y")
assignedTasks = {}
taskBalance = {}
seed(1)

for p in people:
    assignedTasks[p] = [""] * printTo
    taskBalance[p] = {}
    for task in tasks:
        taskBalance[p][task] = 0

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        state = 1
        task = ""
        for line in f:
            if state == 1:
                state = 2
            elif state == 2:
                task = line.split()[0]
                nameToTask[task].offset = int(line.split()[1])
                state = 3
            elif state == 3:
                if line == "\n":
                    state = 2
                    continue
                taskBalance[line.split()[0]][nameToTask[task]] = int(line.split()[1])


def cmpBalance(p1, p2, task, w):
    if len(assignedTasks[p1][w]) > len(assignedTasks[p2][w]):
        return p2
    if len(assignedTasks[p1][w]) < len(assignedTasks[p2][w]):
        return p1

    if taskBalance[p1][task] > taskBalance[p2][task]:
        return p1
    if taskBalance[p1][task] < taskBalance[p2][task]:
        return p2
    totalBalance1 = 0
    totalBalance2 = 0



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


for w in range(1,printTo):

    if w in transitions.keys():
        people[people.index(transitions[w][0])] = transitions[w][1]
        assignedTasks[transitions[w][1]] = [""] * printTo
        taskBalance[transitions[w][1]] = {}
        for task in tasks:
            taskBalance[transitions[w][1]][task] = 0
    if w in excludeWeeks:
        continue
    for task in tasks:
        if (w+task.offset) % task.period == 0:
            duePerson = people[0]
            for p in people:
                duePerson = cmpBalance(p, duePerson, task, w)
            assignedTasks[duePerson][w] = assignedTasks[duePerson][w] + task.name + " "
            taskBalance[duePerson][task] -= len(people)*task.period
        for p in people:
            taskBalance[p][task] += 1



with open(planName + ".html", 'w') as f:
    print("<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>", file=f)
    print("<style> td{border:1px solid black; padding:15px;}</style>", file=f)
    print("<style> .exclude{  background-image: url(./tree.png); background-size: 50px 50px; }</style>", file=f)
    print("<style> .schedule{  background: repeating-linear-gradient(  45deg,  #FFFFFF,  #FFFFFF 10px,  #EEEEEE 10px,  #EEEEEE 20px); text-align:center}</style>", file=f)
    print("</head><body style=\"font-family: verdana\"><h1 style=\"text-align:center\">The Homely Homestead - Putzplan</h1><table style=\"margin: 0px auto\">", file=f)

    print("<tr><td></td>", file=f)
    for p in people:
        print("<td><b>" + p + "<b></td>", file=f);
    print("</tr>", file=f)

    currentDate = startDate
    for w in range(1,printTo):
        if w >= printFrom:
            if w in excludeWeeks:
                print( "<tr class=exclude>", file=f)
            else:
                print( "<tr>", file=f)
            print( "<td style=\"background-image:none;\">" + currentDate.strftime("KW%W, %d.%b") + " </td>", file=f)
            for p in people:
                if w not in excludeWeeks and assignedTasks[p][w] != "":
                    print("<td class=schedule> " + assignedTasks[p][w] + "</td>", file=f)
                else:
                    print("<td></td>", file=f)
            print("</tr>", file=f)
        currentDate += weekDelta

    print("</table>", file=f)
    for task in tasks:
        print("<p><h4 style=\"display:inline\">" + task.name + "</h4> - " + task.desc + "</p>", file=f)
    print("</body></html>", file=f)

with open(planName + ".bal", 'w') as f:
    for t in tasks:
        print( file=f)
        print( t.name + ' ' + str((t.offset + (printTo-printFrom)) % t.period),file=f)
        for p in people:
            print( p + ' ' + str(taskBalance[p][t]),file=f)
