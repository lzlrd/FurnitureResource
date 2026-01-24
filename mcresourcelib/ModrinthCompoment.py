from typing import Optional
from .BaseCompoment import BaseCompoment
import requests
import zipfile
import shutil
import os
import io


class ModrinthCompoment(BaseCompoment):
    def __init__(
        self, project: str, mc_version: Optional[str] = None, id: Optional[str] = None
    ) -> None:
        self.mc_version = mc_version
        self.project = project
        self.id = id

    def copy(self) -> None:
        shutil.copytree(
            f"downloads/{self.project}/assets/",
            f"{self.output}/assets/",
            dirs_exist_ok=True,
        )

    def download(self, url: str) -> None:
        res = requests.get(url)
        res.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(res.content)) as zip:
            for i in zip.infolist():
                if i.filename.startswith("assets/"):
                    zip.extract(i, f"downloads/{self.project}")
        print(f"[modrinth] {self.project} download compleate")
        self.copy()

    def run(self) -> None:
        if self.project in os.listdir("downloads"):
            self.copy()
            print(f"[modrinth] {self.project} cached")
            return
        print(f"[modrinth] {self.project} start download")
        res = requests.get(
            f"https://api.modrinth.com/v2/project/{self.project}/version"
        )
        res.raise_for_status()
        for i in res.json():
            if self.id == id:
                self.download(i["files"][0]["url"])
                return
            if self.mc_version in set(i["game_versions"]):
                self.download(i["files"][0]["url"])
                return
        raise ValueError("cannot find file")
