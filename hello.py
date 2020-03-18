# https://cloud.tencent.com/developer/article/1197066
from flask import Flask, url_for, render_template, request, redirect, jsonify
from markupsafe import escape
from furl import furl
import requests
import json

# github生成的两把钥匙
client_id = 'f7ec5a35613f8a045ad8'
client_secret = 'a59f633152582da6ba58c20f01f62f2320654703'

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
	url = 'https://github.com/login/oauth/authorize'
	params = {
		'client_id': client_id,
		'redirect_uri': 'http://127.0.0.1:5000/oauth2/github/callback',
		'scope': 'read:user',
		'state': 'An unguessable random string.',
		'allow_signup': 'true'
	}
	url = furl(url).set(params)
	return redirect(url, 302)


@app.route('/oauth2/<service>/callback')
def oauth2_callback(service):
	print(service)

	code = request.args.get('code')
	# 根据返回的code获取access token
	access_token_url = 'https://github.com/login/oauth/access_token'
	payload = {
		'client_id': client_id,
		'client_secret': client_secret,
		'code': code,
		'state': 'An unguessable random string.'
	}
	r = requests.post(access_token_url, json=payload, headers={'Accept': 'application/json'})
	access_token = json.loads(r.text).get('access_token')
	# 拿到access token之后就可以去读取用户的信息了
	access_user_url = 'https://api.github.com/user'
	r = requests.get(access_user_url, headers={'Authorization': 'token ' + access_token})
	return jsonify({
		'status': 'success',
		'data': json.loads(r.text)
	})


if __name__ == '__main__':
	app.run(debug=True)