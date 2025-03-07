#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up profiles."""


import json
import unittest
from pathlib import Path
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_profiles import savebackup

BATCH_ASSIGNMENT = [{"value": [{"target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupCustomProfiles(unittest.TestCase):
    """Test class for backup_profiles."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False

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

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_macOS_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSCustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "payload": "SGkgdGhlcmUgcHJldHR5",
                    "payloadFileName": "test.mobileconfig",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_macOSCustomConfiguration.json"
            ).exists()
        )
        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/mobileconfig/test.mobileconfig"
            ).exists()
        )
        self.assertEqual(2, self.count["config_count"])

    def test_backup_ios_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.iosCustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "payload": "SGkgdGhlcmUgcHJldHR5",
                    "payloadFileName": "test.mobileconfig",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_iosCustomConfiguration.json"
            ).exists()
        )
        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/mobileconfig/test.mobileconfig"
            ).exists()
        )
        self.assertEqual(2, self.count["config_count"])

    def test_backup_windows_custom_profile_encrypted(self):
        """The file should be created and the count should be 1."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": True,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": [],
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_windows_custom_profile_encrypted_ignore_omas(self):
        """The file should be created and the count should be 1."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": True,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": "encrypted value",
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            True,
            False,
            None,
        )

        with open(
            f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json",
            "r",
            encoding="utf-8",
        ) as file:
            data = file.read()
            data = json.loads(data)
            print(data)
            self.assertTrue("password" not in data["omaSettings"][0]["value"])

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_windows_custom_profile_not_encrypted(self):
        """The file should be created and the count should be 1."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": False,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": [],
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_scope_tags_and_audit_macOS_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSCustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "payload": "SGkgdGhlcmUgcHJldHR5",
                    "payloadFileName": "test.mobileconfig",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertEqual(2, self.count["config_count"])

    def test_backup_scope_tags_and_audit_windows_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": False,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": [],
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertEqual(1, self.count["config_count"])


class TestBackupStandardProfiles(unittest.TestCase):
    """Test class for backup_profiles."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False

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

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_profiles.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_non_custom_profile(self):
        """The file should be created and the count should be 1."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    "id": "0",
                    "displayName": "test",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            self.exclude,
            "",
            self.append_id,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_macOSGeneralDeviceConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "test1",
            self.append_id,
            False,
            False,
            None,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_prefix_no_match(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    "id": "0",
                    "displayName": "test",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "test1",
            self.append_id,
            False,
            False,
            None,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    "id": "0",
                    "displayName": "test",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            True,
            False,
            False,
            None,
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_macOSGeneralDeviceConfiguration__0.json"
            ).exists()
        )

    def test_backup_scope_tags_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    "id": "0",
                    "displayName": "test",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            self.append_id,
            False,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertEqual(1, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
