from setuptools import setup, find_packages

setup(
    packages=find_packages("src"),
    name="mediakit",
    version="0.1.0",
    description="Tools to manage image and video files",
    author="pcrespov",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "Pillow==8.0",  # Add any other dependencies here
    ],
    console_scripts=[
        "image-syncer = papakit.image_syncer:main",
    ],
)
