import ftpbackup

confText = """
{
    "protocol": "ftp",
    "host": "localhost", // string - The hostname or IP address of the FTP server. Default: 'localhost'
    "port": 21, // integer - The port of the FTP server. Default: 21
    "user": "anonymous", // string - Username for authentication. Default: 'anonymous'
    "pass": "anonymous@", // string - Password for authentication. Default: 'anonymous@'
    "encoding": "big5",
    "remote": ".",
    "local": ".",
    "useGitIgnore": true,
    "gitIgnoreEncoding": "utf-8",
    "useFtpIgnore": true,
    "ftpIgnoreEncoding": "utf-8"
}
"""

conf = ftpbackup.Config()
conf.loadText(confText)

print(conf.protocol)
print(conf.host)
print(conf.port)
print(conf.user)
print(conf.passwd)
print(conf.encoding)
print(conf.remote)
print(conf.local)
print(conf.useGitIgnore)
print(conf.gitIgnoreEncoding)
print(conf.useFtpIgnore)
print(conf.ftpIgnoreEncoding)
