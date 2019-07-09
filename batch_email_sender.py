import os
import re
import configparser
import smtplib
import json
import jsonschema
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BATCH_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "subject": {
            "type": "string"
        },
        "body_template": {
            "type": "string"
        },
        "recipients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string"
                    },
                    "template_params": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "address",
                    "template_params"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "subject",
        "body_template",
        "recipients"
    ],
    "additionalProperties": False
}

def send_email(smtp_server, sender, recipient, subject, body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{sender[2]} <{sender[0]}>"
    msg['To'] = recipient
    mime_text = MIMEText(body, 'plain')
    msg.attach(mime_text)

    try:    
        smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception as e:
        print(e)
        return False
    return True

def stop_program(item_count):
    print(f"Program will stop due to error on batch item {item_count}")
    exit()

if __name__ == '__main__':
    
    # Load config file
    settings_file = 'settings.ini'
    try:
        config = configparser.ConfigParser()
        config.read(settings_file)      
        batch_file = config['CONFIGURATION']['batch_file']
        smtp_server_url = config['CONFIGURATION']['smtp_server_url']
        stop_batch_if_error = (config['CONFIGURATION']['stop_batch_if_error'] == "True")
        sender_email = config['CONFIGURATION']['sender_email']
        sender_token = config['CONFIGURATION']['sender_token']
        sender_name = config['CONFIGURATION']['sender_name']
        sender = (sender_email, sender_token, sender_name)
    except Exception as e:
        print(f"Error: '{settings_file}' not found or invalid. {e}")
        exit()

    # Load batch file
    try:
        with open(batch_file, 'r') as f:
            batch = json.loads(f.read())
        jsonschema.validate(instance=batch, schema=BATCH_JSON_SCHEMA)
    except Exception as e:
        print(f"Error: '{batch_file}' not found or invalid. {e}")   
        exit()

    # Log into server
    smtp_server = smtplib.SMTP(smtp_server_url)
    smtp_server.starttls()
    try:
       smtp_server.login(sender[0], sender[1])
    except smtplib.SMTPAuthenticationError as e:
        print("SMTPAuthenticationError: check your credentials. Exiting program...")
        smtp_server.quit()
        exit()

    # Send emails
    item_count = 0
    for item in batch["recipients"]:
        
        # Print completion rate
        item_count = item_count + 1
        batch_completion = (item_count / len(batch["recipients"])) * 100.0
        send_to = item["address"]
        print(f"({batch_completion:.2f}%) Processing batch item {item_count} for address '{send_to}'")

        # Check if email address is valid   
        if(not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", send_to)):
            print(f"Batch item {item_count} has invalid email address '{send_to}'")
            if(stop_batch_if_error):
                stop_program(item_count)
            else:
                continue

        # Create email body
        email_body = batch["body_template"]
        param_count = 0
        for param in item["template_params"]:
            email_body = email_body.replace(f"[{param_count}]", param)
            param_count = param_count + 1

        # Send email
        if(not send_email(smtp_server, sender, send_to, batch["subject"], email_body)):
            print(f"Error while sending email to '{send_to}'")
            if(stop_batch_if_error):
                stop_program(item_count)

    smtp_server.quit()
    print("Done")