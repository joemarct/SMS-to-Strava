from flask import Flask, request, redirect
import twilio.twiml
import json,httplib,urllib
from splinter import Browser 
import time
from pyvirtualdisplay import Display
from selenium import webdriver

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():

	from_number = request.values.get('From')
	body = request.values.get('Body')

	print from_number
	print body

	connection = httplib.HTTPSConnection('api.parse.com', 443)

	resp = twilio.twiml.Response()

	try:
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
			print "1"
			if result["results"][0]["password"]:
				print "2"
				if result["results"][0]["point_a"]:
					print "3"
					if result["results"][0]["point_b"]:
						print "yo. deleting"
						connection.request('DELETE', '/1/classes/Rider/%s' % result["results"][0]["objectId"], '', {
							"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
							"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq"
						})
					else:
						resp.message("Your route will be available shortly! https://www.strava.com/athlete/routes")
						return str(resp)
						#add point_b
						connection.request('PUT', '/1/classes/Rider/%s' % result["results"][0]["objectId"], json.dumps({
							"point_b": body
						}), {
							"X-Parse-Application-Id": "AOJncxqz885qqhXNcjrvgWrozTAAXPoMwezKue1K",
							"X-Parse-REST-API-Key": "HTwOFGukRZClAFrQezSKMDtcYhKtsL8alF64EFdq",
							"Content-Type": "application/json"
						})

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

				else:
					#add point_a
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
