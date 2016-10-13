import markovify
import time
import json
import re

from slackbot import SlackClient

BOT_TOKEN = "insert bot token here"
GROUP_TOKEN = "insert slack group token here"
MESSAGE_QUERY = "from:username_to_parrot"
MESSAGE_PAGE_SIZE = 100
DEBUG = True

def load_database():
    """
        Reads 'database' from a JSON file on disk.
        Returns a dictionary keyed by unique message permalinks.
    """
    try:
        with open('message_database.json', 'r') as json_file:
            messages = json.loads(json_file.read())
    except IOError:
        with open('message_db.json', 'w') as json_file:
            json_file.write('{}')
        messages = {}

    return messages

def store_database(obj):
    """
        Takes a dictionary keyed by unique message permalinks and
        writes it to the JSON 'database' on disk.
    """

    with open('message_database.json', 'w') as json_file:
        json_file.write(json.dumps(obj))

    return True

def request_messages(client, page=1):
    """
        Convenience method for querying messages from Slack API.
    """
    if DEBUG:
        print "requesting page {}".format(page)

    return client.api_call('search.messages', query=MESSAGE_QUERY,
                            count=MESSAGE_PAGE_SIZE, page=page)


def build_text_model():
    """
        Read the latest 'database' off disk and build a new markov
        chain generator model.
        Returns TextModel.
    """
    if DEBUG:
        print "Building new model..."

    messages = load_database()
    return markovify.Text(" ".join(messages.values()), state_size=2)

def format_message(original):
    """
        Do any formatting necessary to markon chains
        before relaying to Slack.
    """
    if original is None:
        return

    # remove <> from urls
    cleaned_message = re.sub(r'<(htt.*)>', '\1', original)
    return cleaned_message


def main():
    """
        Startup logic and the main application loop
        to monitor Slack events.
    """
    # Create the slackclient instance
    slack_client = SlackClient(BOT_TOKEN)
    # Connect to slack
    if not slack_client.rtm_connect():
        raise Exception("Couldn't connect to slack.")

    while True:
        # check for events
        for slack_event in slack_client.rtm_read():
            # we need only events that are messages
            if not slack_event.get('type') == "message":
                continue

            message = slack_event.get("text")
            user = slack_event.get("user")
            channel = slack_event.get("channel")

            if not message or not user:
                continue

            if "ping" in message.lower():
                slack_client.rtm_send_message(channel, "pong")

        # Sleep for 0.5 seconds
        time.sleep(0.5)


if __name__ == '__main__':
    main()
