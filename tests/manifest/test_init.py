import unittest
from unittest.mock import patch, MagicMock, mock_open, call


from manifest import Manifest

class TestInit(unittest.TestCase):

    @patch('manifest.Manifest.defaultManifest')
    @patch('json.load')
    @patch('builtins.open',function=mock_open)
    def test_manifest_exists(self, mock_open, mock_jsonload, mock_default_manifest):
        #Arrange: file exists
        manifestData = {"a": "a","b":1}
        mock_jsonload.return_value = manifestData

        # Act: create the class
        manifest = Manifest()

        # Assert the manifest is the one loaded from "manifest.json"
        mock_default_manifest.assert_not_called()
        mock_open.assert_called_once_with("manifest.json")
        self.assertEqual(manifest.manifest,manifestData)

    @patch('manifest.Manifest.defaultManifest')
    @patch('json.load')
    @patch('builtins.open')
    def test_manifest_does_notexists(self, mock_open, mock_jsonload,
                                           mock_default_manifest):
        #Arrange: file does not exist
        manifestData = {"a": "a","b":1}
        defaultManifestData= {"defeault":"Manifest"}
        mock_jsonload.return_value = manifestData
        mock_open.side_effect = FileNotFoundError("[Errno 2] No such file or directory: 'manifest.json'")
        mock_default_manifest.return_value = defaultManifestData

        # Act: create the class
        manifest = Manifest()

        # Assert  it tried to open manifest.json but the data is from default manifest
        mock_open.assert_called_once_with("manifest.json")
        self.assertEqual(manifest.manifest,defaultManifestData)

    @patch('manifest.Manifest.defaultManifest')
    @patch('json.load')
    @patch('builtins.open')
    def test_manifest_corrupted(self, mock_open, mock_jsonload, mock_default_manifest):
        #Arrange: corrupted json
        import json
        mock_jsonload.side_effect = json.decoder.JSONDecodeError("msg","doc",12)
        defaultManifestData = {"defeault":"Manifest"}
        mock_default_manifest.return_value = defaultManifestData

        # Act: create the class
        manifest = Manifest()

        # Assert  it tried to open manifest.json but the data is from default manifest
        mock_open.assert_called_once_with("manifest.json")
        self.assertEqual(manifest.manifest,defaultManifestData)


class TestOthers(unittest.TestCase):


    @patch('manifest.Manifest.__init__')
    @patch('manifest.Manifest.hashSkin')
    @patch('os.listdir')
    @patch('builtins.open',function=mock_open)
    def test_defaultManifest_skip_folders(self, mock_open, mock_listdir, mock_hashSkin,mock_manifestInit):
        """ it should create a proper manifest by looking a the current skin folder """
        mock_listdir.return_value= ["skin1","_skip",".skip","__skip","skin2"]
        mock_hashSkin.side_effect = ["<HASH1>","<HASH2>"]
        mock_manifestInit.return_value = None

        manifest = Manifest()

        results = manifest.defaultManifest()

        expectedSkins = {'skin1': '<HASH1>', 'skin2': '<HASH2>'}
        expectedMessage = "Clicca su due colori per scambiarli.\nScopri se hai indovinato la sequenza misteriosa!"

        self.assertEqual(results["skins"],expectedSkins)
        self.assertEqual(results["message"],expectedMessage)



    @patch('manifest.Manifest.hashImages')
    def test_hashSkin(self,  mock_hashImages):
        """ it should call hash images properly"""
        #Arrange: nothing

        #Act:
        Manifest.hashSkin("mySkin")

        #Assert: call hash images
        import globals as G
        mock_hashImages.assert_called_once_with("mySkin",G.COLORS)


    @patch('hashlib.md5')
    @patch('builtins.open',function=mock_open)
    def test_hashSkin(self, mock_open, mock_hash):
        #Arrange: open the colors
        import globals as G
        mock_open().__enter__().read.side_effect = G.COLORS

        # Act: run the function
        Manifest.hashImages("mySkin",G.COLORS)

        # Assert: call has function properly
        for c in G.COLORS:
            self.assertIn(
                unittest.mock.call(f"imgs/skin/mySkin/{c}.png","rb"),
                mock_open.call_args_list)
        # Assert: colors are hashed in order
        mock_open().__enter__.read.assert_not_called()
        self.assertEqual(mock_hash().update.call_args_list,
                        [unittest.mock.call(c) for c in G.COLORS])
