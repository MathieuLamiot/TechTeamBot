"""
    This module define the handler for Slack view submission.
"""

from threading import Thread
from flask import current_app
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.models.InitGithubTaskParam import InitGithubTaskParam


class SlackViewSubmissionHandler():
    """
        Class to handle Slack view submitted and received by the app.
    """

    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_task_handler = GithubTaskHandler()

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
        elif 'ttl_dev_team_escalation_modal_submit' == callback:
            self.dev_team_escalation_modal_submit_callback(payload_json)
        else:
            raise ValueError('Unknown modal callback.')
        return {"response_action": "clear"}

    def create_github_task_modal_submit_callback(self, payload_json):
        """
            Callback method to process a submitted modal "Create GitHub Task".
            The parameters of the task are extracted from the modal payload. A thread is started to generate the Github task.
        """
        task_params = self.create_github_task_modal_retrieve_params(payload_json)

        thread = Thread(target=self.github_task_handler.init_github_task, kwargs={
            "app_context": current_app.app_context(), "task_params": task_params})
        thread.start()

    def create_github_task_modal_retrieve_params(self, payload_json):
        """
            This method extract the github task parameters from a submitted Slack modal "Create GitHub Task".
            Only the parameters found in the payload are set.
        """
        modal_values = payload_json["view"]["state"]["values"]

        # Title component
        title = modal_values['title_block']['task_title']['value']

        # Description component
        body_input = modal_values['description_block']['task_description']['value']
        user_name = payload_json["user"]["name"]
        body = f"Task submitted by {user_name} through TBTT.\n\n{body_input}"

        # Immediate component
        handle_immediately = False
        keys = list(dict.keys(modal_values['immediately_block']))
        selected_options = modal_values['immediately_block'][keys[0]]['selected_options']
        for selected_option in selected_options:
            if 'handle_immediately' == selected_option['value']:
                handle_immediately = True

        # Assignee component
        assignee = 'no-assignee'
        keys = list(dict.keys(modal_values['assignee_block']))
        selected_option = modal_values['assignee_block'][keys[0]]['selected_option']
        if selected_option is not None:
            assignee = selected_option['value']

        # Initiator of the request
        initiator = payload_json["user"]["id"]

        task_params = InitGithubTaskParam(title, body, handle_immediately, assignee, initiator)

        return task_params

    def dev_team_escalation_modal_submit_callback(self, payload_json):
        """
            Callback method to process a submitted modal "Create GitHub Task".
            The parameters of the task are extracted from the modal payload. A thread is started to generate the Github task.
        """
        task_params = self.dev_team_escalation_modal_retrieve_params(payload_json)

        thread = Thread(target=self.github_task_handler.init_github_task, kwargs={
            "app_context": current_app.app_context(), "task_params": task_params})
        thread.start()

    def dev_team_escalation_modal_retrieve_params(self, payload_json):
        """
            This method extract the github task parameters from a submitted Slack modal "Create GitHub Task".
            Only the parameters found in the payload are set.
        """
        modal_values = payload_json["view"]["state"]["values"]

        # Title component
        title = modal_values['title_block']['task_title']['value']

        # Description component
        description_input = modal_values['description_block']['task_description']['value']
        investigation_input = modal_values['investigation_block']['investigation_block']['value']
        replication_input = modal_values['replication_block']['replication_block']['value']
        user_name = payload_json["user"]["name"]
        body = (f"Task submitted by {user_name} through TBTT.\n\n"
                f"**Description of the issue:**\n{description_input}\n\n"
                f"**Investigation performed:**\n{investigation_input}\n\n"
                f"**How to reproduce:**\n{replication_input}\n\n"
                )

        # Initiator of the request
        initiator = payload_json["user"]["id"]

        task_params = InitGithubTaskParam(title, body, handle_immediately=True,
                                          initiator=initiator, flow='dev-team-escalation')

        return task_params
