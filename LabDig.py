import cv2
import numpy as np
import os
import argparse
import face_recognition
import time
import serial
import glob
from PIL import Image

def reset_db():
    #cargar imagen de base de datos
    known_faces = []
    known_names = []
    root_db=glob.glob('db/*.jpeg')
    for filename in root_db: 
        user_id=(filename.split('\\'))[-1].split('.')[0] #'db\\id.jpeg' --> 'id'
        image=face_recognition.load_image_file(filename)
        image_encodings = face_recognition.face_encodings(image)[0]
        known_faces.append(image_encodings)
        known_names.append(user_id)
    return known_faces, known_names

def DataBase(user_id):     
    #captura de video
    url = "http://192.168.31.15:8080/video"
    cap = cv2.VideoCapture(url)    
    ret, frame = cap.read() #Linea para probar con camara ip  
    frame = frame[:, :, ::-1]
    
    
    #cv2.imshow('frame',frame)
    #cv2.waitKey()
    #frame = face_recognition.load_image_file("juliancontreras.jpg")

    face_locations = face_recognition.face_locations(frame, model="cnn")
    print("n de caras: ",len(face_locations))
    if len(face_locations) == 1:
        top, right, bottom, left = face_locations[0]
        face_image = frame[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        #cv2.imshow('frame',face_image)
        #cv2.waitKey()
        pil_image.save("db/"+user_id+".jpeg")
        return True
        #pil_image.show()
    else:        
        print("To many faces or Faces not detected")
        return False

def FaceDetect(known_faces, known_names): #Para probar con camara ip reemplazar def FaceDetect(cap):
    start_time = time.time()
    count=0
    frames=10 #Numero de fotos necesarias para la detección
    for i in range(frames): 
        #leer imagen desde camara ip
        url = "http://192.168.31.15:8080/video"
        cap = cv2.VideoCapture(url) 
        ret, frame = cap.read() #Linea para probar con camara ip        
        #frame=cv2.imread("check.jpeg") #Linea para probar sin camara ip

        #resize imagen, apurar procesamiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        #conversión BGR to RGB
        rgb_small_frame = small_frame[:, :, ::-1]

        #inicializacion nombres
        names = []

        #solo procesar si esta activo el video

        #procesar imagen, buscando caras
        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        if (face_locations==[]):
            match=[]
        else:
            #comparar caras
            match = face_recognition.compare_faces(np.array(known_faces), face_encodings[0], tolerance=0.6)   

        name = "Unknown"
        if True in match: #Se detectó una cara
            count+=1
            for i in range(len(match)):
                #buscar similitud
                if match[i]:
                    name = known_names[i]
                    break
                    
        names.append(name) #Lista donde se guardan los nombres detectados
        
    count_names=[[x,names.count(x)] for x in set(names)] #cuenta los nombres detectados
    if count > 7 and len(count_names)==1: #Si en 7 de las 10 imagenes detecta la misma cara, se envia comando a arduino
        print("Elapsed Time: {}".format(time.time() - start_time))
        print("Acc: ",count*100/10, "%")
        return True
    return False



def main():
    known_faces, known_names = reset_db()
    arduino = serial.Serial("COM3", baudrate=9600, timeout=1.0)
    time.sleep(2)
    start=time.time()
    print("Press a Button, red for save, green for detect.")
    while arduino:    
        rawString = arduino.readline() #Se lee linea de arduino
        string_n=rawString.decode()    #bin -> dec
        string = string_n.rstrip()     #eliminación de \n y \r
        end=time.time()
        
        ##RELLENAR PARTE DE SAVE 
        if (string=="RedButton"): #Save
            print("Red Button, ",round(end-start), "s")
            user_id=int(known_names[-1])+1 #Se le suma 1 al ultimo usuario registrado
            is_face=DataBase(str(user_id))              #Captura y guarda una imagen a la base de datos        
            if is_face:
                known_faces, known_names = reset_db() 
                arduino.write(b'1')            #Avisa a arduino que se guardo la imagen
                print("Face Saved as user ",user_id)
            else:
                arduino.write(b'0')            #Avisa a arduino que no hay o hay muchas caras 

            time.sleep(1.2)
            print("Press Again...")  
            
            start=time.time()
            
        elif (string=='GreenButton'): #Detect
            print("Green Button, ",round(end-start), "s")
            detect=FaceDetect(known_faces, known_names) #Funcion de detectar la cara 
            #detect=FaceDetect(cap) ##Para uso de camara ip quitar comentario
            if detect:
                arduino.write(b'1') #Escribe un 1 binario en la Serial de arduino
                
            else:
                arduino.write(b'0') #Escribe un 0 binario en la Serial de arduino
                
            time.sleep(1.2)
            print("Press Again...")
            start=time.time()
        
        elif ((end-start)>=10000):
            break
    print("Time out: ",round(end-start), "s")
    arduino.close()

if __name__ == "__main__":
    main()
    
