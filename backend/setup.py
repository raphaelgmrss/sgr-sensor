from setuptools import setup, Extension
import os

extensions = []

for root, _, files in os.walk("./api"):
    for file in files:
        if file.endswith(".py") and file not in ("__init__.py", "run.py"):
            path = os.path.join(root, file)
            module = path.replace("/", ".").replace("\\", ".")[4:-3]
            extensions.append(Extension(module, [path]))

setup(
    name="flask_api",
    version="1.0",
    ext_modules=extensions,
)
