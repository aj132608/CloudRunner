import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloud-dsm-pkg-dealt.mineai", # Replace with your own username
    version="0.0.1",
    author="Mine AI",
    author_email="dealt.mineai@gmai.com",
    description="Cloud DSM stands for Distributed Service Manager"
                " is a scheduler for Cloud Agnostic job runs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)