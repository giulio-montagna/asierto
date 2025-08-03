import globals as G
import os
import urllib.request
import logging
import json
import shutil

class Manifest:
    BASE_URL="https://dotto.fxiv.net/asierto/"
    def __init__(self):
        try:
            with open("manifest.json") as f:
                self.manifest = json.load(f)
        except Exception as e:
            logging.warning(f"Init Manifest: got error {e} falling to default")
            self.manifest = self.defaultManifest()

    def downloadSkinColor(self,type,color):
        fpath = f"imgs/skin/_{type}/{color}.png"
        url = f"{self.BASE_URL}imgs/skins/{type}/{color}.png"
        url = url.replace(" ","%20")
        try:
            urllib.request.urlretrieve(url, fpath)
            return fpath
        except Exception as e:
            logging.warning(f"Download Skin:  <{type}:{color}> ({url}) Download error: {e}")
            if os.path.exists(fpath):
                os.remove(fpath)
            return None

    def updateManifest(self):
        url = f"{Manifest.BASE_URL}/manifest.json"
        fpath = "manifest.json"
        # download manifest
        try:
            urllib.request.urlretrieve(url, fpath)
        except Exception as e:
            # in case of error store self.manifest as manifest.json
            logging.warning(f"Manifest download: error on download ({e}). Aborting")
            json.dump(self.manifest,open(fpath,"w"), indent=4)
            return

        try:
            manifest = json.load(open("manifest.json"))
        except Exception as e:
             logging.warning(f"Manifest download: unparseable json ({e}). Aborting")
             json.dump(self.manifest,open(fpath,"w"), indent=4)
             return
        # check manifest content
        if "message" not in manifest or "skins" not in manifest:
            # missing content, reject file
            logging.warning(f"Manifest download: missing content  ({manifest.keys()}). Aborting")
            json.dump(self.manifest,open(fpath,"w"), indent=4)
            return
        # otherwise update self.manifest
        logging.info(f"Updating manifest: {manifest}")
        self.manifest = manifest

    def updateSkins(self):
        for skin in self.manifest["skins"]:
            self.downloadSkin(skin)

    def downloadSkin(self,skin):
        try:
            hash = self.hashSkin(skin)
        except Exception as e:
            # can not hash, force download the skin
            logging.warning(f"Initial Hash: can not hash, force donwnloading")
            hash = ""
        if hash != self.manifest["skins"][skin]:
            try:
                # remove _skin folder if exists
                # remove __skin folder if exists
                self.cleanSkinFolder(skin)
                # create _skin folder
                logging.warning(f"Skin download: create folder imgs/skin/_{skin}")
                os.makedirs(f"imgs/skin/_{skin}", exist_ok=True)
                # download skin files in the skin folder
                for color in G.COLORS:
                    self.downloadSkinColor(skin,color)
                # hash the _skin
                try:
                    hash = self.hashSkin("_"+skin)
                except Exception as e:
                    logging.warning(f"Skin download: <{skin}> can not hash ({e}). Aborting")
                    self.cleanSkinFolder(skin)
                    return
                # check the hash
                if hash != self.manifest["skins"][skin]:
                    # if not ok remove _skin folder and abort
                    logging.warning(f"Skin download: <{skin}> hash failed ({hash}!={self.manifest['skins'][skin]}). Aborting")
                    self.cleanSkinFolder(skin)
                    return
                # if ok rename skin to __skin if exist
                self.backupSkin(skin)
                # rename _skin to skin
                self.finalizeNewSkin(skin)
                # remove __skin
                self.cleanSkinFolder(skin)
                return True
            # in case of error
            except Exception as e:
                logging.warning(f"Skin download: <{skin}> got error {e} line {e.__traceback__.tb_lineno}. Aborting")
                # if skin does not exists but __skin does exist rename it back
                self.tryRollbackSkin(skin)
                # remove _skin and __skin
                self.cleanSkinFolder(skin)
                return
        return False

    @staticmethod
    def backupSkin(skin):
        if os.path.exists(f"imgs/skin/{skin}"):
            shutil.move(f"imgs/skin/{skin}", f"imgs/skin/__{skin}")

    @staticmethod
    def tryRollbackSkin(skin):
        try:
            if os.path.exists(f"imgs/skin/__{skin}") and not os.path.exists(f"imgs/skin/{skin}"):
                logging.warning(f"Skin download: <{skin}> recovering backup skin folder")
                # rename it back
                shutil.move(f"imgs/skin/__{skin}", f"imgs/skin/{skin}")
        except Exception as e:
            logging.warning(f"Skin download: ERROR on rollback! ({e})")

    @staticmethod
    def finalizeNewSkin(skin):
        shutil.move(f"imgs/skin/_{skin}", f"imgs/skin/{skin}")


    def cleanSkinFolder(self,skin):
        try:
            shutil.rmtree(f"imgs/skin/_{skin}",ignore_errors=True)
        except Exception as e:
            logging.warning(f"Skin clean: <{skin}> {e}")
        try:
            shutil.rmtree(f"imgs/skin/__{skin}",ignore_errors=True)
        except Exception as e:
            logging.warning(f"Skin clean: <{skin}> {e}")



    @staticmethod
    def hashSkin(skin):
        return Manifest.hashImages(skin,G.COLORS)

    @staticmethod
    def hashImages(type,colors):
        import hashlib
        hash = hashlib.md5()
        for color in colors:
            with open(f"imgs/skin/{type}/{color}.png","rb") as f:
                hash.update(f.read())
        return hash.digest().hex()


    @staticmethod
    def defaultManifest():
        ret = {"skins":{},"message":"Clicca su due colori per scambiarli.\nScopri se hai indovinato la sequenza misteriosa!"}
        for skin in os.listdir("imgs/skin/"):
            if skin.startswith("_") or skin.startswith("."):
                continue
            try:
                ret["skins"][skin] = Manifest.hashSkin(skin)
            except Exception as e:
                logging.warning(f"Init Default Manifest: <{skin}> got error {e} skipping")
        return ret

    def message():
        doc = "The message property."
        def fget(self):
            return self.manifest["message"]
        return locals()
    message = property(**message())

    def types():
        doc = "The types property."
        def fget(self):
            return [skin.title() for skin in self.manifest["skins"]]
        return locals()
    types = property(**types())
