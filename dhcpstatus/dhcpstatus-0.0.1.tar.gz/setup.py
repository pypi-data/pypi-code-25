import setuptools

setuptools.setup(entry_points={
    'console_scripts': ['dhcpstatus_subnet = dhcpstatus.dhcp_status:main_subnet_status']})
