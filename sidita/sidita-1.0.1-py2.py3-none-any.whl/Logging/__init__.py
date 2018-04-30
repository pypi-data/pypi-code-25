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

"""Implements logging setup.

"""

####################################################################################################

from pathlib import Path
import yaml
import logging
import logging.config

####################################################################################################

def setup_logging(application_name,
                  config_file=Path(__file__).parent.joinpath('logging.yml')):

    logging_config = yaml.load(open(config_file))

    # Fixme: \033 is not interpreted in YAML
    formatter_config = logging_config['formatters']['ansi']['format']
    logging_config['formatters']['ansi']['format'] = formatter_config.replace('<ESC>', '\033')
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(application_name)
    logger.info('Start %s' % (application_name))

    return logger
