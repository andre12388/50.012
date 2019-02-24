import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

fig_dirt = plt.figure()
fig_dirt.suptitle('Dirt Level Graph', fontsize= 16)
ax1 = fig_dirt.add_subplot(1,1,1)

fig_bacteria = plt.figure()
ax2 = fig_bacteria.add_subplot(1,1,1)
fig_bacteria.suptitle('Bacteria Level Graph', fontsize= 16)

fig_ph = plt.figure()
ax3 = fig_ph.add_subplot(1,1,1)
fig_ph.suptitle('Ph Level Graph', fontsize= 16)

fig_vitamin = plt.figure()
ax4 = fig_vitamin.add_subplot(1,1,1)
fig_vitamin.suptitle('Vitamin Level Graph', fontsize= 16)

def animate_dirt(i):
    pullData = open("dataSet_dirt.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
    ax1.clear()
    ax1.plot(xar,yar)

def animate_bacteria(i):
    pullData = open("dataSet_bacteria.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
    ax2.clear()
    ax2.plot(xar,yar)

def animate_ph(i):
    pullData = open("dataSet_ph.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
    ax3.clear()
    ax3.plot(xar,yar)

def animate_vitamin(i):
    pullData = open("dataSet_vitamin.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
    ax4.clear()
    ax4.plot(xar,yar)

plt.xlim([-100, 100])
plt.ylim([-100, 100])
ani_dirt = animation.FuncAnimation(fig_dirt, animate_dirt, interval=1000)
ani_bacteria = animation.FuncAnimation(fig_bacteria, animate_bacteria, interval=1000)
ani_ph = animation.FuncAnimation(fig_ph, animate_ph, interval=1000)
ani_vitamin = animation.FuncAnimation(fig_vitamin, animate_vitamin, interval=1000)

plt.show()