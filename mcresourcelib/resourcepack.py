import os
from .BaseCompoment import BaseCompoment
from .InfoCompoment import InfoCompoment, shutil


class Resourcepack:
    def __init__(self, info: dict, icon: str) -> None:
        self.compoments: list[BaseCompoment] = [InfoCompoment(info, icon)]

    def add(self, compoment) -> None:
        self.compoments.append(compoment)

    def remove(self, compoment: BaseCompoment) -> None:
        self.compoments.remove(compoment)

    def pop(self, index: int):
        self.compoments.pop(index)

    def run(self, output: str) -> None:
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")
        os.mkdir("tmp")
        for _, v in enumerate(self.compoments):
            v.run()
        os.chdir("tmp")
        os.system(f"7z a -mx=0 -r {output} *")
        os.chdir("..")
