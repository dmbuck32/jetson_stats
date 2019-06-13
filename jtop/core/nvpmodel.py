# -*- coding: UTF-8 -*-
# Copyright (C) 2019, Raffaello Bonghi <raffaello@rnext.it>
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
# Logging
import logging
# Launch command
import subprocess as sp

# Create logger for jplotlib
logger = logging.getLogger(__name__)


class NVPmodel():
    """
        This controller read the status from your NVIDIA Jetson and you can control
        performance and status.
        It is available for NVIDIA Jetson TX2, Jetson AGX Xavier, Jetson Nano
        Boards reference:
        * TX2: https://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/
        * AGX Xavier: https://www.jetsonhacks.com/2018/10/07/nvpmodel-nvidia-jetson-agx-xavier-developer-kit/
        * Nano: https://www.jetsonhacks.com/2019/04/10/jetson-nano-use-more-power/
    """
    REGEXP = re.compile(r'POWER_MODEL: ID=(.+?) NAME=((.*))')

    class NVPmodelException(Exception):
        pass

    def __init__(self, type_board):
        self.type_board = type_board
        try:
            nvpmodel_p = sp.Popen(['nvpmodel', '-p', '--verbose'], stdout=sp.PIPE)
            out, _ = nvpmodel_p.communicate()
            # Log value
            logger.debug('nvqmodel status %s', out)
            # Decode lines
            lines = out.decode("utf-8")
            # Read all lines and extract modes
            self.board = []
            for line in lines.split("\n"):
                # Search configuration NVPmodel
                match = NVPmodel.REGEXP.search(line)
                # if match extract name and number
                if match:
                    pm = {"ID": int(match.group(1)), "Name": match.group(2)}
                    self.board += [pm]
        except OSError:
            logger.info("This board {} does not have NVP Model".format(type_board))
            raise NVPmodel.NVPmodelException("NVPmodel does not exist for this board {}".format(type_board))
        # Initialize mode and num
        self.update()

    @property
    def modes(self):
        return self.board

    def set(self, level):
        """ Set nvpmodel to a new status """
        try:
            sp.Popen(['nvpmodel', '-m', str(level)], stdout=sp.PIPE)
            self.num = level
            return True
        except OSError:
            logger.info("NVP Model does not exist")
            return False

    def increase(self):
        if self.num + 1 < len(self.modes):
            return self.set(self.num + 1)
        else:
            return False

    def decrease(self):
        if self.num - 1 >= 0:
            return self.set(self.num - 1)
        else:
            return False

    def update(self):
        """ Read nvpmodel to know the status of the board """
        try:
            nvpmodel_p = sp.Popen(['nvpmodel', '-q'], stdout=sp.PIPE)
            out, _ = nvpmodel_p.communicate()
            # Log value
            logger.debug('nvqmodel status %s', out)
            # Decode lines and split
            lines = out.decode("utf-8").split("\n")
            # Return the mode type
            self.mode = str(lines[0].split(": ")[1])
            self.num = int(lines[1])
        except OSError:
            logger.info("NVP Model does not exist")
# EOF
