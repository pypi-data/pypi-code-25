"""
Classes and utilities to manage IxExplorer statistics views.
"""

import time
from collections import OrderedDict
from enum import Enum
from past.builtins import xrange

from ixexplorer.api.ixapi import TclMember, FLAG_RDONLY, FLAG_IGERR, IxTclHalError
from ixexplorer.ixe_object import IxeObject


class IxeCapFileFormat(Enum):
    cap = 1
    enc = 2
    txt = 3
    mem = 4


class IxeStat(IxeObject):
    __tcl_command__ = 'stat'
    __tcl_members__ = [
            TclMember('duplexMode', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('link', type=int, flags=FLAG_RDONLY),
            TclMember('lineSpeed', type=int, flags=FLAG_RDONLY),
            TclMember('linkFaultState', type=int, flags=FLAG_RDONLY | FLAG_IGERR),

            TclMember('alignmentErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('asynchronousFramesSent', type=int, flags=FLAG_RDONLY),
            TclMember('bitsReceived', type=int, flags=FLAG_RDONLY),
            TclMember('bitsSent', type=int, flags=FLAG_RDONLY),
            TclMember('bytesReceived', type=int, flags=FLAG_RDONLY),
            TclMember('bytesSent', type=int, flags=FLAG_RDONLY),
            TclMember('captureFilter', type=int, flags=FLAG_RDONLY),
            TclMember('captureTrigger', type=int, flags=FLAG_RDONLY),
            TclMember('collisionFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('collisions', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('dataIntegrityErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('dataIntegrityFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('dribbleErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('droppedFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('excessiveCollisionFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('fcsErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('flowControlFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('framesReceived', type=int, flags=FLAG_RDONLY),
            TclMember('framesSent', type=int, flags=FLAG_RDONLY),
            TclMember('fragments', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('ipChecksumErrors', type=int, flags=FLAG_RDONLY),
            TclMember('ipPackets', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('lateCollisions', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('oversize', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('oversizeAndCrcErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('pauseAcknowledge', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('pauseEndFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('pauseOverwrite', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('prbsErroredBits', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('rxPingReply', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('rxPingRequest', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('scheduledFramesSent', type=int, flags=FLAG_RDONLY),
            TclMember('sequenceErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('sequenceFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('symbolErrorFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('symbolErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('synchErrorFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('tcpChecksumErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('tcpPackets', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('transmitDuration', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('txPingReply', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('txPingRequest', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('udpChecksumErrors', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('udpPackets', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('undersize', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('userDefinedStat1', type=int, flags=FLAG_RDONLY),
            TclMember('userDefinedStat2', type=int, flags=FLAG_RDONLY),
            TclMember('vlanTaggedFramesRx', type=int, flags=FLAG_RDONLY | FLAG_IGERR),

            TclMember('enableArpStats'),
            TclMember('enableDhcpStats'),
            TclMember('enableDhcpV6Stats'),
            TclMember('enableFcoeStats'),
            TclMember('enableIcmpStats'),
            TclMember('enableIgmpStats'),
            TclMember('enableMacSecStats'),
            TclMember('enablePosExtendedStats'),
            TclMember('enableProtocolServerStats'),
            TclMember('enableValidStats'),
            TclMember('fcoeRxSharedStatType1'),
            TclMember('fcoeRxSharedStatType2'),
    ]
    __tcl_commands__ = ['write']
    __get_command__ = None

    def __init__(self, parent):
        super(IxeStat, self).__init__(uri=parent.uri, parent=parent)

    def set_attributes(self, **attributes):
        super(IxeStat, self).set_attributes(**attributes)
        self.write()

    def read_stats(self, *stats):
        if not stats:
            stats = [m.attrname for m in self.__tcl_members__ if m.flags & FLAG_RDONLY]
        stats_values = OrderedDict(zip(stats, [-1] * len(stats)))
        for stat in stats:
            stats_values[stat] = getattr(self, stat)
        return stats_values


class IxeStatTotal(IxeStat):
    __get_command__ = 'get statAllStats'


class IxeStatRate(IxeStat):
    __get_command__ = 'getRate statAllStats'


class IxePgStats(IxeObject):
    __tcl_command__ = 'packetGroupStats'
    __tcl_members__ = [
            TclMember('averageLatency', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('bigSequenceError', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('bitRate', type=int, flags=FLAG_RDONLY),
            TclMember('byteRate', type=int, flags=FLAG_RDONLY),
            TclMember('duplicateFrames', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('firstTimeStamp', type=int, flags=FLAG_RDONLY),
            TclMember('frameRate', type=int, flags=FLAG_RDONLY),
            TclMember('lastTimeStamp', type=int, flags=FLAG_RDONLY),
            TclMember('maxDelayVariation', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('maxLatency', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('maxMinDelayVariation', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('maxminInterval', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('minDelayVariation', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('minLatency', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('numGroups', type=int, flags=FLAG_RDONLY),
            TclMember('prbsBerRatio', type=float, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('prbsBitsReceived', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('prbsErroredBits', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('readTimeStamp', type=int, flags=FLAG_RDONLY),
            TclMember('reverseSequenceError', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('sequenceGaps', type=int, flags=FLAG_RDONLY | FLAG_IGERR | FLAG_IGERR),
            TclMember('smallSequenceError', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('standardDeviation', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
            TclMember('totalByteCount', type=int, flags=FLAG_RDONLY),
            TclMember('totalFrames', type=int, flags=FLAG_RDONLY),
            TclMember('totalSequenceError', type=int, flags=FLAG_RDONLY | FLAG_IGERR),
    ]
    __get_command__ = 'getGroup'

    def __init__(self, parent, group_id):
        super(self.__class__, self).__init__(uri=group_id, parent=parent)

    def read_stats(self, *stats):
        if not stats:
            stats = [m.attrname for m in self.__tcl_members__ if m.flags & FLAG_RDONLY]
        stats_values = OrderedDict(zip(stats, [-1] * len(stats)))
        try:
            if int(self.get_attribute('totalFrames')):
                return self.get_attributes(FLAG_RDONLY, *stats)
        except IxTclHalError as _:
            pass

        # No group or no packets on group.
        return stats_values


class IxeStreamTxStats(IxeObject):
    __tcl_command__ = 'streamTransmitStats'
    __tcl_members__ = [
            TclMember('framesSent', type=int, flags=FLAG_RDONLY),
            TclMember('frameRate', type=int, flags=FLAG_RDONLY),
    ]
    __get_command__ = 'getGroup'

    def __init__(self, parent, group_id):
        super(self.__class__, self).__init__(uri=group_id, parent=parent)


class IxeStats(object):

    def __init__(self, session):
        self.session = session


class IxePortsStats(IxeStats):

    def __init__(self, session, *ports):
        super(self.__class__, self).__init__(session)
        self.ports = ports if ports else self.session.ports.values()

    def set_attributes(self, **attributes):
        for port in self.ports:
            IxeStatTotal(port).set_attributes(**attributes)

    def read_stats(self, *stats):
        """ Read port statistics from chassis.

        :param stats: list of requested statistics to read, if empty - read all statistics.
        """

        self.statistics = OrderedDict()
        for port in self.ports:
            port_stats = IxeStatTotal(port).get_attributes(FLAG_RDONLY, *stats)
            port_stats.update({c + '_rate': v for c, v in
                               IxeStatRate(port).get_attributes(FLAG_RDONLY, *stats).items()})
            self.statistics[str(port)] = port_stats
        return self.statistics


class pg_stats_dict(OrderedDict):
    """ If only one RX port - no need to specify port name. """
    def __getitem__(self, key):
        if key in self.keys():
            return OrderedDict.__getitem__(self, key)
        else:
            return list(self.values())[0][key]


class IxeStreamsStats(IxeStats):

    def __init__(self, session, *streams):
        """ Read stream statistics from chassis.

        :param session: Ixia session object.
        :param streams: list of requested streams. If empty - read statistics for all streams.
        """
        from ixexplorer.ixe_port import IxeReceiveMode

        super(self.__class__, self).__init__(session)

        self.tx_ports_streams = dict(zip(self.session.ports.values(), [[] for _ in xrange(len(self.session.ports))]))
        if streams:
            for stream in streams:
                self.tx_ports_streams[stream.parent].append(stream)
        else:
            for port in self.session.ports.values():
                self.tx_ports_streams[port] = port.streams.values()

        self.rx_ports = [p for p in self.session.ports.values() if
                         p.receiveMode & int(IxeReceiveMode.widePacketGroup.value)]

    def read_stats(self, *stats):
        """ Read stream statistics from chassis.

        :param stats: list of requested statistics to read, if empty - read all statistics.
        """
        from ixexplorer.ixe_stream import IxePacketGroupStream

        if not stats:
            stats = [m.attrname for m in IxePgStats.__tcl_members__ if m.flags & FLAG_RDONLY]

        # Read twice to refresh rate statistics.
        for port in self.tx_ports_streams:
            port.api.call_rc('streamTransmitStats get {} 1 4096'.format(port.uri))
        for rx_port in self.rx_ports:
            rx_port.api.call_rc('packetGroupStats get {} 0 65536'.format(rx_port.uri))
        time.sleep(1)

        self.statistics = OrderedDict()
        for tx_port, streams in self.tx_ports_streams.items():
            for stream in streams:
                stream_stats = OrderedDict()
                tx_port.api.call_rc('streamTransmitStats get {} 1 4096'.format(tx_port.uri))
                stream_tx_stats = IxeStreamTxStats(tx_port, stream.index)
                stream_stats_tx = {c: v for c, v in stream_tx_stats.get_attributes(FLAG_RDONLY).items()}
                stream_stats['tx'] = stream_stats_tx
                stream_stat_pgid = IxePacketGroupStream(stream).groupId
                stream_stats_pg = pg_stats_dict()
                for port in self.session.ports.values():
                    stream_stats_pg[str(port)] = OrderedDict(zip(stats, [-1] * len(stats)))
                for rx_port in self.rx_ports:
                    if not stream.rx_ports or rx_port in stream.rx_ports:
                        rx_port.api.call_rc('packetGroupStats get {} 0 65536'.format(rx_port.uri))
                        pg_stats = IxePgStats(rx_port, stream_stat_pgid)
                        stream_stats_pg[str(rx_port)] = pg_stats.read_stats(*stats)
                stream_stats['rx'] = stream_stats_pg
                self.statistics[str(stream)] = stream_stats
        return self.statistics
