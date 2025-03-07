#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Scope Tags."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_scopeTags import update

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "test1"}}]}]

OBJECT_ASSIGNMENT = [{"target": {"groupName": "test"}}]

UPDATE_ASSIGNMENT = {"assignments": [{"target": {"groupName": "test1"}}]}


class TestUpdatescopeTags(unittest.TestCase):
    """Test class for update_scopeTags."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Scope Tags")
        self.directory.write(
            "Scope Tags/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write("Scope Tags/test.txt", "txt", encoding="utf-8")
        self.token = "token"

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#test.test.test",
                    "id": "1",
                    "displayName": "test",
                    "description": "test",
                    "isBuiltIn": False,
                    "assignments": [{"target": {"groupName": "test1"}}],
                }
            ]
        }

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()
        self.update_assignment.return_value = UPDATE_ASSIGNMENT

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = {
            "@odata.type": "#test.test.test",
            "id": "1",
            "displayName": "test",
            "description": "test1",
            "isBuiltIn": False,
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_scopeTags.makeapirequestDelete"
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
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            assignment=True,
            report=False,
            create_groups=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            create_groups=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.load_file.return_value = {
            "@odata.type": "#test.test.test",
            "id": "1",
            "displayName": "test",
            "description": "test",
            "isBuiltIn": False,
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.count = update(
            self.directory.path,
            self.token,
            assignment=True,
            report=False,
            create_groups=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.load_file.return_value = {
            "@odata.type": "#test.test.test",
            "id": "1",
            "displayName": "test",
            "description": "test",
            "isBuiltIn": False,
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            create_groups=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.makeapirequest.return_value = {
            "value": [
                {"@odata.type": "#test.test.test", "id": "1", "displayName": "test1"}
            ]
        }

        self.count = update(
            self.directory.path,
            self.token,
            assignment=True,
            report=False,
            create_groups=False,
            remove=False,
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config_isBultIn_true(self):
        """makeapirequestDelete should not be called."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#test.test.test",
                    "id": "1",
                    "displayName": "test",
                    "description": "test1",
                    "isBuiltIn": False,
                    "assignments": [{"target": {"groupName": "test1"}}],
                },
                {
                    "@odata.type": "#test.test.test",
                    "id": "0",
                    "displayName": "test2",
                    "description": "test2",
                    "isBuiltIn": True,
                    "assignments": [{"target": {"groupName": "test1"}}],
                },
            ]
        }

        self.update = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            create_groups=False,
            remove=True,
        )

        self.assertEqual(self.makeapirequestDelete.call_count, 0)

    def test_remove_config_isBultIn_false(self):
        """makeapirequestDelete should be called."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#test.test.test",
                    "id": "1",
                    "displayName": "test",
                    "description": "test1",
                    "isBuiltIn": False,
                    "assignments": [{"target": {"groupName": "test1"}}],
                },
                {
                    "@odata.type": "#test.test.test",
                    "id": "2",
                    "displayName": "test2",
                    "description": "test2",
                    "isBuiltIn": False,
                    "assignments": [{"target": {"groupName": "test1"}}],
                },
            ]
        }

        self.update = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            create_groups=False,
            remove=True,
        )

        self.assertEqual(self.makeapirequestDelete.call_count, 1)


if __name__ == "__main__":
    unittest.main()
