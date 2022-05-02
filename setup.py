# create a setup script for colab_connect
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="colab_connect",
    version="0.0.2",
    author="Sifat",
    author_email="hossain0338@gmail.com",
    description="Colab Connect",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hossain0338/colab_connect",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    project_urls={
        "Bug Tracker": "https://github.com/hossain0338/colab_connect/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
   'pyngrok',
]
)
