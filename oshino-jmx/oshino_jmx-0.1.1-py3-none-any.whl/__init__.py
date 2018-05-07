def jmx_trans_command():
        return [
            'java',
            '-Djmxtrans.log.dir=.',
            '-jar',
            'lib/jmxtrans-all.jar',
            '--run-endlessly',
            '--json-directory', 'etc/',
            '--continue-on-error', 'true'
        ]
