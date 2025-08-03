import unittest
from unittest.mock import patch, MagicMock

from manifest import Manifest

class TestDownloadSkinColor(unittest.TestCase):

    @patch('os.path.exists')
    @patch('os.remove')
    @patch('urllib.request.urlretrieve')
    def test_download_failed_with_partial_file(self, mock_urlretrieve, mock_remove, mock_exists):
        # Arrange: Not found + existing partial file ( is it realistic?)
        from urllib.error import HTTPError
        mock_urlretrieve.side_effect = HTTPError(url='mock_url', code=404, msg='Not Found', hdrs={}, fp=None)
        mock_exists.return_value = True

        manifest = Manifest()

        # Act: call the function
        result = manifest.downloadSkinColor("human", "red")

        # Assert: URL called
        expected_url = f"{Manifest.BASE_URL}/skins/human/red.png"
        expected_fpath = "imgs/skin/_human/red.png"
        mock_urlretrieve.assert_called_once_with(expected_url, expected_fpath)
        # Assert: file removed
        mock_remove.assert_called_once_with(expected_fpath)
        # Assert: return None
        self.assertIsNone(result)

    @patch('os.path.exists')
    @patch('os.remove')
    @patch('urllib.request.urlretrieve')
    def test_download_failed_without_partial_file(self, mock_urlretrieve, mock_remove, mock_exists):
        # Arrange: Not found + no  partial file
        from urllib.error import HTTPError
        mock_urlretrieve.side_effect = HTTPError(url='mock_url', code=404, msg='Not Found', hdrs={}, fp=None)
        mock_exists.return_value = False

        manifest = Manifest()

        # Act: call the function
        result = manifest.downloadSkinColor("human", "red")

        # Assert: URL called
        expected_url = f"{Manifest.BASE_URL}/skins/human/red.png"
        expected_fpath = "imgs/skin/_human/red.png"
        mock_urlretrieve.assert_called_once_with(expected_url, expected_fpath)
        # Assert: file not removed
        mock_remove.assert_not_called()
        # Assert: return None
        self.assertIsNone(result)


    @patch('os.path.exists')
    @patch('os.remove')
    @patch('urllib.request.urlretrieve')
    def test_download_timedout_with_partial_file(self, mock_urlretrieve, mock_remove, mock_exists):
        # Arrange: Time Out +  partial file
        from urllib.error import  URLError
        mock_urlretrieve.side_effect = URLError("Timeout reached during connection")
        mock_exists.return_value = True

        manifest = Manifest()

        # Act: call the function
        result = manifest.downloadSkinColor("human", "red")

        # Assert: URL called
        expected_url = f"{Manifest.BASE_URL}/skins/human/red.png"
        expected_fpath = "imgs/skin/_human/red.png"
        mock_urlretrieve.assert_called_once_with(expected_url, expected_fpath)
        # Assert: file removed
        mock_remove.assert_called_once_with(expected_fpath)
        # Assert: return None
        self.assertIsNone(result)


    @patch('os.path.exists')
    @patch('os.remove')
    @patch('urllib.request.urlretrieve')
    def test_download_success(self, mock_urlretrieve, mock_remove, mock_exists):
        # Arrange:  partial file
        mock_exists.return_value = True

        manifest = Manifest()

        # Act: call the function
        result = manifest.downloadSkinColor("human", "red")

        # Assert: URL called
        expected_url = f"{Manifest.BASE_URL}/skins/human/red.png"
        expected_fpath = "imgs/skin/_human/red.png"
        mock_urlretrieve.assert_called_once_with(expected_url, expected_fpath)
        # Assert: file removed
        mock_remove.assert_not_called()
        # Assert: return None
        self.assertEqual(result,expected_fpath)
