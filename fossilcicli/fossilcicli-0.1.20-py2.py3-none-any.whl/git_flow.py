import re

from . import env


class DeploymentInfo:
    '''
    DeploymentInfo hold information for building and triggering Jenkins jobs
    on Bitbucket pipelines.

    DeploymentInfo includes below information:
        "is_deploy"             A boolean flag for determining whether pipelines should trigger
                                Jenkins jobs.

        "service"               Include brands and their services(Jenkins jobs) to deploy.
                                Example:
                                    service = {
                                        "fossil": ["stg-fossil-user-v2-api", "stg-fossil-user-v2-consumer"],
                                        "mk":     ["stg-mk-user-v2-api", "stg-mk-user-v2-consumer"]
                                    }

        "unsupported_brands"    Include a set of unsupported brands.
                                Example:
                                    unsupported_brands = {
                                        "tb",
                                        "ax"
                                    }

        "image_tag":            The tag for docker image.

        "service_version":      The version of service. This version is the version of all services listed in 
                                "service"
    '''

    def __init__(self, brands, branches_brands, jobs, jobs_mapping, deploy_env):
        self.__branches_brands = branches_brands
        self.__brands = brands
        self.__jobs = jobs
        self.__jobs_mapping = jobs_mapping
        self.__deploy_env = deploy_env

        self.__git_branch = ""
        self.__git_tag = ""
        self.__git_commit = ""
        self.__bitbucket_build_number = ""

        self.is_deploy = False
        self.image_tag = ""
        self.services = {}
        self.service_version = ""
        self.unsupported_brands = set()

    def parse(self, git_branch, git_tag, git_commit, bitbucket_build_number, bitbucket_repo_slug):
        self.__git_branch = git_branch
        self.__git_tag = git_tag
        self.__git_commit = git_commit
        self.__bitbucket_build_number = bitbucket_build_number

        self.is_deploy = self.__is_deploy()
        self.services = self.__get_services()
        self.image_tag = self.__get_image_tag(
            git_tag, git_branch, git_commit, bitbucket_build_number, bitbucket_repo_slug)
        self.service_version = self.__get_service_version(
            git_tag, git_branch, git_commit, bitbucket_build_number)

    def __is_deploy(self):
        '''
        Check if the current building has deployment permission.
        '''
        if re.compile(r".+-(v\d+\.\d+\.\d+)$").match(self.__git_tag):
            return self.__git_tag != "" and self.__git_tag is not None
        elif re.compile(r"^develop[A-Za-z0-9_.]*$").match(self.__git_branch):
            return True
        elif re.compile(r"^release/\d+\.\d+\.\d+").match(self.__git_branch):
            return True
        else:
            return False

    def __get_services(self):
        '''
        Get deployments service by brand.
        '''
        services = {}
        deploy_able_brands = self.__get_deploy_able_brands(self.__git_tag)

        for brand in deploy_able_brands:
            if brand not in self.__brands:
                self.unsupported_brands.add(brand)
                continue

            services[brand] = []
            for job in self.__jobs:
                full_job_name = "{e}-{b}-{j}".format(
                    e=self.__deploy_env, b=brand, j=job)

                if full_job_name in self.__jobs_mapping:
                    full_job_name = self.__jobs_mapping[full_job_name]

                services[brand].append(full_job_name)

        return services

    def __get_deploy_able_brands(self, git_tag):
        '''
        Get deploy brand from the git tag and config.
        '''
        if self.__git_branch not in self.__branches_brands:
            return []

        brands = []
        if re.compile(r".+-(v\d+\.\d+\.\d+)$").match(git_tag):
            brands = re.findall(r"(.*)-v\d+\.\d+\.\d+$", git_tag)
        else:
            brands = self.__branches_brands[self.__git_branch]

        return brands

    def __get_image_tag(self, git_tag, git_branch, git_commit, bitbucket_build_number, bitbucket_repo_slug):
        '''
        Get deploy brand from the git tag, git brand and bitbucket_build_number.
        '''
        image_tag = []
        if re.compile(r".+-(v\d+\.\d+\.\d+)$").match(git_tag):
            image_tag = "{r}-{v}".format(r=bitbucket_repo_slug,
                                         v=re.findall(r".+-(v\d+\.\d+\.\d+)$", git_tag))
        elif re.compile(r"^develop[A-Za-z0-9_.]*$").match(git_branch):
            image_tag = ["{r}-{b}-{h}-{n}".format(
                r=bitbucket_repo_slug, b=git_branch, n=bitbucket_build_number, h=git_commit[:7])]
        elif re.compile(r"^release/\d+\.\d+\.\d+").match(git_branch):
            image_tag = ["{r}-{b}-{h}-{n}".format(
                r=bitbucket_repo_slug, b=git_branch, n=bitbucket_build_number, h=git_commit[:7])]
        else:
            return ""

        if image_tag:
            return image_tag[0]

        return ""

    def __get_service_version(self, git_tag, git_branch, git_commit, bitbucket_build_number):
        '''
        Get deploy brand from the git tag, git brand and bitbucket_build_number.
        '''
        service_version = []
        if re.compile(r".+-(v\d+\.\d+\.\d+)$").match(git_tag):
            service_version = "{v}".format(
                v=re.findall(r".+-(v\d+\.\d+\.\d+)$", git_tag))
        elif re.compile(r"^develop[A-Za-z0-9_.]*$").match(git_branch):
            service_version = [
                "{b}-{h}-{n}".format(b=git_branch, n=bitbucket_build_number, h=git_commit[:7])]
        elif re.compile(r"^release/\d+\.\d+\.\d+").match(git_branch):
            service_version = [
                "{b}-{h}-{n}".format(b=git_branch, n=bitbucket_build_number, h=git_commit[:7])]
        else:
            return ""

        if service_version:
            return service_version[0]

        return ""
