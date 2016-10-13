import markovify
import time

from slackbot import SlackClient

BOT_TOKEN = "insert bot token here"
GROUP_TOKEN = "insert slack group token here"

def main():
    """
        Startup logic and the main application loop to monitor Slack events.
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
