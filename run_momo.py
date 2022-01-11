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

# Using Flask for web development
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Testing out a flask app route, this is for a Slack slash command
@app.route("/slack/pokemomo", methods=["POST"])

def command():
  if not verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)
  info = request.form

# In the channel the slash command /pokemomo was used, post message from "commander"
# commander uses the Slash class which always returns self (a monkey emoji, see below)
# This was just practice using the Slash command 
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

# Credentials and Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNATURE"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events",app)

# Credentials and creating a SlackClient for bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(slack_bot_token)

# When momo is mentioned (@Momo)
@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    # Gets message from "app_mention" event
    message = event_data["event"]
    # If the message contains the word "pet", upload "momo_pet.gif"
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
    # If instead the message contains the word "feed", randomly choose either
    # "momo_apple.gif" or "momo_melon.gif" to post.
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

# Responder to greetings. When a message is posted, get the message text from
# the event data.
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hello", the bot responds by mentioning
    # the user and posting the :monkey_face: emoji
    if message.get("subtype") is None and "hello" in message.get('text'):
        channel = message["channel"]
        try:
            ts = message["thread_ts"]
        except KeyError :
            ts = message["ts"]
        message = "<@%s> :monkey_face:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message, thread_ts=ts)
    # If the message contains the text "momo" (without mentioning momo as @momo),
    # the bot uploads the "momo_tilt.gif" file in the channel.
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
    # This is why Momo was created. If Momo notices that someone (who is not a bot)
    # replied to a message creating a thread, Momo also responds and tags three users
    # "Natasha" (me), "Tejas". and "Tim" because Slack does not automatically notify
    # anyone of thread replies unless they are specifically mentioned. (We have a small
    # group so this is useful for us without overwhelming us with notifications.)
    elif message.get("subtype") is None :
        channel = message["channel"]
        user_info = slack_client.users_info(user=message.get('user'))
        all_users = slack_client.users_list()
        num = len(all_users["members"])
        # Ignore this, it's for debugging. I left it in because it just prints
        # to the log, and I find it useful to keep.
        for i in range(num):
            print(all_users["members"][i]["real_name"])
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            if all_users["members"][i]["real_name"] == "Natasha" :
                user1 = all_users["members"][i]["id"]
            elif all_users["members"][i]["real_name"] == "Tejas" :
                user2 = all_users["members"][i]["id"]
            elif all_users["members"][i]["real_name"] == "Tim" :
                user3 = all_users["members"][i]["id"]
        # If the user who posted is not a bot
        if not user_info["user"]["is_bot"]:
            try:
                # If message is a reply in a thread and the number of replies
                # is < 3, post a message mentioning the three users defined above
                ts = message["thread_ts"]
                replies = slack_client.conversations_replies(channel=channel,ts=ts)
                if replies['messages'][0]['reply_count'] < 3 :
                    message = "<@%s> " % user1 + "<@%s> " % user2 + "<@%s> " % user3
                    slack_client.chat_postMessage(channel=channel, text=message, thread_ts=ts)
            except KeyError :
                pass

# Reaction emoji echo if the reaction added to a post is one of the monkey emojis
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

# Start the server
if __name__ == "__main__":
    verifier = SignatureVerifier(slack_signing_secret)

    commander = Slash(":monkey:")
    app.run(port=5001)
