import cv2
import numpy as np
import os
import pyodbc
from datetime import datetime
import subprocess
import sys
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def is_camera_pinging(ip_address):
    # Execute the ping command
    process = subprocess.Popen(['ping', '-n', '1', '-w', '1000', ip_address], stdout=subprocess.PIPE)
    output, _ = process.communicate()

    # Check the output for a successful ping
    if "Reply from {}".format(ip_address) in output.decode():
        return True
    else:
        return False

def read_camera_detail():
    # Connect to the SQL Server database
    cnxn = pyodbc.connect("Driver={SQL Server};"
                          "Server=LAPTOP-C3GTL6B2\SQLEXPRESS;"
                          "Database=Camera_Data;"
                          "Trusted_Connection=yes;")
    try:
        # Create a cursor object to execute SQL queries
        cursor = cnxn.cursor()

        # Fetch all camera credentials from the database
        cursor.execute("SELECT * FROM camera_detail")
        rows = cursor.fetchall()

        # Create a list to store the camera credentials
        camera_detail = []

        # Iterate over the rows and extract the credentials
        for row in rows:
            ip_address, username, password, rtsp_port = row
            camera_detail.append({
                'ip_address': ip_address,
                'username': username,
                'password': password,
                'rtsp_port': rtsp_port
            })

        return camera_detail
    except Exception as e:
        print("Error occurred while fetching camera credentials from the database:", e)
        return None
    finally:
        # Close the database connection
        cnxn.close()

def read_email_config():
    # Connect to the SQL Server database
    cnxn = pyodbc.connect("Driver={SQL Server};"
                          "Server=LAPTOP-C3GTL6B2\SQLEXPRESS;"
                          "Database=Camera_Data;"
                          "Trusted_Connection=yes;")
    try:
        # Create a cursor object to execute SQL queries
        cursor = cnxn.cursor()

        # Fetch the email configuration from the database
        cursor.execute("SELECT * FROM email_config")
        row = cursor.fetchone()

        # Check if the email configuration is available
        if row:
            smtp_host, smtp_port, sender_email, sender_password, receiver_email, cc_emails = row

            # Parse the CC emails as a list
            cc_emails = cc_emails.split(',')

            email_config = {
                'smtp_host': smtp_host,
                'smtp_port': smtp_port,
                'sender_email': sender_email,
                'sender_password': sender_password,
                'receiver_email': receiver_email,
                'cc_emails': cc_emails
            }

            return email_config
        else:
            print("No email configuration found in the database.")
            return None
    except Exception as e:
        print("Error occurred while fetching email configuration from the database:", e)
        return None
    finally:
        # Close the database connection
        cnxn.close()

# Read camera credentials from the database
camera_detail = read_camera_detail()

# Check if camera credentials are fetched successfully
if camera_detail:
    # Read email configuration from the database
    email_config = read_email_config()

    # Check if email configuration is fetched successfully
    if email_config:
        # Specify the time to capture images (e.g., 12:00 PM)
        # capture_time = "13:04"

        while True:
            # Get the current time
            # current_time = datetime.now().strftime("%H:%M")

            # Check if it is the capture time
            # if current_time == capture_time:
                captured_images = []

                for camera_credential in camera_detail:
                    # Extract the credentials
                    ip_address = camera_credential.get('ip_address')
                    username = camera_credential.get('username')
                    password = camera_credential.get('password')
                    rtsp_port = camera_credential.get('rtsp_port')

                    # Check if the necessary credentials are present
                    if not all([ip_address, username, password, rtsp_port]):
                        print("Incomplete camera credentials for IP address:", ip_address)
                        continue

                    # Check if the camera is pinging
                    if is_camera_pinging(ip_address):
                        # Create the RTSP URL for the IP camera stream
                        rtsp_url = f"rtsp://{username}:{password}@{ip_address}:{rtsp_port}/live"

                        # Connect to the IP camera stream
                        camera = cv2.VideoCapture(rtsp_url)

                        # Check if the camera stream is opened successfully
                        if not camera.isOpened():
                            print("Failed to open IP camera stream for IP address:", ip_address)
                            continue

                        # Capture a single frame from the camera stream
                        ret, frame = camera.read()

                        # Check if the frame capture was successful
                        if not ret:
                            print("Failed to capture frame from camera with IP address:", ip_address)
                            camera.release()
                            continue

                        # Release the camera stream
                        camera.release()

                        # Create a folder to store the captured images
                        save_folder = 'E://Captured_Images'

                        # Generate the filename using the IP address
                        filename = ip_address.replace(".", "_") + ".jpg"

                        # Save the captured image
                        save_path = os.path.join(save_folder, filename)
                        cv2.imwrite(save_path, frame)

                        # Add the image path to the list of captured images
                        captured_images.append(save_path)

                        print("Image captured from camera with IP address", ip_address, "and saved as", filename)
                    else:
                        print("Camera", ip_address, "is not pinging.")

                # Send the captured images as email attachments
                if captured_images:
                    # Email configuration
                    smtp_host = email_config['smtp_host']
                    smtp_port = email_config['smtp_port']
                    sender_email = email_config['sender_email']
                    sender_password = email_config['sender_password']
                    receiver_email = email_config['receiver_email']
                    cc_emails = email_config['cc_emails']

                    # Create a multipart message object
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = 'Captured Images'
                    msg['CC'] = ', '.join(cc_emails)

                    # Attach the captured images to the email
                    for image_path in captured_images:
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        image = MIMEImage(image_data)
                        image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                        msg.attach(image)

                    # Send the email
                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)

                    print("Captured images sent via email.")

                    # Delete the captured images
                    for image_path in captured_images:
                        os.remove(image_path)

                    print("Captured images deleted.")

                # Exit the while loop after capturing and processing images
                break

            # else:
            #     # Wait for 60 seconds before checking the capture time again
            #     time.sleep(60)

    else:
        print("No email configuration found in the database.")
else:
    print("No camera credentials found in the database.")
