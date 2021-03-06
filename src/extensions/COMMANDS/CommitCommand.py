###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" Commit Command for RDMC """

import sys

from optparse import OptionParser
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                        NoChangesFoundOrMadeError, NoCurrentSessionEstablished

from rdmc_base_classes import RdmcCommandBase

class CommitCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='commit',\
            usage='commit [OPTIONS]\n\n\tRun to apply all changes made during the' \
                    ' current session\n\texample: commit',\
            summary='Applies all the changes made during the current' \
                    ' session.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)
        #remove reboot option if there is no reboot command
        try:
            self.rebootobj = rdmcObj.commandsDict["RebootCommand"](rdmcObj)
        except:
            self.parser.remove_option('--reboot')

    def commitfunction(self, options=None):
        """ Main commit worker function

        :param options: command line options
        :type options: list.
        """
        self.commitvalidation()

        sys.stdout.write(u"Committing changes...\n")

        if options:
            if options.biospassword:
                self._rdmc.app.update_bios_password(options.biospassword)

        try:
            if not self._rdmc.app.commit(verbose=self._rdmc.opts.verbose):
                raise NoChangesFoundOrMadeError("No changes found or made " \
                                                    "during commit operation.")
        except Exception, excp:
            raise excp

        if options:
            if options.reboot:
                self.rebootobj.run(options.reboot)
            else:
                self.logoutobj.logoutfunction("")
        else:
            self.logoutobj.logoutfunction("")

    def run(self, line):
        """ Wrapper function for commit main function
        
        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.commitfunction(options)

        #Return code
        return ReturnCodes.SUCCESS

    def commitvalidation(self):
        """ Commit method validation function """
        try:
            self._rdmc.app.get_current_client()
        except:
            raise NoCurrentSessionEstablished("Please login and make setting" \
                                      " changes before using commit command.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_option(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
        customparser.add_option(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute.",
            default=None,
        )
