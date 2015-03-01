# How this works
# 1) SMS Strava login + route points via Twilio (+1.267.578.7282)
# 2) Save SMS data to Parse
# 3) Create Strava route with Selenium 

from flask import Flask, request
import twilio.twiml
import json,httplib,urllib
import time
from pyvirtualdisplay import Display
from selenium import webdriver

app = Flask(__name__)

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
		       "X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
		       "X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"
		     })
		result = json.loads(connection.getresponse().read())
		print result

		if result["results"][0]["email"]:
			if result["results"][0]["password"]:
				if result["results"][0]["point_a"]:
					if result["results"][0]["point_b"]:
						connection.connect()
						connection.request('DELETE', '/1/classes/Rider/%s' % result["results"][0]["objectId"], '', {
							"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
							"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"
						})
					else:
						resp.message("Your route is ready! https://www.strava.com/athlete/routes")
						
						#add point_b
						connection.connect()
						connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
							"point_b": body
						}), {
							"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
							"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
							"Content-Type": "application/json"
						})

						# get data for route
						connection = httplib.HTTPSConnection('api.parse.com', 443)
						params = urllib.urlencode({"where":json.dumps({
						       "objectId": result["results"][0]["objectId"]
						     })})
						connection.connect()
						connection.request('GET', '/1/classes/Rider?%s' % params, '', {
						       "X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
						       "X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"
						     })
						result = json.loads(connection.getresponse().read())

						# launch browser
						# if selenium has firefox problems see this Stack Overflow question
						# http://stackoverflow.com/questions/6682009/selenium-firefoxprofile-exception-cant-load-the-profile/25645344#25645344
						display = Display(visible=0, size=(1440, 800))
						display.start()
						browser = webdriver.Firefox()

						#log in
						browser.get('http://www.strava.com/routes/new')
						time.sleep(1)
						email = browser.find_element_by_name("email")
						email.send_keys(result["results"][0]["email"])
						password = browser.find_element_by_name("password")
						password.send_keys(result["results"][0]["password"])
						loginButton = browser.find_element_by_id('login-button')
						loginButton.click()
						time.sleep(3)

						#input first location
						locationField = browser.find_element_by_css_selector('.input-lg')
						locationField.send_keys(result["results"][0]["point_a"])
						locationFieldButton = browser.find_element_by_css_selector('.icon')
						locationFieldButton.click()
						time.sleep(3)
						canvas = browser.find_element_by_xpath('//*[@id="map-canvas"]/div/div[1]/div[2]')
						canvas.click()
						time.sleep(3)

						#input second location
						locationField.clear()
						locationField.send_keys(result["results"][0]["point_b"])
						locationFieldButton = browser.find_element_by_css_selector('.icon')
						locationFieldButton.click()
						time.sleep(3)
						canvas = browser.find_element_by_xpath('//*[@id="map-canvas"]/div/div[1]/div[2]')
						canvas.click()
						time.sleep(3)

						#save and name route
						saveButton = browser.find_element_by_css_selector('.save-route')
						saveButton.click()
						routeName = browser.find_element_by_id('name')
						routeName.send_keys(result["results"][0]["point_a"] + " to " + result["results"][0]["point_b"])
						submitButton = browser.find_element_by_css_selector('.submit')
						submitButton.click()

						browser.quit()

						display.stop()

						connection.request('DELETE', '/1/classes/Rider/%s' % result["results"][0]["objectId"], '', {
							"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
							"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"
						})

						return str(resp)

				else:
					#add point_a
					connection.connect()
					connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
						"point_a": body
					}), {
						"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
						"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
						"Content-Type": "application/json"
					})
					resp.message("What's your ending location?")
			else:
				# add their password
				connection.connect()
				connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
					"password": body
				}), {
					"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
					"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
					"Content-Type": "application/json"
				})
				resp.message("What's your starting location?")
		else:
			# add their email
			connection.connect()
			connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
				"email": body
			}), {
				"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
				"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
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
			"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
			"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
			"Content-Type": "application/json"
		})
		resp.message("What's your email?")

	return str(resp)

if __name__ == "__main__":
	app.run(debug=True)
