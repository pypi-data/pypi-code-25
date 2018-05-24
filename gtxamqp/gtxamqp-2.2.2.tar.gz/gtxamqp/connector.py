from twisted.internet import tcp


class FriendlyTCPConnector(tcp.Connector):

    def __str__(self):
        msg = "{type} | Address:{host}:{port} | bindAddress={bindAddress} | connector={connector}"
        return msg.format(type=str(self.__class__),
                          host=self.host,
                          port=self.port,
                          bindAddress=self.bindAddress,
                          connector=hex(id(self)))


def connectTCP(host, port, factory, timeout=30, bindAddress=None, reactor=None):
    """
    @see: twisted.internet.interfaces.IReactorTCP.connectTCP
    """
    if not reactor:
        from twisted.internet import reactor

    c = FriendlyTCPConnector(host,
                             port,
                             factory,
                             timeout,
                             bindAddress,
                             reactor)
    c.connect()
    return c
