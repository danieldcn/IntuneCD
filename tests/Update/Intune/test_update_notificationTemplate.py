#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Notification Templates."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_notificationTemplate import update


class TestUpdateNotificationTemplates(unittest.TestCase):
    """Test class for update_notificationTemplate."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Compliance Policies/Message Templates")
        self.directory.write(
            "Compliance Policies/Message Templates/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Message Templates/test.txt",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "id": "0",
                    "displayName": "test",
                    "defaultLocale": "en-us",
                    "brandingOptions": "test",
                    "localizedNotificationMessages": [{"messageTemplate": "test"}],
                }
            ]
        }
        self.mem_template_data = {
            "id": "0",
            "displayName": "test",
            "defaultLocale": "en-us",
            "brandingOptions": "test",
            "roleScopeTagIds": [],
            "localizedNotificationMessages": [
                {
                    "messageTemplate": "test",
                    "lastModifiedDateTime": "test",
                    "locale": "en-us",
                    "id": "0",
                }
            ],
        }
        self.repo_data = {
            "displayName": "test",
            "defaultLocale": "en-us",
            "brandingOptions": "test",
            "roleScopeTagIds": [],
            "localizedNotificationMessages": [
                {"messageTemplate": "test1", "locale": "en-us"}
            ],
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_notificationTemplate.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_notificationTemplate.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_notificationTemplate.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_notificationTemplate.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_notificationTemplate.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.makeapirequest.side_effect = [self.mem_data, self.mem_template_data]
        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 2 and makeapirequestPatch should be called."""

        self.repo_data["brandingOptions"] = "test1"
        self.makeapirequest.side_effect = [self.mem_data, self.mem_template_data]

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 2)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.mem_template_data["localizedNotificationMessages"][0][
            "messageTemplate"
        ] = "test1"
        self.makeapirequest.side_effect = [self.mem_data, self.mem_template_data]
        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_data["value"].append(
            {
                "displayName": "test2",
                "id": "2",
                "localizedNotificationMessages": [{"messageTemplate": "test"}],
            }
        )

        self.makeapirequest.side_effect = [self.mem_data, self.mem_template_data]

        self.update = update(
            self.directory.path, self.token, report=False, remove=True, scope_tags=[]
        )

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_scope_tags(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.makeapirequest.side_effect = [self.mem_data, self.mem_template_data]

        self.count = update(
            self.directory.path,
            self.token,
            remove=False,
            report=False,
            scope_tags=["test"],
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
