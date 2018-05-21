# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model
from modelhub.core.utils import cached_property
from collections import defaultdict

# TODO: move to config
REDIS_URL_ENV_KEY = "RD_REDIS_URL"
REDIS_PREFIX_ENV_KEY = "RD_REDIS_PREFIX"
REDIS_TIMEOUT = 10


@register("runserver")
class Command(BaseCommand):
    arguments = [
        argument("models_name", nargs=-1),
        option("-b", "--bin_path", type=click.Path(exists=True)),
        option("-r", "--register_model", is_flag=True),
        option("-p", "--port", default=8500)
    ]

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.redis_url = os.getenv(REDIS_URL_ENV_KEY)
        self.redis_prefix = os.getenv(REDIS_PREFIX_ENV_KEY, "")
        # bin_path = "/usr/bin/tensorflow_model_server"

    @cached_property
    def bin_path(self):
        import subprocess
        return subprocess.check_output(["which", "tensorflow_model_server"]).strip().decode()

    def run(self, models_name, port, bin_path=None, register_model=False):
        """run tensorflow_model_server with models"""
        if not models_name:
            self.echo("no model name provided")
            return

        self.is_register_model = register_model
        if register_model:
            self._prepare_auto_discovery(port)

        if bin_path:
            self.bin_path = bin_path

        model_name_version_list = [Model.split_name_version(model_name) for model_name in models_name]
        model_versions_map = defaultdict(list)
        for model_name, version in model_name_version_list:
            model_versions_map[model_name].append(version)

        model_versions_list = [(Model.get_local(model_name), list(filter(None, versions))) for model_name, versions in model_versions_map.items()]

        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile("r+") as f:
            f.write(self.generate_model_config(model_versions_list))
            f.flush()
            self.echo("server bin_path:\t%s" % self.bin_path)
            self.echo("model_config_file:\t%s" % f.name)
            self._run_server(
                models=model_versions_list,
                model_config_file=f.name,
                port=port
            )

    def generate_model_config(self, model_versions_list):
        from tensorflow_serving.config.model_server_config_pb2 import ModelServerConfig, ModelConfigList, ModelConfig
        from tensorflow_serving.sources.storage_path.file_system_storage_path_source_pb2 import FileSystemStoragePathSourceConfig

        def build_model_config(model, versions):
            if not versions:
                versions_list = [model.latest_local_version]
            else:
                versions_list = []
                for version in versions:
                    version = model.get_version(version)
                    assert version.local_exists, "model {model.name}@{version} is not exist in local, try ‘modelhub checkout {model.name}@{version}"
                    versions_list.append(version)

            assert all(version.manifest.is_saved_model for version in versions_list), "%s is not a TensorFlow Model, cannot serving" % model.name
            # import ipdb; ipdb.set_trace()
            return ModelConfig(
                name=model.name,
                base_path=model.local_path,
                model_platform="tensorflow",
                model_version_policy=None if not versions else FileSystemStoragePathSourceConfig.ServableVersionPolicy(specific=FileSystemStoragePathSourceConfig.ServableVersionPolicy.Specific(versions=versions))
            )

        res = str(ModelServerConfig(
            model_config_list=ModelConfigList(
                config=[build_model_config(model, versions) for model, versions in model_versions_list]
            )
        ))
        # print(res)
        return res

    def _prepare_auto_discovery(self, port):
        from modelhub.tf_serving import AutoDiscovery, parse_redis_url, get_local_ip
        self.hostport = "%s:%d" % (get_local_ip(), port)
        if not self.redis_url:
            raise ValueError("No REDIS url configured, should set env '%s'" % REDIS_URL_ENV_KEY)
        ad_args = parse_redis_url(self.redis_url)
        ad_args["redis_prefix"] = self.redis_prefix
        self.auto_discovery = AutoDiscovery(**ad_args)

    def _register_model(self, models, port):
        for model, versions in models:
            versions = versions or [model.latest_local_version.manifest.seq]
            for v in versions:
                try:
                    self.log_debug("register %s@%s", model.name, v)
                    self.auto_discovery.register(
                        model.name,
                        v,
                        self.hostport
                    )
                    self.log_info("register %s@%s success", model.name, v)

                except Exception:
                    self.log_exception("register %s@%s error", model.name, v)

    def _run_server(self, models, model_config_file, port, **kwargs):
        from subprocess import Popen, PIPE, TimeoutExpired
        import threading
        popen = Popen(
            [
                self.bin_path,
                "--port=%s" % port,
                "--model_config_file=%s" % model_config_file
            ] + [
                "--%s=%s" % (key, value) for key, value in kwargs.items()
            ],
            stdin=PIPE,
            stderr=PIPE if self.is_register_model else None,
            universal_newlines=True
        )
        try:
            if not self.is_register_model:
                return popen.wait()
            # initialized = False
            while True:
                line = popen.stderr.readline()
                self.log_info(line.strip())
                if "Running ModelServer at" in line:
                    # initialized = True
                    self._register_model(models, port)
                    break

            def print_stderr():
                while True:
                    # print("start read")
                    line = popen.stderr.readline()
                    if not line:
                        break
                    self.log_info(line.strip())
            t = threading.Thread(target=print_stderr, name='print_stderr')
            t.start()

            while True:
                try:
                    ret = popen.wait(timeout=REDIS_TIMEOUT)
                    # print("out", stderr)
                except TimeoutExpired:
                    self._register_model(models, port)
                else:
                    # print(popen.stderr.read().decode())
                    self.log_warning("serving stoped on returncode %s", ret)
                    break
        finally:
            if popen.returncode is None:
                self.log_warning("quitting")
                popen.kill()
