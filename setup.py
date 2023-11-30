import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="asyncio-pipe",
    version="0.0.2",
    author="Roger Iyengar",
    author_email="ri@rogeriyengar.com",
    description="Non-blocking IPC with Asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rogerthat94/asyncio-pipe",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License",
    ],
    python_requires=">=3.6",
)
