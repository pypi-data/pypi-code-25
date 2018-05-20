from .api import Api

class Deployments(Api):

    def list_deployments(self, project_id, environement_id, options = None):
        """
        :param project_id:
        :param environement_id:
        :param options:
            deployer_email
            string (optional) Example: joe@example.com
            Filter by deployer

            state
            string (optional) Example: New
            Filter by state, one of New,Submitted,Invalid,Approved,Rejected,Queued,Deploying,Aborting,Completed,Failed,Deleted

            lastedited_from_unix
            int (optional) Example: 1267148625
            Include only deployments edited after this timestamp

            datestarted_from_unix
            int (optional) Example: 1267148625
            Include only deployments started after this timestamp

            datestarted_to_unix
            int (optional) Example: 4075753425
            Include only deployments started before this timestamp

            title
            string (optional) Example: Deployment of site v1.0.0
            Filter by title

            summary
            string (optional) Example: We fixed all the bugs in this deployment
            Filter by summary
        :return:
        """
        return self.do_request('/naut/project/%s/environment/%s/deploys' % (project_id, environement_id), options)
