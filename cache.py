import json
import os


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'trans_res.json')

class Cache:
    def __init__(self, save_path=DEFAULT_PATH, max_size=100000):
        self.save_path = save_path
        self.caches = {}
        self.max_size = max_size
        self.load()
    
    def load(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r', encoding='utf-8') as f:
                self.caches = json.load(f)
        else:
            self.caches = {}

    def save(self):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.caches, f, ensure_ascii=False, indent=4)
    
    def clear(self):
        self.caches = {}

    def get(self, key):
        return self.caches.get(key)

    def set(self, key, value):
        self.caches[key] = value
        if len(self.caches) > self.max_size:
            self.clear()

    def delete(self, key):
        if key in self.caches:
            del self.caches[key]