from .BaseCompoment import BaseCompoment
import shutil
import os
import json


class TextCompoment(BaseCompoment):
    def __init__(self, splash: list[str], lang: dict, texts: str) -> None:
        self.lang = lang
        self.splash = splash
        self.texts = texts

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/texts", exist_ok=True)
        shutil.copytree(
            f"resources/{self.texts}",
            f"{self.output}/assets/minecraft/texts/",
            dirs_exist_ok=True,
        )
        os.makedirs(f"{self.output}/assets/minecraft/lang", exist_ok=True)
        with open(f"{self.output}/assets/minecraft/texts/splashes.txt", "a") as f:
            for _ in range(1000):
                f.write("\n".join(self.splash) + "\n")
        with open("tmp/assets/minecraft/lang/en_us.json", "w") as f:
            json.dump(self.lang, f)
