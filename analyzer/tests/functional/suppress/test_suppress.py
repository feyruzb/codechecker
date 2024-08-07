# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------
"""
Test source-code level suppression data writing to suppress file.
"""


import os
import inspect
import shutil
import sys
import unittest

from libtest import env, codechecker, project


def _generate_suppress_file(suppress_file):
    """
    Create a dummy suppress file just to check if the old and the new
    suppress format can be processed.
    """
    print("Generating suppress file: " + suppress_file)

    import calendar
    import hashlib
    import random
    import time

    hash_version = '1'
    suppress_stuff = []
    for _ in range(10):
        curr_time = calendar.timegm(time.gmtime())
        random_integer = random.randint(1, 9999999)
        suppress_line = str(curr_time) + str(random_integer)
        suppress_stuff.append(
            hashlib.md5(suppress_line.encode("utf-8")).hexdigest() +
            '#' + hash_version)

    s_file = open(suppress_file, 'w', encoding='utf-8', errors='ignore')
    for k in suppress_stuff:
        s_file.write(k + '||' + 'idziei éléáálk ~!@#$#%^&*() \n')
        s_file.write(
            k + '||' + 'test_~!@#$%^&*.cpp' +
            '||' + 'idziei éléáálk ~!@#$%^&*(\n')
        s_file.write(
            hashlib.md5(suppress_line.encode("utf-8")).hexdigest() + '||' +
            'test_~!@#$%^&*.cpp' + '||' + 'idziei éléáálk ~!@#$%^&*(\n')

    s_file.close()


