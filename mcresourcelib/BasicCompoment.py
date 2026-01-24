from .BaseCompoment import BaseCompoment
import shutil


class BasicCompoment(BaseCompoment):
    def __init__(self, dir: str) -> None:
        self.dir = dir

    def run(self) -> None:
        shutil.copytree(
            "resources/" + self.dir, f"{self.output}/assets/", dirs_exist_ok=True
        )
