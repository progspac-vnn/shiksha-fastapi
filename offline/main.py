from fastapi import FastAPI, Form
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import cv2
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio Client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# FastAPI App
app = FastAPI()

@app.post("/receive_sms")
async def receive_sms(From: str = Form(...), Body: str = Form(...), NumMedia: str = Form(...), MediaUrl0: str = Form(None)):
    """
    Handles incoming SMS/MMS from Twilio.
    If an image is attached, process it for face detection.
    """
    response = MessagingResponse()

    if int(NumMedia) > 0:  # If an image is received
        # Download the image from Twilio's URL
        image_url = MediaUrl0
        img_response = requests.get(image_url)
        
        if img_response.status_code == 200:
            # Convert the image to a numpy array
            nparr = np.frombuffer(img_response.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Load OpenCV face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Count faces
            face_count = len(faces)

            # Send SMS response with face count
            message = client.messages.create(
                body=f"Detected {face_count} face(s) in the image.",
                from_=TWILIO_PHONE_NUMBER,
                to=From
            )
            
            response.message(f"Processed image. Found {face_count} face(s).")
        else:
            response.message("Failed to process the image. Please try again.")
    else:
        response.message("Send an image to count the faces in it.")

    return str(response)