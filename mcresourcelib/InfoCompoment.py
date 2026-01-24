from .BaseCompoment import BaseCompoment
import shutil
import json


class InfoCompoment(BaseCompoment):
    def __init__(self, data, icon) -> None:
        self.data = data
        self.icon = icon

    def run(self) -> None:
        with open(f"{self.output}/pack.mcmeta", "w") as f:
            json.dump(self.data, f)
        shutil.copy("resources/" + self.icon, self.output)
