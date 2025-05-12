import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randrange
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.serial()

portList = []

for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))

val = input("select Port: COM")

print(val)

for x in range(0, len(portList)):
    if portList[x].startswith("COM"+ str(val)):
        portVar = "COM" + str(val)
        print(portList[x])

serialInst.baudrate = 115200
serialInst.port = portVar

serialInst.open()

while True:
    if serialInst.in_waiting:
        packet = serialInst.readline()
        print(packet.decode('utf'))

    fig = plt.figure(figsize=(6, 3))
    x = [0] #Valores iniciales
    y = [0]

    ln, = plt.plot(x, y, '-') #Parametros para dibujar la linea
    plt.axis([0, 100, 0, 1025]) # X de 0 a 100 / Y de 0 a 10

    def update(frame):
        x.append(x[-1] + 1)
        y.append(randrange(0,1024)) #
        ln.set_data(x, y) 
        return ln,
        
    animation = FuncAnimation(fig, update, interval=500)
    plt.show()