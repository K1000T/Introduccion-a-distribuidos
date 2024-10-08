import datetime
import random
import threading
from Sensor import Sensor
from time import sleep
import zmq
from threading import Thread

class SensorHumedad(Sensor, Thread):  
    def __init__(self, parametro1, parametro2):
        self.inicializado = threading.Event()
        Sensor.__init__(self, parametro1, parametro2)
        Thread.__init__(self) 
        self.rango_normal = (0.7, 1)
        self.inicializado.set()
        

    def run(self):
        while True:
            self.tomarMuestra()
            sleep(5)  
    
        

    def tomarMuestra(self):
        self.inicializado.wait()
        while True:
            probabilidades = {
            "correctos": self.pCorrecto,
            "fuera_rango": self.pFueraRango,
            "error": self.pError,
            }
            eleccion = random.choices(list(probabilidades.keys()), probabilidades.values())[0]

            if eleccion == "correctos":
                self.muestra['valor']= random.uniform(*self.rango_normal)
            elif eleccion == "fuera_rango":
                self.muestra['valor'] = random.uniform(self.rango_normal[1], self.rango_normal[1] + 5)
            else:
                self.muestra['valor'] = random.uniform(-5, 0)
                
            self.muestra['tipo'] = "humedad"
            self.muestra['hora'] = str(datetime.datetime.now())
            
            self.enviarMuestraProxy()
            sleep(5)

    
    def enviarMuestraProxy(self):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        #socket.bind("tcp://localhost:5555")
        socket.connect("tcp://localhost:5556")

        try:
            socket.send_pyobj(self.muestra)
            print("Muestra enviada al Proxy.")
        except zmq.ZMQError as e:
            print(f"Error al enviar la muestra: {e}")
        finally:
            socket.close()
            context.term()
