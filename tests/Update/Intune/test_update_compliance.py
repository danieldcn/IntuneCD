#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Compliance."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_compliance import update


class TestUpdateCompliance(unittest.TestCase):
    """Test class for update_compliance."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Compliance Policies")
        self.directory.write(
            "Compliance Policies/Policies/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Policies/test.txt", "txt", encoding="utf-8"
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "scheduledActionsForRule": [
                        {"scheduledActionConfigurations": [{"gracePeriodHours": 0}]}
                    ],
                    "assignments": [{"target": {"groupId": "test"}}],
                }
            ]
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test1",
            "scheduledActionsForRule": [
                {"scheduledActionConfigurations": [{"gracePeriodHours": 1}]}
            ],
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_compliance.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.update_assignment.stop()
        self.load_file.stop()
        self.post_assignment_update.stop()
        self.makeapirequestPatch.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 2 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=True
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 2 and the makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"
        self.mem_data["value"][0]["scheduledActionsForRule"][0][
            "scheduledActionConfigurations"
        ][0]["gracePeriodHours"] = 1

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=True
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"
        self.mem_data["value"][0]["scheduledActionsForRule"][0][
            "scheduledActionConfigurations"
        ][0]["gracePeriodHours"] = 1

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=True
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_data["value"].append({"displayName": "test2", "id": "2"})

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_scope_tags(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            assignment=True,
            remove=False,
            scope_tags=["test"],
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_complianceScriptPolicy(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["deviceComplianceScriptName"] = "test"
        self.repo_data["deviceCompliancePolicyScript"] = {
            "deviceComplianceScriptId": "1"
        }
        self.makeapirequest.side_effect = [
            self.mem_data,
            {
                "value": [{"id": "0", "displayName": "test"}],
            },
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 2)

    def test_update_complianceScriptPolicy_platform(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["platforms"] = "linux"
        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])

    def test_update_complianceScriptPolicy_not_found(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["ComplianceScriptName"] = "test"
        self.repo_data["displayName"] = "test1"
        self.repo_data["deviceCompliancePolicyScript"] = {
            "deviceComplianceScriptId": "1"
        }
        self.makeapirequest.side_effect = [
            self.mem_data,
            {
                "value": [{"id": "0", "displayName": "test"}],
            },
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_customCompliancePolicy(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["deviceComplianceScriptName"] = "test"
        self.repo_data["deviceCompliancePolicyScript"] = {
            "deviceComplianceScriptId": "1"
        }
        self.makeapirequest.side_effect = [
            self.mem_data,
            {"value": [{"id": "0", "displayName": "test"}]},
        ]
        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 2)

    def test_update_customCompliancePolicy_script_not_found(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["deviceComplianceScriptName"] = None
        self.repo_data["deviceCompliancePolicyScript"] = {
            "deviceComplianceScriptId": "1"
        }
        self.makeapirequest.side_effect = [
            self.mem_data,
            {"value": []},
        ]
        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])

    def test_update_customCompliancePolicy_script_not_found_create(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["displayName"] = "test1"
        self.repo_data["deviceComplianceScriptName"] = "test"
        self.repo_data["deviceCompliancePolicyScript"] = {
            "deviceComplianceScriptId": "1"
        }
        self.makeapirequest.side_effect = [
            self.mem_data,
            {"value": []},
        ]
        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False, report=False
        )

        self.assertEqual(self.makeapirequestPost.call_count, 0)


if __name__ == "__main__":
    unittest.main()
