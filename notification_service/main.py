from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

app = FastAPI()

# Pydantic models for request validation
class AppointmentNotification(BaseModel):
    patient_email: str
    appointment_time: str
    doctor_name: str
    status: str

class NotificationResponse(BaseModel):
    message: str


# Email settings (adjust as per your email provider)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Replace with your email
SENDER_PASSWORD = "your-email-password"  # Replace with your email password

# Function to send email notifications
def send_email(receiver_email: str, appointment_time: str, doctor_name: str, status: str):
    try:
        # Setup the MIME
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = receiver_email
        message["Subject"] = "Appointment Notification"
        
        # Email body content
        body = f"Dear Patient,\n\nYou have an upcoming appointment with Dr. {doctor_name} at {appointment_time}.\nStatus: {status}\n\nBest regards,\nNotification Service"
        message.attach(MIMEText(body, "plain"))
        
        # Connect to the SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = message.as_string()
            server.sendmail(SENDER_EMAIL, receiver_email, text)
        
        return "Email sent successfully"
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")


# API Endpoint to trigger notification
@app.post("/send-notification/", response_model=NotificationResponse)
async def send_appointment_notification(notification: AppointmentNotification):
    try:
        # Send the email
        response_message = send_email(
            notification.patient_email,
            notification.appointment_time,
            notification.doctor_name,
            notification.status
        )
        return NotificationResponse(message=response_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
