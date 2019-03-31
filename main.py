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
    name = form_data["username"]
    course = form_data["course"]
    send_simple_message(email)
    articles = find_news()
    return render_template("hello.html", name=name.title(), articles=articles)

# sends a welcome email to users when they login
def send_simple_message(address):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org/messages",
		auth=("api", "dc8d31d20b0995dd1e58bfc3dc650cd6-de7062c6-b92fa5a7"),
		data={"from": "University of Bath Dashboard <mailgun@sandboxb298abe6bf9b4f2597ff936c91181223.mailgun.org>",
			"to": [address],
			"subject": "University made easier ;)",
			"text": "Thanks for signing up!"})


# will request the news articles 'Powered by NewsApi'
@app.route('/', methods=['GET'])
@cross_origin()
def find_news():
    newsapi = NewsApiClient(api_key='becec0b66fa741fb9868408992b4587a')

    # get all articles relating to users' course
    all_articles = newsapi.get_everything(q='brexit',
                                         sources='bbc-news, bloomberg, business-insider-uk, financial-times',
                                         domains='bbc.co.uk, bloomberg.com, uk.businessinsider.com, ft.com',
                                         from_param='2019-03-01',
                                         to='2019-03-20',
                                         language='en',
                                         sort_by='relevancy',
                                         page=2)
    return jsonify(all_articles)




app.run(debug=True)
app.run(port=5050)
