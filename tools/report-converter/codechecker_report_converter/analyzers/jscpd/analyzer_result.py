# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------

from typing import List

from codechecker_report_converter.report import Report

from ..analyzer_result import AnalyzerResultBase
from .parser import Parser


class AnalyzerResult(AnalyzerResultBase):
    """ Transform analyzer result of the JSCPD analyzer. """

    TOOL_NAME = 'jscpd'
    NAME = 'JSCPD'
    URL = 'https://www.npmjs.com/package/jscpd'

    def get_reports(self, file_path: str) -> List[Report]:
        """ Get reports from the given analyzer result. """
        return Parser().get_reports(file_path)
