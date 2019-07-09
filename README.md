# About

A Python app to send a batch of emails to different addresses following a template

# Requirements

The only requirement is Python 3 which has the following libraries included:
- [configparser](https://docs.python.org/3/library/configparser.html)
- [email.mime](https://docs.python.org/3/library/email.mime.html) 
- [json](https://docs.python.org/3/library/json.html)
- [jsonschema](https://pypi.org/project/jsonschema/)
- [re](https://docs.python.org/3/library/re.html)
- [smtplib](https://docs.python.org/3/library/smtplib.html)

# To Run

1. Get credentials at your provider for sending emails programatically with SMTP (for gmail you can generate a token [here](https://security.google.com/settings/security/apppasswords))

2. Create a batch job file according to the following json schema (a batch file example is included in this repository):
```
{
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
```

3. Edit "settings.ini" file with your configuration. The following fields are required:
- `sender_email`: email address of the sender 
- `sender_token`: password or token for the sender
- `sender_name`: name of the sender as it appears on the receiver's inbox
- `batch_file`: file containing the batch job
- `stop_batch_if_error`: If "True", it will stop sending emails if an error occurs in one item of the batch
- `smtp_server_url` = Url for the SMTP server

4. Run command `python3 batch_email_sender.py`