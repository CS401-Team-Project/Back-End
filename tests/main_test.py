import os
import pathlib
import webview
import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

# app = Flask("Google Login App")
# app.secret_key = "CodeSpecialist.com"

# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
#
# GOOGLE_CLIENT_ID = "33674737284-srfbp7srvi8ie2m0sr426fved0hjq2tp.apps.googleusercontent.com"
# client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
#
# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
#             "openid"],
#     redirect_uri="http://127.0.0.1:5000/callback"
# )
#
authorization_url, state = flow.authorization_url()
webview.create_window('Google Login', url='https://www.google.com', html='', js_api=None, width=800, height=600,
                      x=None, y=None, resizable=True, fullscreen=False,
                      min_size=(200, 100), hidden=False, frameless=False,
                      minimized=False, on_top=False, confirm_close=False,
                      background_color='#FFF', text_select=False)
webview.start()

# @app.route("/callback")
# def callback():
#     flow.fetch_token(authorization_response=request.url)
#
#     if not session["state"] == request.args["state"]:
#         abort(500)  # State does not match!
#
#     credentials = flow.credentials
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)
#
#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID
#     )
#
#     session["google_id"] = id_info.get("sub")
#     session["name"] = id_info.get("name")
#     return redirect("/protected_area")
#
#
# @app.route("/login")
# def login():
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)
#
#
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")
#
#
# @app.route("/")
# def index():
#     return "Hello World <a href='/login'><button>Login</button></a>"
#
#
#
#
# if __name__ == "__main__":
#     app.run(debug=True)
