from setuptools import setup, find_packages

setup(
    name="transcriber",
    version="0.0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "google-cloud-storage>=2.14.0",
        "google-cloud-pubsub>=2.19.0",
        "google-cloud-logging>=3.9.0",
        "google-cloud-monitoring>=2.17.0",
        "google-cloud-trace>=1.13.0",
    ],
)
