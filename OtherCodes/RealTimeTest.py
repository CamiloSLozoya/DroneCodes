import time
measureTime=5 #Cantidad de segundos que espera para realizar la acción
t_start=time.gmtime()
t_next=t_start.tm_sec+measureTime
while True:
    t=time.gmtime()
    if (t.tm_sec==(t_next)):
        print(t.tm_sec) #Esto es opcional
#--------------------------------------------------------------------------------------------------------------
#Aquí pones lo que quieras que realize cada x tiempo
#--------------------------------------------------------------------------------------------------------------
        t_next=t.tm_sec+measureTime
        if (t_next>=60):
            t_next=t_next%60
    #time.sleep(1)


    