class TestSuppress(unittest.TestCase):
    """
    Test source-code level suppression data writing to suppress file.
    """
    def setup_class(self):
        """Setup the environment for the tests."""

        global TEST_WORKSPACE
        TEST_WORKSPACE = env.get_workspace('suppress')

        os.environ['TEST_WORKSPACE'] = TEST_WORKSPACE

        test_project = 'suppress'

        test_config = {}

        project_info = project.get_info(test_project)

        test_proj_path = os.path.join(TEST_WORKSPACE, "test_proj")
        shutil.copytree(project.path(test_project), test_proj_path)

        project_info['project_path'] = test_proj_path

        test_config['test_project'] = project_info

        # Generate a suppress file for the tests.
        suppress_file = os.path.join(TEST_WORKSPACE, 'suppress_file')
        if os.path.isfile(suppress_file):
            os.remove(suppress_file)
        _generate_suppress_file(suppress_file)

        test_env = env.test_env(TEST_WORKSPACE)

        codechecker_cfg = {
            'suppress_file': None,
            'skip_list_file': None,
            'check_env': test_env,
            'workspace': TEST_WORKSPACE,
            'checkers': []
        }

        ret = project.clean(test_project, test_env)
        if ret:
            sys.exit(ret)

        output_dir = codechecker_cfg['reportdir'] \
            if 'reportdir' in codechecker_cfg \
            else os.path.join(codechecker_cfg['workspace'], 'reports')

        codechecker_cfg['reportdir'] = output_dir

        ret = codechecker.log_and_analyze(codechecker_cfg,
                                          project.path(test_project))

        if ret:
            sys.exit(1)
        print("Analyzing the test project was successful.")

        test_config['codechecker_cfg'] = codechecker_cfg

        env.export_test_cfg(TEST_WORKSPACE, test_config)

    def teardown_class(self):
        """Clean up after the test."""

        # TODO: If environment variable is set keep the workspace
        # and print out the path.
        global TEST_WORKSPACE

        print("Removing: " + TEST_WORKSPACE)
        shutil.rmtree(TEST_WORKSPACE)

    def setup_method(self, _):
        self._test_workspace = os.environ['TEST_WORKSPACE']

        self._testproject_data = env.setup_test_proj_cfg(self._test_workspace)
        self.assertIsNotNone(self._testproject_data)

        self._test_project_path = self._testproject_data['project_path']
        self._test_directory = os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe())))

    def test_source_suppress_export(self):
        """
        Test exporting a source suppress comment automatically to file.
        """

        generated_file = os.path.join(self._test_workspace,
                                      "generated.suppress")
        skip_file = os.path.join(self._test_directory, "suppress_export.skip")

        extract_cmd = [env.codechecker_cmd(), 'parse',
                       os.path.join(self._test_workspace, "reports"),
                       "--suppress", generated_file,
                       "--export-source-suppress", "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            extract_cmd, self._test_project_path,
            env.test_env(self._test_directory))
        self.assertEqual(ret, 2, "Failed to generate suppress file.")

        with open(generated_file, 'r',
                  encoding='utf-8', errors='ignore') as generated:
            expected_file = os.path.join(self._test_directory,
                                         "suppress.expected")
            with open(expected_file, 'r', encoding='utf-8',
                      errors='ignore') as expected:
                generated_content = generated.read()
                expected_content = expected.read()
                print("generated")
                print(generated_content)
                print("expected")
                print(expected_content)

                diff = set(expected_content).symmetric_difference(
                           generated_content)
                print("difference")
                for elem in diff:
                    print(elem)
                self.assertEqual(len(diff),
                                 0,
                                 "The generated suppress file does not "
                                 "look like what was expected")

    def test_doubled_suppress(self):
        """
        Test to catch repeated suppress comments with same bug.
        """

        skip_file = os.path.join(self._test_directory,
                                 "duplicated_suppress.skip")

        cmd = [env.codechecker_cmd(), 'parse',
               os.path.join(self._test_workspace, "reports"),
               "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            cmd, self._test_project_path,
            env.test_env(self._test_workspace))
        self.assertEqual(ret, 1, "Repeated suppress comment not recognized.")

    def test_doubled_suppress_by_all(self):
        """
        Test to catch multiple suppress comments in a line when "all"
        is one of them.
        """

        skip_file = os.path.join(self._test_directory, "suppress_by_all.skip")

        cmd = [env.codechecker_cmd(), 'parse',
               os.path.join(self._test_workspace, "reports"),
               "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            cmd, self._test_project_path,
            env.test_env(self._test_workspace))
        self.assertEqual(ret, 1, "Already covered suppress comment not "
                         "recognized.")

    def test_doubled_suppress_by_all_in_two_lines(self):
        """
        Test to catch unnecessary suppress comment that was covered by a
        suppress all comment in the previous line.
        """

        skip_file = os.path.join(self._test_directory,
                                 "suppress_by_all_in_two_lines.skip")

        cmd = [env.codechecker_cmd(), 'parse',
               os.path.join(self._test_workspace, "reports"),
               "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            cmd, self._test_project_path,
            env.test_env(self._test_workspace))
        self.assertEqual(ret, 1, "Already covered suppress comment not "
                         "recognized.")

    def test_confirmed_already_suppressed(self):
        """
        Test to catch unnecessary confirmed comment that was covered by a
        suppress all comment in the previous line.
        """

        skip_file = os.path.join(self._test_directory,
                                 "suppress_already_confirmed.skip")

        cmd = [env.codechecker_cmd(), 'parse',
               os.path.join(self._test_workspace, "reports"),
               "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            cmd, self._test_project_path,
            env.test_env(self._test_workspace))
        self.assertEqual(ret, 1, "Already suppressed comment must not be "
                         "confirmed.")

    def test_suppress_with_no_bug_is_ok(self):
        """
        Test that the suppress comment that suppresses non existent bug does
        not cause fail.
        """

        skip_file = os.path.join(self._test_directory,
                                 "suppress_without_bug.skip")

        cmd = [env.codechecker_cmd(), 'parse',
               os.path.join(self._test_workspace, "reports"),
               "--ignore", skip_file]

        _, _, ret = codechecker.call_command(
            cmd, self._test_project_path,
            env.test_env(self._test_workspace))
        self.assertEqual(ret, 0, "Suppress without existent bug causes error.")
