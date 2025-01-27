"""
    This module defines a factory class, able to create Slack modals and open them for the Slack user.
"""

import requests

from flask import current_app
import sources.utils.Constants as cst


class SlackModalFactory():
    """
        Class capable of creating and opening modal views for Slack users.
    """

    def __init__(self):
        self.open_view_url = 'https://slack.com/api/views.open'
        self.__slack_bot_user_token = None

    def __get_slack_bot_user_token(self, app_context):
        """
            Returns the Slack Bot User token of the app.
            If not retrieved yet, it is retrieved from the Flask app configuration.
        """
        if self.__slack_bot_user_token is None:
            app_context.push()  # The factory usually runs in a dedicated thread, so Flask app context must be applied.
            self.__slack_bot_user_token = current_app.config[cst.APP_CONFIG_TOKEN_SLACK_BOT_USER_TOKEN]
        return self.__slack_bot_user_token

    def create_github_task_modal(self, app_context, trigger_id):
        """
            Method to create and open the Create github task modal on Slack
        """
        view = '''{
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Create a Github task"
            },
            "blocks": [
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Title of the task"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_title",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Type in here"
                        },
                        "multiline": false
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Description of the task"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_description",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe the task, or provide a Slack thread link."
                        },
                        "multiline": true
                    },
                    "optional": false
                }
            ],
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save"
            },
            "private_metadata": "",
            "callback_id": "ttl_create_github_task_modal_submit"
        }'''

        request_open_view_header = {"Authorization": "Bearer " + self.__get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['view'] = view
        request_open_view_payload['trigger_id'] = trigger_id
        requests.post(url=self.open_view_url, headers=request_open_view_header, json=request_open_view_payload, timeout=3000)
