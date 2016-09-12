#!/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date, timedelta
from random import randint, seed, shuffle, random
import sqlite3
import numbers

conn = sqlite3.connect('test4.db')

class Task:
    def __init__(self, name, period, offset, desc):
        self.name = name
        self.period = period
        self.offset = offset
        self.desc = desc


people = ["Philipp", "Anna", "Benni", "Dominik", "Sophia"]
tasks = [Task("KüPu", 1.1, 0, ("Küche Aufräumen. Flächen, Herd und Tisch "
                              "aufräumen und abwischen. Alle Mülleimer leeren. "
                              "Spülmaschine leeren/anmachen/füllen. "
                               "Den Boden immer kehren und wischen!")),
         Task("GaPu", 6, 3, ("Gang Putzen. Kehren oder Wischen, nach eigenem Ermessen")),
         Task("Klos", 1.1, 0, ("Beide Klos putzen")),
         Task("WaBe", 2.1, 1, ("Waschbecken + Spiegel in beiden Toiletten putzen")),
         Task("GlaMü", 8, 4,("Glas Müll wegbringen") ),
         Task("Surp", 3.0, 0, ("Surprise Task. Putze irgendetwas das dreckig ist"))]

for t in tasks:
    t.period *= 5 / len(people)

tasks.sort(key= lambda task:  -task.period)
seed(1)

def selectBestCandidate(week, task):
    leastAssignments = []
    assignmentCount = -1
    for p in people:
        cursor = conn.execute("SELECT * FROM assignments WHERE week=? AND person=?",
                              (week, p))
        res = cursor.fetchall()
        if len(res) == assignmentCount or assignmentCount == -1:
            leastAssignments.append(p)
            assignmentCount = len(res)
        if len(res) < assignmentCount:
            leastAssignments = [p]
            assignmentCount = len(res)

    print( leastAssignments )
    leastRecentlyAssigned = []
    weeksSinceAssignment = 0
    avPeriod = task.period * len(people)
    for p in leastAssignments:
        cursor = conn.execute("SELECT week FROM assignments" \
                              " WHERE task=? AND person=? ORDER BY WEEK DESC", (task.name, p))
        res = cursor.fetchall()

        events = [0,0,0,0]

        events[0] = avPeriod * 1.25
        if len(res) > 0:
            events[0] = week-res[0][0]

        events[1] = events[0] + avPeriod * 1.25
        if len(res) > 1:
            events[1] = week-res[1][0]

        events[2] = events[1] + avPeriod * 1.25
        if len(res) > 2:
            events[2] = week-res[2][0]

        events[3] = events[2] + avPeriod * 1.25
        if len(res) > 3:
            events[3] = week-res[3][0]

        last = (events[0] + events[1] * 0.9 + events[2] * 0.5 + events[3] * 0.1)/2.5

        print(str(week) + " " + task.name + " " + p + " " + str(last));

        if last == weeksSinceAssignment or len(leastRecentlyAssigned) == 0:
            leastRecentlyAssigned.append(p)
            weeksSinceAssignment = last
        if last > weeksSinceAssignment:
            leastRecentlyAssigned = [p]
            weeksSinceAssignment = last

    shuffle(leastRecentlyAssigned)
    print( leastRecentlyAssigned )
    print()

    return (leastRecentlyAssigned[0], round(weeksSinceAssignment/avPeriod,2))

def schedule(fromWeek, toWeek):
    for w in range(fromWeek,toWeek):
        for task in tasks:
            cursor = conn.execute("SELECT * FROM assignments WHERE task=? ORDER BY week DESC",
                                  (task.name,))
            res = cursor.fetchall()
            if len(res) == 0:
                weeksSinceAssignment = 1 + w - fromWeek + task.offset
            else:
                weeksSinceAssignment = w-res[0][3]
            if weeksSinceAssignment >= round(task.period  + random() *0.49):
              (candidate, balance) = selectBestCandidate(w, task)
              cursor = conn.execute("INSERT INTO assignments (week, person, task, balance)" \
                                    "VALUES (?, ?, ?, ?)",
                                    (w, candidate, task.name, balance ))

def printHTML(fromWeek, toWeek):
    startDate = date(2015, 10, 12)
    weekDelta = timedelta(weeks=1)
    planName = ((startDate + fromWeek*weekDelta).strftime("%WY%y") + "-"
                + (startDate + toWeek*weekDelta).strftime("%WY%y"))

    print(planName)
    with open(planName + ".html", 'w') as f:
        print("<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; " \
              "charset=utf-8\"/>", file=f)
        print("<style> td{border:1px solid black; padding:15px;}</style>", file=f)
        print("<style> .exclude{  background-image: url(./tree.png);" \
              "background-size: 50px 50px; }</style>", file=f)
        print("<style> .schedule{  background: repeating-linear-gradient(  45deg,  "
              "#FFFFFF,  #FFFFFF 10px,  RGBA(0,0,0,0.5) 10px,  RGBA(0,0,0,0.5) 20px);"
              "text-align:center}</style>",
              file=f)
        print("</head><body style=\"font-family: verdana\"><h1 style=\"text-align:center\">" \
              "The Homely Homestead - Putzplan</h1><table style=\"margin: 0px auto\">", file=f)

        print("<tr><td><b>KW, Beginn</b></td>", file=f)
        for p in people:
            print("<td><b>" + p + "<b></td>", file=f);
        print("</tr>", file=f)

        currentDate = startDate + (fromWeek-1)*weekDelta
        for w in range(fromWeek,toWeek):
            print( "<tr>", file=f)
            print( "<td>" + currentDate.strftime("KW%W, ab %d.%b") + " </td>", file=f)
            for p in people:
                cursor = conn.execute("SELECT task, balance FROM assignments "
                                      "WHERE person = ? AND week = ?", (p, w))
                res = cursor.fetchall()
                if len(res) != 0:
                    if isinstance(res[0][1], numbers.Number):
                        intensity = round(min(max((res[0][1]-1.0)*0.05, 0.0), 0.25), 2)
                    else:
                        intensity = 0.1

                    intensity = round(255-intensity*255)
                    color = ("RGB(" + str(intensity) + ","
                             + str(intensity) + "," + str(intensity) + ")")
                    print("<td style=\"background: repeating-linear-gradient(45deg,"
                          "#FFFFFF,  #FFFFFF 10px,"
                          +color+ " 10px," + color + " 20px); text-align:center\">",
                          file=f)

                    for row in res:
                        print ( row[0], file=f)
                else:
                    print("<td>", file=f)
                print("</td>", file=f)

            print("</tr>", file=f)
            currentDate += weekDelta

        print("</table>", file=f)
        for task in tasks:
            print("<p><h4 style=\"display:inline\">" + task.name +
                  "</h4> (" + str(task.period) + ") - " + task.desc + "</p>", file=f)
        print("</body></html>", file=f)


