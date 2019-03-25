from flask import Flask, render_template, request
import requests

app = Flask("MyApp")

@app.route("/")
def login():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def sign_up():
    form_data = request.form
    email = form_data["email"]
    send_simple_message(email)
    return "All OK"

@app.route("/dashboard")
def hello_someone(name):
    return render_template("hello.html", name=name.title())

def send_simple_message(address):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org/messages",
		auth=("api", "dc8d31d20b0995dd1e58bfc3dc650cd6-de7062c6-b92fa5a7"),
		data={"from": "University of Bath Dashboard <mailgun@sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org>",
			"to": [address],
			"subject": "University made easier ;)",
			"text": "Thanks for signing up!"})


app.run(debug=True)
app.run(port=5050)
