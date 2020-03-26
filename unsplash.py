# https://cloud.tencent.com/developer/article/1197066
from flask import Flask, url_for, render_template, request, redirect, jsonify
from markupsafe import escape
from furl import furl
import requests
import json

# github生成的两把钥匙
client_id = 'ee30dc2b9d62ada98d08a69460e89785479f5b7abf33e275df16fbbe93188d75'
client_secret = '53b390ec95b33b9dc7f49e12985353c650c10cb84ac5e1c0065f7780f919918c'

app = Flask(__name__)

@app.route('/spotify')
def spotify_app():
	spotify_auth_url = 'https://accounts.spotify.com/authorize'
	spotify_client_id = '29105ab2d56547ac8ba6171418363689'
	spotify_client_secret = '78ba77653d0f410196a3ba96c89406cb'
	spotify_scope = 'user-read-private user-read-email'

	params = {
		'client_id': spotify_client_id,
		'response_type': 'code',
		'scope': spotify_scope,
		'redirect_uri': 'http://localhost:5000/oauth2/spotify/callback',
	}
	url = furl(spotify_auth_url).set(params)
	return redirect(url, 302)


@app.route('/', methods=['GET', 'POST'])
def index():
	url = 'https://unsplash.com/oauth/authorize'
	params = {
		'client_id': client_id,
		'redirect_uri': 'http://127.0.0.1:5000/oauth2/splash/callback',
        'response_type': 'code',
		'scope': 'public',
		'state': 'An unguessable random string.',
		'allow_signup': 'true'
	}
	url = furl(url).set(params)
	return redirect(url, 302)


@app.route('/oauth2/<service>/callback')
def oauth2_callback(service):
	code = request.args.get('code')
	if service == 'spotify':
		oauth2_callback_spotify(code)
	if service == 'unsplash':
		oauth2_callback_unsplash(code)

def oauth2_callback_spotify(code):
	return 'hello world'


def oauth2_callback_unsplash(code):
	# 根据返回的code获取access token
	access_token_url = 'https://unsplash.com/oauth/token'
	payload = {
		'client_id': client_id,
		'client_secret': client_secret,
		'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:5000/oauth2/splash/callback',
		'state': 'An unguessable random string.'
	}
	r = requests.post(access_token_url, json=payload, headers={'Accept': 'application/json'})
	access_token = json.loads(r.text).get('access_token')

	access_user_url = 'https://api.unsplash.com/photos'
	r = requests.get(access_user_url, headers={'Authorization': 'Bearer ' + access_token})
	# print(json.loads(r.text)[0]['urls']['regular'])
	urls = []
	for url in json.loads(r.text):
		urls.append(url['urls']['regular'])
	return jsonify({
		'status': 'success',
		'data': urls
	})


if __name__ == '__main__':
	app.run(debug=True)