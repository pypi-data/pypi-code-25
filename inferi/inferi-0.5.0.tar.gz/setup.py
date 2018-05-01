from setuptools import setup

setup(
 name="inferi",
 version="0.5.0",
 description="A statistics library.",
 url="https://inferi.samireland.com",
 author="Sam Ireland",
 author_email="mail@samireland.com",
 license="MIT",
 classifiers=[
  "Development Status :: 4 - Beta",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Topic :: Scientific/Engineering :: Mathematics",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.6",
 ],
 keywords="statistics probability data-science",
 packages=["inferi"],
 install_requires=["fuzz"]
)
