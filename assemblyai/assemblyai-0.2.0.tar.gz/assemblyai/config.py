"""Configs."""

import logging
import os


ASSEMBLYAI_URL = os.environ.get('ASSEMBLYAI_URL', 'https://api.assemblyai.com')
ASSEMBLYAI_TOKEN = os.environ.get('ASSEMBLYAI_TOKEN')

log = logging.getLogger('AssemblyAI')
log.setLevel(logging.ERROR)
