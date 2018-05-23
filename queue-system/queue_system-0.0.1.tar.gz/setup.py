import setuptools

setuptools.setup(
    name="queue_system",
    version="0.0.1",
    author="Matej Jularic",
    author_email="matej@morpheuszone.com",
    description="Publisher and consumer written for rabbitMQ",
    packages=setuptools.find_packages(),
    install_requires=['pika'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)