import setuptools

setuptools.setup(
    name="Python-Parking2",
    version="1.1",
    author="Bartlomiej Mazur",
    author_email="bmazur230146@e-science.pl",
    description="A small example package",
    packages=['DataBaseConnection', 'ParkingLot', 'ParkingManagement'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)