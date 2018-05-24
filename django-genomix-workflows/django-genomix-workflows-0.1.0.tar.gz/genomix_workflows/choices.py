# -*- coding: utf-8 -*-
from model_utils import Choices


STATUS = Choices(
    (1, 'PENDING', 'Pending'),
    (2, 'COMPLETE', 'Complete'),
    (3, 'HOLD', 'Hold'),
    (4, 'SKIP', 'Skip'),
)

WORKFLOW_STATE = Choices(
    (1, 'ACTIVE', 'Active'),
    (2, 'COMPLETE', 'Complete'),
    (3, 'HOLD', 'Hold'),
    (4, 'CANCELED', 'Canceled')
)
