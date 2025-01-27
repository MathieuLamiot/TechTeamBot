"""
    This module defines the endpoint handler (called listener) for the Slack Interaction endpoint.
"""

import json

from flask_slacksigauth import slack_sig_auth
from flask import request
from sources.handlers.SlackShortcutHandler import SlackShortcutHandler
from sources.handlers.SlackViewSubmissionHandler import SlackViewSubmissionHandler


class SlackInteractionListener():
    """
        Class to define the Slack Interaction endpoint handler. It is callable and called when the right url is used.
    """

    def __init__(self):
        """
            The listener instanciates the handlers it will pass the request to so that it is processed.
        """
        self.slack_shortcut_handler = SlackShortcutHandler()
        self.slack_view_submission_handler = SlackViewSubmissionHandler()

    @slack_sig_auth
    def __call__(self):
        """
            Method called to process a request on the registered endpoint.
            It is subject to signed authentication.
            The method extracts the payload and route it to the correct handler.
            This method catches errors and manages their mapping to HTTP error codes.
        """

        # Retrieve the payload of the POST request
        payload_json = json.loads(request.form.get('payload'))

        # Route the request to the correct handler
        payload_type = payload_json['type']
        response_payload = {}
        try:
            if 'view_submission' == payload_type:
                response_payload = self.slack_view_submission_handler.process(payload_json)
            elif 'shortcut' == payload_type:
                response_payload = self.slack_shortcut_handler.process(payload_json)
            else:
                raise ValueError('Unknown payload type.')
        except ValueError as error:
            return str(error), 500
        except KeyError as error:
            return str(error), 500
        except NotImplementedError as error:
            return str(error), 501
        # pylint: disable-next=broad-exception-caught
        except Exception as error:
            return str(error), 500
        return response_payload, 200
