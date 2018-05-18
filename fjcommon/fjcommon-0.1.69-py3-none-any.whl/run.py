"""
run train.py config
run val.py config


.fjcommon_run_rc
    short_queue = "gpu.short.q@*"

.fjcommon_run_default_config
    --mem 40


run_config
    all
        --git_repo GIT_LOCAL GIT_URL
        --pre_run_cmds BLA
        --log_file
        -v FOO=bar
        --mem 40
    train.py
        --medium
        --gpu
    val.py
        --short
"""


def main():
    flags = _parse_flags()


def _parse_flags():
    pass

