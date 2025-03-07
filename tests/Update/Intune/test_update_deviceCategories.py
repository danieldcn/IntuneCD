# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_deviceCategories import update


class TestUpdatedeviceCategories(unittest.TestCase):
    """Test class for update_deviceCategories."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Device Categories")
        self.directory.write(
            "Device Categories/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write(
            "Device Categories/test.txt", '{"test": "test"}', encoding="utf-8"
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                }
            ]
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test1",
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_deviceCategories.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_deviceCategories.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_deviceCategories.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_deviceCategories.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_deviceCategories.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()
        self.makeapirequestPost_patch.stop()
        self.makeapirequestDelete_patch.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.repo_data["testvalue2"] = "test2"
        self.mem_data["value"][0]["testvalue"] = "test"
        self.mem_data["value"][0]["testvalue2"] = "test1"

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"
        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=[]
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_config_remove(self):
        """The count should be 0 and makeapirequestPost should be called."""

        os.remove(self.directory.path + "/Device Categories/test.json")
        self.count = update(
            self.directory.path, self.token, report=False, remove=True, scope_tags=[]
        )

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_scope_tags(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

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
