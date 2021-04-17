import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='queue_bot',
    version="0.0.1",
    install_requires=requirements,
    author="Matthew Wen",
    author_email="mattwen2018@gmail.com",
    description="QueueUpBot",
    packages=setuptools.find_packages(),
    scripts=["bin/queueup-bot", "bin/report"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
