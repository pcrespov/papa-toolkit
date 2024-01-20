from setuptools import setup, find_packages

setup(
    packages=find_packages("src"),
    name="image-syncer",
    version="0.1.0",
    description="A script to organize images by their creation date.",
    author="pcrespov",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "Pillow==8.0",  # Add any other dependencies here
    ],
    console_scripts=[
        "image-syncer = image_syncer:main",
    ],
)
