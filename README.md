# SMS-to-Strava

This is a Flask-based web handler for Twilio that allows for SMS-based creation of routes in Strava.

## Installation

1) Spin up an Ubuntu server and connect through SSH
2) Install the latest firefox and xvfb
3) Install python-pip
4) Install virtualenv with pip
5) Create a virtual environment and install all the packages in requirements.txt
6) Run the app with the command: python StravaMobileRouteApp.py
7) This will run the app at your server's IP address listening at port 8000
8) Buy a Twilio number that allows for SMS messaging
9) Set the Request URL for the Messaging to: http://IP-Address-of-Server:8000/

## Workflow

1) Send your email as SMS to the Twilio number
2) An automated prompt will ask you for your Strava password
3) Send your password as SMS to the Twilio number
4) An automated prompt will ask you for the start location
5) Send your start location to the Twilio number
6) An automated prompt will ask you for the end location
7) Send your end location to the Twilio number
8) The route is then automatically created in Strava
