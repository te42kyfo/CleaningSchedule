#!/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date, timedelta
from random import randint, seed, shuffle
import sqlite3

conn = sqlite3.connect('test2.db')

class Task:
    def __init__(self, name, period, offset, desc):
        self.name = name
        self.period = period
        self.offset = offset
        self.desc = desc


people = ["Anna", "Benni", "Dominik", "Sophia", "Philipp"]
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

    leastRecentlyAssigned = []
    weeksSinceAssignment = 0
    for p in leastAssignments:
        cursor = conn.execute("SELECT * FROM assignments" \
                              " WHERE task=? AND person=? ORDER BY WEEK DESC", (task.name, p))
        res = cursor.fetchall()
        if len(res) == 0:
            last = week
        else:
            last = week-res[0][3]

        if last == weeksSinceAssignment or len(leastRecentlyAssigned) == 0:
            leastRecentlyAssigned.append(p)
            weeksSinceAssignment = last
        if last > weeksSinceAssignment:
            leastRecentlyAssigned = [p]
            weeksSinceAssignment = last

    shuffle(leastRecentlyAssigned)

    return leastRecentlyAssigned[0]

def schedule(fromWeek, toWeek):
    for w in range(fromWeek,toWeek):
        for task in tasks:
            cursor = conn.execute("SELECT * FROM assignments WHERE task=? ORDER BY week DESC",
                                  (task.name,))
            res = cursor.fetchone()

            if (w - res[3]) >= task.period:
              candidate = selectBestCandidate(w, task)
              cursor = conn.execute("INSERT INTO assignments (week, person, task)" \
                                    "VALUES (?, ?, ?)", (w, candidate, task.name))

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
        print("<style> .schedule{  background: repeating-linear-gradient(  45deg,  "\
              "#FFFFFF,  #FFFFFF 10px,  #EEEEEE 10px,  #EEEEEE 20px);"
              "\text-align:center}</style>",
              file=f)
        print("</head><body style=\"font-family: verdana\"><h1 style=\"text-align:center\">" \
              "The Homely Homestead - Putzplan</h1><table style=\"margin: 0px auto\">", file=f)

        print("<tr><td></td>", file=f)
        for p in people:
            print("<td><b>" + p + "<b></td>", file=f);
        print("</tr>", file=f)

        currentDate = startDate + (fromWeek-1)*weekDelta
        for w in range(fromWeek,toWeek):
            print( "<tr>", file=f)
            print( "<td>" + currentDate.strftime("KW%W, %d.%b") + " </td>", file=f)
            for p in people:
                cursor = conn.execute("SELECT * FROM assignments WHERE person = ? AND week = ?",
                                      (p, w))
                res = cursor.fetchall()
                if len(res) != 0:
                    print("<td class=schedule>", file=f)
                    for row in res:
                        print ( row[2], file=f)
                else:
                    print("<td>", file=f)
                print("</td>", file=f)

            print("</tr>", file=f)
            currentDate += weekDelta

        print("</table>", file=f)
        for task in tasks:
            print("<p><h4 style=\"display:inline\">" + task.name +
                  "</h4> - " + task.desc + "</p>", file=f)
        print("</body></html>", file=f)


