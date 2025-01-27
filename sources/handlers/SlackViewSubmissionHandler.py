"""
    This module define the handler for Slack view submission.
"""

from threading import Thread
from flask import current_app
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory


class SlackViewSubmissionHandler():
    """
        Class to handle Slack view submitted and received by the app.
    """

    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_gql_call_factory = GithubGQLCallFactory()

    def process(self, payload_json):
        """
            Method called to process a request of type "view submitted". It identifies the callback assigned to the Slack modal
            and routes the request according to it to the right callback method.
        """
        # Retrieve the modal callback
        callback = payload_json['view']['callback_id']

        # Process the paylaod according to the callback
        if 'ttl_create_github_task_modal_submit' == callback:
            self.create_github_task_modal_submit_callback(payload_json)
        else:
            raise ValueError('Unknown modal callback.')
        return {"response_action": "clear"}

    def create_github_task_modal_submit_callback(self, payload_json):
        """
            Callback method to process a submitted modal "Create GitHub Task".
            The parameters of the task are extracted from the modal payload. A thread is started to generate the Github task.
        """
        task_params = self.create_github_task_modal_retrieve_params(payload_json)

        thread = Thread(target=self.github_gql_call_factory.create_github_task, kwargs={
            "app_context": current_app.app_context(), "task_params": task_params})
        thread.start()

    def create_github_task_modal_retrieve_params(self, payload_json):
        """
            This method extract the github task parameters from a submitted Slack modal "Create GitHub Task".
            Only the parameters found in the payload are set.
        """
        task_params = {}
        modal_values = payload_json["view"]["state"]["values"]
        for key in modal_values:
            for item_key in modal_values[key]:
                if 'task_title' == item_key:
                    task_params['title'] = modal_values[key][item_key]['value']
                elif 'task_description' == item_key:
                    task_params['body'] = modal_values[key][item_key]['value']
        return task_params
