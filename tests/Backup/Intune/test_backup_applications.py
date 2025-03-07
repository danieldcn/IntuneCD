#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up applications."""


import json
import unittest
from pathlib import Path
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_applications import savebackup


class TestBackupApplications(unittest.TestCase):
    """Test class for backup_applications."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.scope_tag = {"roleScopeTagIds": ["0"]}
        self.app_base_data = {
            "value": [
                {
                    "@odata.type": "",
                    "id": "0",
                    "displayName": "test",
                    "vppTokenAppleId": "test@test.com",
                    "roleScopeTagIds": ["0"],
                }
            ]
        }
        self.batch_assignment_data = [
            {
                "value": [
                    {
                        "target": {
                            "groupId": "00000-0000-0000-0000-000000000000",
                            "groupName": "Group1",
                        }
                    }
                ]
            }
        ]
        self.batch_request_data = [
            {
                "id": "0",
                "roleScopeTagIds": ["0"],
            }
        ]
        self.object_assignment_data = [{"target": {"groupName": "Group1"}}]
        self.audit_data = {
            "value": [
                {
                    "resources": [
                        {"resourceId": "0", "auditResourceType": "MagicResource"}
                    ],
                    "activityDateTime": "2021-01-01T00:00:00Z",
                    "activityOperationType": "Patch",
                    "activityResult": "Success",
                    "actor": [{"auditActorType": "ItPro"}],
                }
            ]
        }

        self.batch_request_patch = patch(
            "src.IntuneCD.backup.Intune.backup_applications.batch_request"
        )
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.return_value = self.batch_request_data

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_applications.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = self.batch_assignment_data

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_applications.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = self.object_assignment_data

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_applications.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_applications.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_request_patch.stop()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_ios_vpp_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.iosVppApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/iOS").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/iOS/test_iOSVppApp_test.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_macOS_vpp_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.macOsVppApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/macOS").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/macOS/test_macOSVppApp_test.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_vpp_app_exclude_licensecount(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.iosVppApp"
        self.app_base_data["value"][0]["usedLicenseCount"] = "1"

        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.exclude = ["VPPusedLicenseCount"]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        app_data = json.load(
            open(
                self.directory.path + "/Applications/iOS/test_iOSVppApp_test.json",
                encoding="utf-8",
            )
        )

        self.assertTrue(app_data.get("VPPusedlicenseCount") is None)

    def test_backup_win32_lob_app_and_displayVersion(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.win32LobApp"
        self.app_base_data["value"][0]["displayVersion"] = "1.0.0"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Windows").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/Windows/test_Win32_1_0_0.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_win32_lob_app_no_displayVersion(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.win32LobApp"
        self.app_base_data["value"][0]["displayVersion"] = None
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Windows").exists())
        self.assertTrue(
            Path(self.directory.path + "/Applications/Windows/test_Win32.json").exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_msi_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windowsMobileMSI"
        self.app_base_data["value"][0]["productVersion"] = "1.0.0"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Windows").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/Windows/test_WinMSI_1_0_0.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_android_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.androidManagedStoreApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Android").exists())
        self.assertTrue(
            Path(
                self.directory.path
                + "/Applications/Android/test_androidManagedStoreApp.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_microsoft_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.microsoftApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Windows").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/Windows/test_microsoftApp.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_office_suite_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.microsoftOfficeSuiteApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(
            Path(self.directory.path + "/Applications/Office Suite").exists()
        )
        self.assertTrue(
            Path(
                self.directory.path
                + "/Applications/Office Suite/test_microsoftOfficeSuiteApp.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_web_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.webApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/Web App").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/Web App/test_webApp.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_other_app(self):
        """The folder should be created, the file should be created, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.macOSother"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )

        self.assertTrue(Path(self.directory.path + "/Applications/macOS").exists())
        self.assertTrue(
            Path(
                self.directory.path + "/Applications/macOS/test_macOSother.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""
        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            self.append_id,
            False,
            False,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.iosVppApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, True, False, False
        )

        self.assertTrue(
            Path(
                self.directory.path + "/Applications/iOS/test_iOSVppApp_test__0.json"
            ).exists()
        )

    def test_backup_scope_tag_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.app_base_data["value"][0]["@odata.type"] = "#microsoft.graph.iosVppApp"
        self.makeapirequest.side_effect = [self.app_base_data, self.scope_tag]

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            True,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertTrue(
            Path(
                self.directory.path + "/Applications/iOS/test_iOSVppApp_test__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
