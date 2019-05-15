import os
from slackclient import SlackClient

TOKEN = "xoxp-2558097324-15804180977-636560575872-518d8ef3d4dd9a51263a6cfcb04a9049"

slack_token = os.environ["xoxp-2558097324-15804180977-636560575872-518d8ef3d4dd9a51263a6cfcb04a9049"]
sc = SlackClient(slack_token)

expert_channel_id = "C02S1T177"
totis_channel_id = "C4PJMPXM3"

sc.api_call(
    "chat.postMessage",
    channel=expert_channel_id,
    text="Hello from Python! :tada:"
)
