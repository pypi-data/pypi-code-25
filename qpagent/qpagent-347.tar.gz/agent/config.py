#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.config
    ~~~~~~~~~~~~

    This module provide the global settings.

    :copyright: (c) 2017 by Ma Fei.
"""

agent_env_port = {
    "alpha": 9096,
    "alta": 9099,
    "prod": 9099,
}

qualityplatform_env_api_url = {
    "alpha": "http://qp.alpha.elenet.me/api/",
    "alta": "http://qp.alta.elenet.me/api/",
    "prod": "http://qp.alta.elenet.me/api/"
}

sentry_env_url = {
    "alpha": "https://faf72d91b8724a59823e096c9acf397a:17cdc3bffe7a45b1b01894ecf4ae6048@sentry.alpha.elenet.me/1283",
    "alta": "https://68b6af8ce33c4ea5ae4a74b20bedca53:25cce717ed944b8a899af042b08301cb@sentry.alta.elenet.me/1588",
    "prod": "https://bdfb78f23a6a4bebb62ad2108c79a01b:d60af383987444b595ceb0d9019f6d23@sentry.elenet.me/181",
}
