import os
import json
import logging
import random

from flask import Flask, request, make_response, Response

from slack.web.client import WebClient
from slack.errors import SlackApiError
from slack.signature import SignatureVerifier
from slackeventsapi import SlackEventAdapter

from slashCommand import Slash

# This `app` represents your existing Flask app
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# An example of one of your Flask app's routes
@app.route("/slack/pokemomo", methods=["POST"])
def command():
  if not verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)
  info = request.form


  try:
    response = slack_client.chat_postMessage(
      channel='#{}'.format(info["channel_name"]),
      text=commander.getMessage()
    )
  except SlackApiError as e:
    logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
    logging.error(e.response)
    return make_response("", e.response.status_code)

  return make_response("", response.status_code)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNATURE"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events",app)

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(slack_bot_token)

# Pet and feed momo
@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    message = event_data["event"]
    if "pet" in message.get('text'):
        channel = message["channel"]
        try:
            filepath="./momo_pet.gif"
            response = slack_client.files_upload(
                channels=channel,
                file=filepath)
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
    elif "feed" in message.get('text'):
        channel = message["channel"]
        try:
            if round(random.random()) == 0:
                filepath="./momo_apple.gif"
            else :
                filepath="./momo_melon.gif"
            response = slack_client.files_upload(
                channels=channel,
                file=filepath)
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hello" in message.get('text'):
        channel = message["channel"]
        try:
            ts = message["thread_ts"]
        except KeyError :
            ts = message["ts"]
        message = "<@%s> :monkey_face:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message, thread_ts=ts)
    elif message.get("subtype") is None and "momo" in message.get('text'):
        channel = message["channel"]
        try:
            filepath="./momo_tilt.gif"
            response = slack_client.files_upload(
                channels=channel,
                file=filepath)
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
    elif message.get("subtype") is None :
        channel = message["channel"]
        user_info = slack_client.users_info(user=message.get('user'))
        all_users = slack_client.users_list()
        num = len(all_users["members"])
        for i in range(num):
            print(all_users["members"][i]["real_name"])
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            if all_users["members"][i]["real_name"] == "Natasha" :
                user1 = all_users["members"][i]["id"]
            elif all_users["members"][i]["real_name"] == "Tejas" :
                user2 = all_users["members"][i]["id"]
            elif all_users["members"][i]["real_name"] == "Tim" :
                user3 = all_users["members"][i]["id"]
        if not user_info["user"]["is_bot"]:
            try:
                ts = message["thread_ts"]
                replies = slack_client.conversations_replies(channel=channel,ts=ts)
                if replies['messages'][0]['reply_count'] < 3 :
                    message = "<@%s> " % user1 + "<@%s> " % user2 + "<@%s> " % user3
                    slack_client.chat_postMessage(channel=channel, text=message, thread_ts=ts)
            except KeyError :
                pass

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    if emoji == "monkey_face" or emoji == "monkey" or emoji == "see_no_evil"  or emoji == "hear_no_evil"  or emoji == "speak_no_evil":
        channel = event["item"]["channel"]
        text = ":%s:" % emoji
        slack_client.chat_postMessage(channel=channel, text=text)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Start the server on port 3000
if __name__ == "__main__":
    verifier = SignatureVerifier(slack_signing_secret)

    commander = Slash(":monkey:")
    app.run(port=5001)
