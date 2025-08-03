import unittest
from unittest.mock import patch, MagicMock

from manifest import Manifest

class TestUpdateManifest(unittest.TestCase):


    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    @patch('manifest.Manifest.__init__')
    @patch('urllib.request.urlretrieve')
    def test_download_success(self, mock_urlretrieve,mock_init,
                                    mock_jsonload,mock_jsondump,
                                    mock_open):

        #Arrange: manifest initial value, json download successfully
        initialManifest ={"initial":"manifest"}
        downloadedManifest = {"downloaded":"manifest","message":"messages","skins":{}}
        mock_init.return_value = None
        mock_open.return_value = "<MANIFEST.JSON>"
        mock_jsonload.return_value = downloadedManifest

        manifest = Manifest()
        manifest.manifest = initialManifest

        # Act: create the class
        manifest.updateManifest()


        # Assert: download called properly
        expected_url = f"{Manifest.BASE_URL}/manifest.json"
        expected_fpath = "manifest.json"
        mock_urlretrieve.assert_called_once_with(expected_url,expected_fpath)
        # Assert:  manifest updated
        self.assertEqual(manifest.manifest,downloadedManifest)
        # Assert: manifest not stored
        mock_jsondump.assert_not_called()

    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    @patch('manifest.Manifest.__init__')
    @patch('urllib.request.urlretrieve')
    def test_download_failed(self, mock_urlretrieve,mock_init,
                                    mock_jsonload,mock_jsondump,
                                    mock_open):

        #Arrange: manifest initial value, json download with error
        from urllib.error import HTTPError
        mock_urlretrieve.side_effect = HTTPError(url='mock_url', code=404, msg='Not Found', hdrs={}, fp=None)
        mock_init.return_value = None

        mock_open.return_value = "<MANIFEST.JSON>"

        manifest = Manifest()
        initialManifest ={"initial":"manifest"}
        manifest.manifest = initialManifest

        # Act: create the class
        manifest.updateManifest()


        # Assert: download called properly
        expected_url = f"{Manifest.BASE_URL}/manifest.json"
        expected_fpath = "manifest.json"
        mock_urlretrieve.assert_called_once_with(expected_url,expected_fpath)
        # Assert:  manifest unchanged
        self.assertEqual(manifest.manifest,initialManifest)
        # Assert: current manifest stored
        mock_jsondump.assert_called_once_with(initialManifest,mock_open.return_value,indent=4)

    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    @patch('manifest.Manifest.__init__')
    @patch('urllib.request.urlretrieve')
    def test_downloaded_corrupted_file(self, mock_urlretrieve,mock_init,
                                    mock_jsonload,mock_jsondump,
                                    mock_open):

        #Arrange: manifest initial value, downloaded invalid json
        mock_init.return_value = None
        import json
        mock_jsonload.side_effect = json.decoder.JSONDecodeError("msg","doc",12)

        mock_open.return_value = "<MANIFEST.JSON>"

        manifest = Manifest()
        initialManifest ={"initial":"manifest"}
        manifest.manifest = initialManifest

        # Act: create the class
        manifest.updateManifest()


        # Assert: download called properly
        expected_url = f"{Manifest.BASE_URL}/manifest.json"
        expected_fpath = "manifest.json"
        mock_urlretrieve.assert_called_once_with(expected_url,expected_fpath)
        # Assert:  manifest unchanged
        self.assertEqual(manifest.manifest,initialManifest)
        # Assert: current manifest stored
        mock_jsondump.assert_called_once_with(initialManifest,mock_open.return_value,indent=4)


    @patch('builtins.open')
    @patch('json.dump')
    @patch('json.load')
    @patch('manifest.Manifest.__init__')
    @patch('urllib.request.urlretrieve')
    def test_downloaded_wrong_json(self, mock_urlretrieve,mock_init,
                                    mock_jsonload,mock_jsondump,
                                    mock_open):

        #Arrange: manifest initial value, json download with wrong data
        initialManifest ={"initial":"manifest"}
        downloadedManifest = {"downloaded":"manifest"}
        mock_init.return_value = None
        mock_open.return_value = "<MANIFEST.JSON>"
        mock_jsonload.return_value = downloadedManifest

        manifest = Manifest()
        manifest.manifest = initialManifest

        # Act: create the class
        manifest.updateManifest()


        # Assert: download called properly
        expected_url = f"{Manifest.BASE_URL}/manifest.json"
        expected_fpath = "manifest.json"
        mock_urlretrieve.assert_called_once_with(expected_url,expected_fpath)
        # Assert:  manifest unchanged
        self.assertEqual(manifest.manifest,initialManifest)
        # Assert: current manifest stored
        mock_jsondump.assert_called_once_with(initialManifest,mock_open.return_value,indent=4)
