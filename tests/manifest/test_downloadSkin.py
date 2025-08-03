import unittest
from unittest.mock import patch, MagicMock,call

from manifest import Manifest

@patch('manifest.Manifest.__init__', return_value=None)
class TestDownloadSkin(unittest.TestCase):

    @patch('manifest.Manifest.hashSkin')
    def test_hash_matching_no_download_needed(self, mock_hashSkin, mock_manifestInit):
        """it should not download when current skin hash matches manifest hash."""
        # Arrange: current hash equals manifest hash
        expected_hash = "matching_hash_123"
        mock_hashSkin.return_value = expected_hash

        manifest = Manifest()
        manifest.manifest = {"skins": {"test_skin": expected_hash}}

        # Act: call downloadSkin
        result = manifest.downloadSkin("test_skin")

        # Assert:
        # 1. hashSkin called once to verify current hash
        mock_hashSkin.assert_called_once_with("test_skin")
        # 2. no download needed, returns False
        self.assertFalse(result)

    @patch('manifest.Manifest.cleanSkinFolder')
    @patch('shutil.move')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('manifest.Manifest.downloadSkinColor')
    @patch('manifest.Manifest.hashSkin')
    def test_hash_different_download_success(self, mock_hashSkin, mock_downloadSkinColor,
                                         mock_makedirs, mock_exists, mock_move,
                                         mock_cleanSkinFolder, mock_manifestInit):
          """It should download skin when hash differs and complete successfully."""
          # Arrange: different hashes, successful operations
          current_hash = "old_hash_123"
          manifest_hash = "new_hash_456"
          final_hash = "new_hash_456"  # matches manifest after download

          # hashSkin called twice: initial check, final verification
          mock_hashSkin.side_effect = [current_hash, final_hash]
          mock_downloadSkinColor.return_value = "imgs/skin/_test_skin/color.png"
          mock_exists.side_effect = [True, False]  # __skin exists, skin doesn't exist initially

          manifest = Manifest()
          manifest.manifest = {"skins": {"test_skin": manifest_hash}}

          # Act: call downloadSkin
          result = manifest.downloadSkin("test_skin")

          # Assert: complete download flow
          # 1. Initial hash check
          self.assertEqual(mock_hashSkin.call_args_list[0], call("test_skin"))

          # 2. Cleanup and folder creation
          mock_cleanSkinFolder.assert_any_call("test_skin")
          mock_makedirs.assert_called_once_with("imgs/skin/_test_skin", exist_ok=True)

          # 3. Download all colors (assuming G.COLORS has specific colors)
          import globals as G
          mock_downloadSkinColor.assert_has_calls([call("test_skin",c) for c in G.COLORS])

          # 4. Final hash verification
          self.assertEqual(mock_hashSkin.call_args_list[1], call("_test_skin"))


          # 5. Folder operations: __skin backup, _skin to skin rename
          expected_moves = [
              call("imgs/skin/test_skin", "imgs/skin/__test_skin"),
              call("imgs/skin/_test_skin", "imgs/skin/test_skin"),
          ]
          mock_move.assert_has_calls(expected_moves)

          # 6. Final cleanup
          mock_cleanSkinFolder.assert_called_with("test_skin")  # final cleanup

          # 7. Returns True for successful download
          self.assertTrue(result)

    @patch('manifest.Manifest.cleanSkinFolder')
    @patch('os.makedirs')
    @patch('manifest.Manifest.downloadSkinColor')
    @patch('manifest.Manifest.hashSkin')
    def test_download_colors_failure(self, mock_hashSkin, mock_downloadSkinColor,
                             mock_makedirs, mock_cleanSkinFolder, mock_manifestInit):
        """It should cleanup and return None when downloadSkinColor fails."""
        # Arrange: different hashes, downloadSkinColor silently fails, hash fails
        current_hash = "old_hash_123"
        manifest_hash = "new_hash_456"

        mock_hashSkin.side_effect = [current_hash, FileNotFoundError("[Errno 2] No such file or directory: 'something.png'")]


        manifest = Manifest()
        manifest.manifest = {"skins": {"test_skin": manifest_hash}}

        # Act: call downloadSkin
        result = manifest.downloadSkin("test_skin")

        # Assert: error handling flow
        # 1. Initial hash check
        mock_hashSkin.assert_any_call("test_skin")

        # 2. Folder creation attempted
        mock_makedirs.assert_called_once_with("imgs/skin/_test_skin", exist_ok=True)

        # 3. Cleanup called due to download failures
        mock_cleanSkinFolder.assert_called_with("test_skin")

        # 4. Returns None for failure
        self.assertIsNone(result)

    @patch('manifest.Manifest.cleanSkinFolder')
    @patch('os.makedirs')
    @patch('manifest.Manifest.downloadSkinColor')
    @patch('manifest.Manifest.hashSkin')
    def test_final_hash_does_not_match(self, mock_hashSkin, mock_downloadSkinColor,
                                   mock_makedirs, mock_cleanSkinFolder, mock_manifestInit):
        """It should cleanup and return None when final hash doesn't match manifest."""
        # Arrange: different hashes, download succeeds but final hash is wrong
        current_hash = "old_hash_123"
        manifest_hash = "expected_hash_456"
        final_hash = "wrong_hash_789"  # doesn't match manifest

        # hashSkin called twice: initial check, final verification
        mock_hashSkin.side_effect = [current_hash, final_hash]
        mock_downloadSkinColor.return_value = "imgs/skin/_test_skin/color.png"

        manifest = Manifest()
        manifest.manifest = {"skins": {"test_skin": manifest_hash}}

        # Act: call downloadSkin
        result = manifest.downloadSkin("test_skin")

        # Assert: hash mismatch handling
        # 1. Initial hash check
        self.assertEqual(mock_hashSkin.call_args_list[0], call("test_skin"))

        # 2. Final hash verification (on _test_skin)
        self.assertEqual(mock_hashSkin.call_args_list[1], call("_test_skin"))

        # 5. Cleanup called due to hash mismatch
        mock_cleanSkinFolder.assert_called_with("test_skin")

        # 6. Returns None for hash verification failure
        self.assertIsNone(result)


    @patch('manifest.Manifest.cleanSkinFolder')
    @patch('shutil.move')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('manifest.Manifest.downloadSkinColor')
    @patch('manifest.Manifest.hashSkin')
    def test_initial_hash_error_forces_download(self, mock_hashSkin, mock_downloadSkinColor,
                                            mock_makedirs, mock_exists, mock_move,
                                            mock_cleanSkinFolder, mock_manifestInit):
        """It should force download when initial hashSkin fails."""
        # Arrange: initial hashSkin throws exception, final hash succeeds
        manifest_hash = "expected_hash_456"
        final_hash = "expected_hash_456"

        # hashSkin: first call fails, second call succeeds
        mock_hashSkin.side_effect = [
          FileNotFoundError("No such file"),  # initial hash fails
          final_hash  # final hash succeeds
        ]
        mock_exists.side_effect = [True, False]  # __skin exists, skin doesn't exist

        manifest = Manifest()
        manifest.manifest = {"skins": {"test_skin": manifest_hash}}

        # Act: call downloadSkin
        result = manifest.downloadSkin("test_skin")

        # Assert: forced download due to hash error
        # 1. Initial hash check attempted and failed
        self.assertEqual(mock_hashSkin.call_args_list[0], call("test_skin"))

        # 2. downloadSkinColor called
        mock_downloadSkinColor.assert_called()



    @patch('manifest.Manifest.tryRollbackSkin')
    @patch('manifest.Manifest.finalizeNewSkin')
    @patch('manifest.Manifest.backupSkin')
    @patch('manifest.Manifest.cleanSkinFolder')
    @patch('manifest.Manifest.downloadSkinColor')
    @patch('manifest.Manifest.hashSkin')
    @patch('os.makedirs')
    def test_rollback(self, mock_move, mock_hashSkin,
                      mock_downloadSkinColor,mock_cleanSkinFolder,
                      mock_backupSkin, mock_finalizeNewSkin, mock_tryRollbackSkin,
                      mock_manifestInit):
        """It should restore from __skin when first move succeeds but second move fails."""
        # Arrange: first move succeeds, second move fails
        current_hash = "old_hash_123"
        manifest_hash = "new_hash_456"
        final_hash = "new_hash_456"

        mock_hashSkin.side_effect = [current_hash, final_hash]
        mock_finalizeNewSkin.side_effect = OSError("Permission denied")

        manifest = Manifest()
        manifest.manifest = {"skins": {"test_skin": manifest_hash}}

        # Act: call downloadSkin
        result = manifest.downloadSkin("test_skin")

        # Assert: rollback after failed second move

        # 1. hashSkin called properly
        mock_hashSkin.assert_has_calls([call("test_skin"),call("_test_skin")])

        # 2. backup successful
        mock_backupSkin.assert_called_once_with("test_skin")

        # 3. try to rollback
        mock_tryRollbackSkin.assert_called_once_with("test_skin")

        # 4. clean skin folder called once at the beginning and once while rollback
        mock_cleanSkinFolder.assert_has_calls([call("test_skin"),call("test_skin")])

        # 5. Returns None for failure
        self.assertIsNone(result)
