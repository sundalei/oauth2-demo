# https://cloud.tencent.com/developer/article/1197066
from flask import Flask, url_for, render_template, request, redirect, jsonify
from markupsafe import escape
from furl import furl
import requests
import json
import os

app = Flask(__name__)
site_name = 'unsplash'

def config(site_name):
	path = os.path.join('config.json')
	json_config = json.load(open(path))
	oauth_config = json_config["supported"][site_name]['auth']
	return oauth_config
	

@app.route('/')
def index(name=None):
	return render_template('index.html', name=name)


@app.route('/login')
def login():
	oauth_config = config(site_name)

	auth_url = oauth_config['auth_url']
	client_id = oauth_config['client_id']
	scope = oauth_config['scope']
	redirect_uri = oauth_config['redirect_uri']

	params = {
		'client_id': client_id,
		'response_type': 'code',
		'scope': scope,
		'redirect_uri': redirect_uri
	}
	url = furl(auth_url).set(params)
	return redirect(url, 302)


@app.route('/oauth2/<service>/callback')
def oauth2_callback(service):
	oauth_config = config(site_name)

	client_id = oauth_config['client_id']
	client_secret = oauth_config['client_secret']
	redirect_uri = oauth_config['redirect_uri']
	access_token_url = oauth_config['access_token_url']
	code = request.args.get('code')

	payload = {
		'code': code,
		'redirect_uri': redirect_uri,
		'grant_type': 'authorization_code',
		'client_id': client_id,
		'client_secret': client_secret,
	}
	result = requests.post(access_token_url, json=payload, headers={'Accept': 'application/json'})

	if result.status_code == 200:
		body = json.loads(result.text)
		access_token = body['access_token']
		refresh_token = body['refresh_token']
		
		access_user_url = 'https://api.unsplash.com/photos'
		result = requests.get(access_user_url, headers={'Authorization': 'Bearer ' + access_token})
		
		params = {
			'access_token': access_token,
			'refresh_token': refresh_token,
		}
		redirect_index = 'http://127.0.0.1:5000/#'
		redirect_index = furl(redirect_index).set(params)
		return redirect(redirect_index, 302)


if __name__ == '__main__':
	app.run(debug=True)