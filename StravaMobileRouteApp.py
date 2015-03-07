# How this works
# 1) SMS Strava login + route points via Twilio (+1.267.578.7282)
# 2) Save SMS data to Parse
# 3) Create Strava route with Selenium 

import twilio.twiml
import json,httplib,urllib
from strava import create_route
from flask import Flask, request

app = Flask(__name__)

PARSE_APP_ID = "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K"
PARSE_APP_KEY = "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"


@app.route("/", methods=['GET', 'POST'])
def hello():

	from_number = request.values.get('From')
	body = request.values.get('Body')

	resp = twilio.twiml.Response()

	try:
		connection = httplib.HTTPSConnection('api.parse.com', 443)
		params = urllib.urlencode({"where":json.dumps({
		       "phone": from_number
		     })})
		connection.connect()
		connection.request('GET', '/1/classes/Rider?%s' % params, '', {
		       "X-Parse-Application-Id": PARSE_APP_ID,
		       "X-Parse-REST-API-Key": PARSE_APP_KEY
		     })
		result = json.loads(connection.getresponse().read())
		print result

		if result["results"][0]["email"]:
			if result["results"][0]["password"]:
				if result["results"][0]["point_a"]:
					if result["results"][0]["point_b"]:
						connection.connect()
						connection.request('DELETE', '/1/classes/Rider/%s' % result["results"][0]["objectId"], '', {
							"X-Parse-Application-Id": PARSE_APP_ID,
							"X-Parse-REST-API-Key": PARSE_APP_KEY
						})
					else:
						resp.message("Your route is ready! https://www.strava.com/athlete/routes")
						
						#add point_b
						connection.connect()
						connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
							"point_b": body
						}), {
							"X-Parse-Application-Id": PARSE_APP_ID,
							"X-Parse-REST-API-Key": PARSE_APP_KEY,
							"Content-Type": "application/json"
						})

						# get data for route
						connection = httplib.HTTPSConnection('api.parse.com', 443)
						params = urllib.urlencode({"where":json.dumps({
						       "objectId": result["results"][0]["objectId"]
						     })})
						connection.connect()
						connection.request('GET', '/1/classes/Rider?%s' % params, '', {
						       "X-Parse-Application-Id": PARSE_APP_ID,
						       "X-Parse-REST-API-Key": PARSE_APP_KEY
						     })
						result = json.loads(connection.getresponse().read())

                        # Define the parameters
                        user_email = result["results"][0]["email"]
                        user_password = result["results"][0]["password"]
                        loc1 = result["results"][0]["point_a"]
                        loc2 = result["results"][0]["point_b"]
                        
                        # Create route in Strava
                        create_route(user_email, user_password, loc1, loc2)
                        
						connection.request('DELETE', '/1/classes/Rider/%s' % result["results"][0]["objectId"], '', {
							"X-Parse-Application-Id": PARSE_APP_ID,
							"X-Parse-REST-API-Key": PARSE_APP_KEY
						})

						return str(resp)

				else:
					#add point_a
					connection.connect()
					connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
						"point_a": body
					}), {
						"X-Parse-Application-Id": PARSE_APP_ID,
						"X-Parse-REST-API-Key": PARSE_APP_KEY,
						"Content-Type": "application/json"
					})
					resp.message("What's your ending location?")
			else:
				# add their password
				connection.connect()
				connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
					"password": body
				}), {
					"X-Parse-Application-Id": PARSE_APP_ID,
					"X-Parse-REST-API-Key": PARSE_APP_KEY,
					"Content-Type": "application/json"
				})
				resp.message("What's your starting location?")
		else:
			# add their email
			connection.connect()
			connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
				"email": body
			}), {
				"X-Parse-Application-Id": PARSE_APP_ID,
				"X-Parse-REST-API-Key": PARSE_APP_KEY,
				"Content-Type": "application/json"
			})
			resp.message("What's your password?")
	except:
		#create a record
		connection.connect()
		connection.request('POST', '/1/classes/Rider', json.dumps({
			"phone": from_number,
			"email": '',
			"password": '',
			"point_a": '',
			"point_b": ''
		}), {
			"X-Parse-Application-Id": PARSE_APP_ID,
			"X-Parse-REST-API-Key": PARSE_APP_KEY,
			"Content-Type": "application/json"
		})
		resp.message("What's your email?")

	return str(resp)

if __name__ == "__main__":
	app.run(debug=True)
