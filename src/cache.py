import cv2
from collections import OrderedDict

# Least-recently-used cache
class LRUImageCache():
    def __init__(self, max_size: int):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get_image(self, section_id: int):
        if section_id not in self.cache:
            img = cv2.imread(f"./Datasets/SectionImages/{section_id}.jpg")
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
                self.cache[section_id] = img
            return img
        else:
            self.cache.move_to_end(section_id)
            return self.cache[section_id]
