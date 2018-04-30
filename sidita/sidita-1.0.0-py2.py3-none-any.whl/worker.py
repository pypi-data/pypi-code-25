####################################################################################################
#
# sidita - Simple Distributed Task Queue
# Copyright (C) 2018 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Implements default main function for workers.
"""

####################################################################################################

from importlib import import_module
import argparse
import sys

####################################################################################################

if __name__ == '__main__':

    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        '--python-path',
        default=None,
    )

    argument_parser.add_argument(
        '--worker-module',
    )

    argument_parser.add_argument(
        '--worker-class',
    )

    argument_parser.add_argument(
        '--worker-id',
        type=int,
    )

    args = argument_parser.parse_args()

    sys.stderr.write('Worker ARGV: {}\n'.format(sys.argv))

    if args.python_path:
        sys.path.insert(0, args.python_path)

    worker_module = import_module(args.worker_module)
    worker_cls = getattr(worker_module, args.worker_class)
    worker = worker_cls(args.worker_id)
    worker.run()
    sys.exit(0)
