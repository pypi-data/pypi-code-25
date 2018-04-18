# -*- coding: utf-8 -*-
#
# python3-RevPiModIO
#
# Webpage: https://revpimodio.org/
# (c) Sven Sager, License: LGPLv3
#
"""RevPiModIO Hauptklasse fuer piControl0 Zugriff."""
import warnings
from json import load as jload
from os import access, F_OK, R_OK
from queue import Empty
from signal import signal, SIG_DFL, SIGINT, SIGTERM
from threading import Thread, Event

from . import app as appmodule
from . import device as devicemodule
from . import helper as helpermodule
from . import summary as summarymodule
from .io import IOList


class RevPiModIO(object):

    """Klasse fuer die Verwaltung der piCtory Konfiguration.

    Diese Klasse uebernimmt die gesamte Konfiguration aus piCtory und bilded
    die Devices und IOs ab. Sie uebernimmt die exklusive Verwaltung des
    Prozessabbilds und stellt sicher, dass die Daten synchron sind.
    Sollten nur einzelne Devices gesteuert werden, verwendet man
    RevPiModIOSelected() und uebergibt bei Instantiierung eine Liste mit
    Device Positionen oder Device Namen.

    """

    def __init__(
            self, autorefresh=False, monitoring=False, syncoutputs=True,
            procimg=None, configrsc=None, simulator=False):
        """Instantiiert die Grundfunktionen.

        @param autorefresh Wenn True, alle Devices zu autorefresh hinzufuegen
        @param monitoring In- und Outputs werden gelesen, niemals geschrieben
        @param syncoutputs Aktuell gesetzte Outputs vom Prozessabbild einlesen
        @param procimg Abweichender Pfad zum Prozessabbild
        @param configrsc Abweichender Pfad zur piCtory Konfigurationsdatei
        @param simulator Laedt das Modul als Simulator und vertauscht IOs

        """
        self._autorefresh = autorefresh
        self._configrsc = configrsc
        self._monitoring = monitoring
        self._procimg = "/dev/piControl0" if procimg is None else procimg
        self._simulator = simulator
        self._syncoutputs = syncoutputs

        # TODO: bei simulator und procimg prüfen ob datei existiert / anlegen?

        # Private Variablen
        self.__cleanupfunc = None
        self._buffedwrite = False
        self._exit = Event()
        self._imgwriter = None
        self._ioerror = 0
        self._length = 0
        self._looprunning = False
        self._lst_devselect = []
        self._lst_refresh = []
        self._maxioerrors = 0
        self._myfh = None
        self._th_mainloop = None
        self._waitexit = Event()

        # Modulvariablen
        self.core = None

        # piCtory Klassen
        self.app = None
        self.device = None
        self.io = None
        self.summary = None

        # Nur Konfigurieren, wenn nicht vererbt
        if type(self) == RevPiModIO:
            self._configure(self.get_jconfigrsc())

    def __del__(self):
        """Zerstoert alle Klassen um aufzuraeumen."""
        if hasattr(self, "_exit"):
            self.exit(full=True)
            if self._myfh is not None:
                self._myfh.close()

    def __evt_exit(self, signum, sigframe):
        """Eventhandler fuer Programmende.
        @param signum Signalnummer
        @param sigframe Signalframe"""
        signal(SIGINT, SIG_DFL)
        signal(SIGTERM, SIG_DFL)
        self.exit(full=True)
        if self.__cleanupfunc is not None:
            self.readprocimg()
            self.__cleanupfunc()
            self.writeprocimg()

    def _configure(self, jconfigrsc):
        """Verarbeitet die piCtory Konfigurationsdatei."""

        # Filehandler konfigurieren, wenn er noch nicht existiert
        if self._myfh is None:
            self._myfh = self._create_myfh()

        # App Klasse instantiieren
        self.app = appmodule.App(jconfigrsc["App"])

        # Devicefilter anwenden
        if len(self._lst_devselect) > 0:
            lst_found = []

            if type(self) == RevPiModIODriver \
                    or type(self) == RevPiNetIODriver:
                _searchtype = "VIRTUAL"
            else:
                _searchtype = None

            # Angegebene Devices suchen
            for dev in jconfigrsc["Devices"]:
                if _searchtype is None or dev["type"] == _searchtype:
                    if dev["name"] in self._lst_devselect:
                        lst_found.append(dev)
                    elif dev["position"].isdigit() \
                            and int(dev["position"]) in self._lst_devselect:
                        lst_found.append(dev)

        # Devices aus JSON oder Filter übernehmen
        lst_devices = jconfigrsc["Devices"] if len(self._lst_devselect) == 0 \
            else lst_found

        # Device und IO Klassen anlegen
        self.device = devicemodule.DeviceList()
        self.io = IOList()

        # Devices initialisieren
        err_names = []
        for device in sorted(lst_devices, key=lambda x: x["position"]):

            # VDev alter piCtory Versionen auf Kunbus-Standard ändern
            if device["position"] == "adap.":
                device["position"] = 64
                while device["position"] in self.device:
                    device["position"] += 1

            if device["type"] == "BASE":
                # Core
                dev_new = devicemodule.Core(
                    self, device, simulator=self._simulator
                )
                self.core = dev_new
            elif device["type"] == "LEFT_RIGHT":
                # IOs
                dev_new = devicemodule.Device(
                    self, device, simulator=self._simulator
                )
            elif device["type"] == "VIRTUAL":
                # Virtuals
                dev_new = devicemodule.Virtual(
                    self, device, simulator=self._simulator
                )
            elif device["type"] == "EDGE":
                # Gateways
                dev_new = devicemodule.Gateway(
                    self, device, simulator=self._simulator
                )
            else:
                # Device-Type nicht gefunden
                warnings.warn(
                    "device type '{}' unknown".format(device["type"]),
                    Warning
                )
                dev_new = None

            if dev_new is not None:
                # Offset prüfen, muss mit Länge übereinstimmen
                if self._length < dev_new._offset:
                    self._length = dev_new._offset

                self._length += dev_new._length

                # Auf doppelte Namen prüfen, da piCtory dies zulässt
                if hasattr(self.device, dev_new._name):
                    err_names.append(dev_new._name)

                # DeviceList für direkten Zugriff aufbauen
                setattr(self.device, dev_new._name, dev_new)

        # Namenszugriff zerstören, wenn doppelte Namen vorhanden sind
        for errdev in err_names:
            self.device.__delattr__(errdev, False)
            warnings.warn(
                "equal device name in pictory configuration. can not "
                "build device to access by name. you can access all devices "
                "by position number .device[nn] only!",
                Warning
            )

        # ImgWriter erstellen
        self._imgwriter = helpermodule.ProcimgWriter(self)

        # Aktuellen Outputstatus von procimg einlesen
        if self._syncoutputs:
            self.syncoutputs()

        # Optional ins autorefresh aufnehmen
        if self._autorefresh:
            self.autorefresh_all()

        # Summary Klasse instantiieren
        self.summary = summarymodule.Summary(jconfigrsc["Summary"])

    def _create_myfh(self):
        """Erstellt FileObject mit Pfad zum procimg.
        return FileObject"""
        self._buffedwrite = False
        return open(self._procimg, "r+b", 0)

    def _get_configrsc(self):
        """Getter function.
        @return Pfad der verwendeten piCtory Konfiguration"""
        return self._configrsc

    def _get_cycletime(self):
        """Gibt Aktualisierungsrate in ms der Prozessabbildsynchronisierung aus.
        @return Millisekunden"""
        return self._imgwriter.refresh

    def _get_ioerrors(self):
        """Getter function.
        @return Aktuelle Anzahl gezaehlter Fehler"""
        if self._looprunning:
            return self._imgwriter._ioerror
        else:
            return self._ioerror

    def _get_length(self):
        """Getter function.
        @return Laenge in Bytes der Devices"""
        return self._length

    def _get_maxioerrors(self):
        """Getter function.
        @return Anzahl erlaubte Fehler"""
        return self._maxioerrors

    def _get_monitoring(self):
        """Getter function.
        @return True, wenn als Monitoring gestartet"""
        return self._monitoring

    def _get_procimg(self):
        """Getter function.
        @return Pfad des verwendeten Prozessabbilds"""
        return self._procimg

    def _get_simulator(self):
        """Getter function.
        @return True, wenn als Simulator gestartet"""
        return self._simulator

    def _gotioerror(self, action):
        """IOError Verwaltung fuer Prozessabbildzugriff."""
        self._ioerror += 1
        if self._maxioerrors != 0 and self._ioerror >= self._maxioerrors:
            raise RuntimeError(
                "reach max io error count {} on process image".format(
                    self._maxioerrors
                )
            )
        warnings.warn(
            "got io error during {} and count {} errors now".format(
                action, self._ioerror
            ),
            RuntimeWarning
        )

    def _set_cycletime(self, milliseconds):
        """Setzt Aktualisierungsrate der Prozessabbild-Synchronisierung.
        @param milliseconds <class 'int'> in Millisekunden"""
        if self._looprunning:
            raise RuntimeError(
                "can not change cycletime when cycleloop or mainloop are "
                "running"
            )
        else:
            self._imgwriter.refresh = milliseconds

    def _set_maxioerrors(self, value):
        """Setzt Anzahl der maximal erlaubten Fehler bei Prozessabbildzugriff.
        @param value Anzahl erlaubte Fehler"""
        if type(value) == int and value >= 0:
            self._maxioerrors = value
            self._imgwriter.maxioerrors = value
        else:
            raise ValueError("value must be 0 or a positive integer")

    def autorefresh_all(self):
        """Setzt alle Devices in autorefresh Funktion."""
        for dev in self.device:
            dev.autorefresh()

    def cleanup(self):
        """Beendet autorefresh und alle Threads."""
        self.exit(full=True)
        self._myfh.close()
        self.app = None
        self.core = None
        self.device = None
        self.io = None
        self.summary = None

    def cycleloop(self, func, cycletime=None):
        """Startet den Cycleloop.

        Der aktuelle Programmthread wird hier bis Aufruf von
        .exit() "gefangen". Er fuehrt nach jeder Aktualisierung
        des Prozessabbilds die uebergebene Funktion "func" aus und arbeitet sie
        ab. Waehrend der Ausfuehrung der Funktion wird das Prozessabbild nicht
        weiter aktualisiert. Die Inputs behalten bis zum Ende den aktuellen
        Wert. Gesetzte Outputs werden nach Ende des Funktionsdurchlaufs in das
        Prozessabbild geschrieben.

        Verlassen wird der Cycleloop, wenn die aufgerufene Funktion einen
        Rueckgabewert nicht gleich None liefert, oder durch Aufruf von
        revpimodio.exit().

        HINWEIS: Die Aktualisierungszeit und die Laufzeit der Funktion duerfen
        die eingestellte autorefresh Zeit, bzw. uebergebene cycletime nicht
        ueberschreiten!

        Ueber das Attribut cycletime kann die Aktualisierungsrate fuer das
        Prozessabbild gesetzt werden.

        @param func Funktion, die ausgefuehrt werden soll
        @param cycletime Zykluszeit in Millisekunden, bei Nichtangabe wird
               aktuelle .cycletime Zeit verwendet - Standardwert 50 ms
        @return None

        """
        # Prüfen ob ein Loop bereits läuft
        if self._looprunning:
            raise RuntimeError(
                "can not start multiple loops mainloop/cycleloop"
            )

        # Prüfen ob Devices in autorefresh sind
        if len(self._lst_refresh) == 0:
            raise RuntimeError("no device with autorefresh activated")

        # Prüfen ob Funktion callable ist
        if not callable(func):
            raise RuntimeError(
                "registered function '{}' ist not callable".format(func)
            )

        # Zykluszeit übernehmen
        if not (cycletime is None or cycletime == self._imgwriter.refresh):
            self._imgwriter.refresh = cycletime

            # Zeitänderung in _imgwriter neuladen
            self._imgwriter.newdata.clear()

        # Cycleloop starten
        self._exit.clear()
        self._looprunning = True
        cycleinfo = helpermodule.Cycletools(self._imgwriter.refresh)
        ec = None
        try:
            while ec is None and not self._exit.is_set():
                # Auf neue Daten warten und nur ausführen wenn set()
                if not self._imgwriter.newdata.wait(2.5):
                    if not self._exit.is_set() \
                            and not self._imgwriter.is_alive():
                        self.exit(full=False)
                        self._looprunning = False
                        raise RuntimeError("autorefresh thread not running")
                    continue
                self._imgwriter.newdata.clear()

                # Vor Aufruf der Funktion autorefresh sperren
                self._imgwriter.lck_refresh.acquire()

                # Funktion aufrufen und auswerten
                ec = func(cycleinfo)
                cycleinfo._docycle()

                # autorefresh freigeben
                self._imgwriter.lck_refresh.release()
        except Exception as e:
            if self._imgwriter.lck_refresh.locked():
                self._imgwriter.lck_refresh.release()
            self.exit(full=False)
            self._looprunning = False
            raise e

        # Cycleloop beenden
        self._looprunning = False

        return ec

    def exit(self, full=True):
        """Beendet mainloop() und optional autorefresh.

        Wenn sich das Programm im mainloop() befindet, wird durch Aufruf
        von exit() die Kontrolle wieder an das Hauptprogramm zurueckgegeben.

        Der Parameter full ist mit True vorbelegt und entfernt alle Devices aus
        dem autorefresh. Der Thread fuer die Prozessabbildsynchronisierung
        wird dann gestoppt und das Programm kann sauber beendet werden.

        @param full Entfernt auch alle Devices aus autorefresh"""
        self._exit.set()
        self._waitexit.set()

        if full:
            # ProcimgWriter beenden und darauf warten
            if self._imgwriter is not None and self._imgwriter.is_alive():
                self._imgwriter.stop()
                self._imgwriter.join(self._imgwriter._refresh)

            # Mainloop beenden und darauf waretn
            if self._th_mainloop is not None and self._th_mainloop.is_alive():
                self._th_mainloop.join(1)

            # Alle Devices aus Autorefresh entfernen
            while len(self._lst_refresh) > 0:
                dev = self._lst_refresh.pop()
                dev._selfupdate = False
                if not self._monitoring:
                    self.writeprocimg(dev)

    def get_jconfigrsc(self):
        """Laedt die piCtory Konfiguration und erstellt ein <class 'dict'>.
        @return <class 'dict'> der piCtory Konfiguration"""
        # piCtory Konfiguration prüfen
        if self._configrsc is not None:
            if not access(self._configrsc, F_OK | R_OK):
                raise RuntimeError(
                    "can not access pictory configuration at {}".format(
                        self._configrsc))
        else:
            # piCtory Konfiguration an bekannten Stellen prüfen
            lst_rsc = ["/etc/revpi/config.rsc", "/opt/KUNBUS/config.rsc"]
            for rscfile in lst_rsc:
                if access(rscfile, F_OK | R_OK):
                    self._configrsc = rscfile
                    break
            if self._configrsc is None:
                raise RuntimeError(
                    "can not access known pictory configurations at {} - "
                    "use 'configrsc' parameter so specify location"
                    "".format(", ".join(lst_rsc))
                )

        with open(self._configrsc, "r") as fhconfigrsc:
            try:
                jdata = jload(fhconfigrsc)
            except:
                raise RuntimeError(
                    "can not read piCtory configuration - check your hardware "
                    "configuration http://revpi_ip/"
                )
            return jdata

    def handlesignalend(self, cleanupfunc=None):
        """Signalhandler fuer Programmende verwalten.

        Wird diese Funktion aufgerufen, uebernimmt RevPiModIO die SignalHandler
        fuer SIGINT und SIGTERM. Diese werden Empfangen, wenn das
        Betriebssystem oder der Benutzer das Steuerungsprogramm sauber beenden
        will.

        Die optionale Funktion "cleanupfunc" wird als letztes nach dem letzten
        Einlesen der Inputs ausgefuehrt. Dort gesetzte Outputs werden nach
        Ablauf der Funktion ein letztes Mal geschrieben.
        Gedacht ist dies fuer Aufraeumarbeiten, wie z.B. das abschalten der
        LEDs am RevPi-Core.

        Nach einmaligem Empfangen eines der Signale und dem Beenden der
        RevPiModIO Thrads / Funktionen werden die SignalHandler wieder
        freigegeben.

        @param cleanupfunc Funktion wird nach dem letzten Lesen der Inputs
        ausgefuehrt, gefolgt vom letzten Schreiben der Outputs

        """
        # Prüfen ob Funktion callable ist
        if not (cleanupfunc is None or callable(cleanupfunc)):
            raise RuntimeError(
                "registered function '{}' ist not callable".format(cleanupfunc)
            )
        self.__cleanupfunc = cleanupfunc
        signal(SIGINT, self.__evt_exit)
        signal(SIGTERM, self.__evt_exit)

    def mainloop(self, blocking=True):
        """Startet den Mainloop mit Eventueberwachung.

        Der aktuelle Programmthread wird hier bis Aufruf von
        RevPiDevicelist.exit() "gefangen" (es sei denn blocking=False). Er
        durchlaeuft die Eventueberwachung und prueft Aenderungen der, mit
        einem Event registrierten, IOs. Wird eine Veraenderung erkannt,
        fuert das Programm die dazugehoerigen Funktionen der Reihe nach aus.

        Wenn der Parameter "blocking" mit False angegeben wird, aktiviert
        dies die Eventueberwachung und blockiert das Programm NICHT an der
        Stelle des Aufrufs. Eignet sich gut fuer die GUI Programmierung, wenn
        Events vom RevPi benoetigt werden, aber das Programm weiter ausgefuehrt
        werden soll.

        @param blocking Wenn False, blockiert das Programm NICHT
        @return None

        """
        # Prüfen ob ein Loop bereits läuft
        if self._looprunning:
            raise RuntimeError(
                "can not start multiple loops mainloop/cycleloop"
            )

        # Prüfen ob Devices in autorefresh sind
        if len(self._lst_refresh) == 0:
            raise RuntimeError("no device with autorefresh activated")

        # Thread erstellen, wenn nicht blockieren soll
        if not blocking:
            self._th_mainloop = Thread(
                target=self.mainloop, kwargs={"blocking": True}
            )
            self._th_mainloop.start()
            return

        # Event säubern vor Eintritt in Mainloop
        self._exit.clear()
        self._looprunning = True

        # Beim Eintritt in mainloop Bytecopy erstellen
        for dev in self._lst_refresh:
            dev._filelock.acquire()
            dev._ba_datacp = dev._ba_devdata[:]
            dev._filelock.release()

        # ImgWriter mit Eventüberwachung aktivieren
        self._imgwriter._collect_events(True)
        e = None

        while not self._exit.is_set():
            try:
                tup_fire = self._imgwriter._eventq.get(timeout=1)
                # Direct callen da Prüfung in io.IOBase.reg_event ist
                tup_fire[0].func(tup_fire[1], tup_fire[2])
            except Empty:
                if not self._exit.is_set() and not self._imgwriter.is_alive():
                    self.exit(full=False)
                    e = RuntimeError("autorefresh thread not running")
            except Exception as ex:
                self.exit(full=False)
                e = ex

        # Mainloop verlassen
        self._imgwriter._collect_events(False)
        self._looprunning = False
        self._th_mainloop = None

        # Fehler prüfen
        if e is not None:
            raise e

    def readprocimg(self, device=None):
        """Einlesen aller Inputs aller/eines Devices vom Prozessabbild.

        Devices mit aktiverem autorefresh werden ausgenommen!

        @param device nur auf einzelnes Device anwenden
        @return True, wenn Arbeiten an allen Devices erfolgreich waren

        """
        if device is None:
            mylist = self.device
        else:
            dev = device if issubclass(type(device), devicemodule.Device) \
                else self.device.__getitem__(device)

            if dev._selfupdate:
                raise RuntimeError(
                    "can not read process image, while device '{}|{}'"
                    "is in autorefresh mode".format(dev._position, dev._name)
                )
            mylist = [dev]

        # Daten komplett einlesen
        try:
            self._myfh.seek(0)
            bytesbuff = self._myfh.read(self._length)
        except IOError:
            self._gotioerror("read")
            return False

        for dev in mylist:
            if not dev._selfupdate:

                # FileHandler sperren
                dev._filelock.acquire()

                if self._monitoring:
                    # Alles vom Bus einlesen
                    dev._ba_devdata[:] = bytesbuff[dev._slc_devoff]
                else:
                    # Inputs vom Bus einlesen
                    dev._ba_devdata[dev._slc_inp] = bytesbuff[dev._slc_inpoff]

                    # Mems vom Bus lesen
                    dev._ba_devdata[dev._slc_mem] = bytesbuff[dev._slc_memoff]

                dev._filelock.release()

        return True

    def resetioerrors(self):
        """Setzt aktuellen IOError-Zaehler auf 0 zurueck."""
        self._ioerror = 0
        self._imgwriter._ioerror = 0

    def setdefaultvalues(self, device=None):
        """Alle Outputbuffer werden auf die piCtory default Werte gesetzt.
        @param device nur auf einzelnes Device anwenden"""
        if self._monitoring:
            raise RuntimeError(
                "can not set default values, while system is in monitoring "
                "mode"
            )

        if device is None:
            mylist = self.device
        else:
            dev = device if issubclass(type(device), devicemodule.Device) \
                else self.device.__getitem__(device)
            mylist = [dev]

        for dev in mylist:
            for io in dev.get_outputs():
                io.set_value(io._defaultvalue)

    def syncoutputs(self, device=None):
        """Lesen aller aktuell gesetzten Outputs im Prozessabbild.

        Devices mit aktiverem autorefresh werden ausgenommen!

        @param device nur auf einzelnes Device anwenden
        @return True, wenn Arbeiten an allen Devices erfolgreich waren

        """
        if device is None:
            mylist = self.device
        else:
            dev = device if issubclass(type(device), devicemodule.Device) \
                else self.device.__getitem__(device)

            if dev._selfupdate:
                raise RuntimeError(
                    "can not sync process image, while device '{}|{}'"
                    "is in autorefresh mode".format(dev._position, dev._name)
                )
            mylist = [dev]

        try:
            self._myfh.seek(0)
            bytesbuff = self._myfh.read(self._length)
        except IOError:
            self._gotioerror("read")
            return False

        for dev in mylist:
            if not dev._selfupdate:
                dev._filelock.acquire()
                dev._ba_devdata[dev._slc_out] = bytesbuff[dev._slc_outoff]
                dev._filelock.release()

        return True

    def writeprocimg(self, device=None):
        """Schreiben aller Outputs aller Devices ins Prozessabbild.

        Devices mit aktiverem autorefresh werden ausgenommen!

        @param device nur auf einzelnes Device anwenden
        @return True, wenn Arbeiten an allen Devices erfolgreich waren

        """
        if self._monitoring:
            raise RuntimeError(
                "can not write process image, while system is in monitoring "
                "mode"
            )

        if device is None:
            mylist = self.device
        else:
            dev = device if issubclass(type(device), devicemodule.Device) \
                else self.device.__getitem__(device)

            if dev._selfupdate:
                raise RuntimeError(
                    "can not write process image, while device '{}|{}'"
                    "is in autorefresh mode".format(dev._position, dev._name)
                )
            mylist = [dev]

        workokay = True
        for dev in mylist:
            if not dev._selfupdate:
                dev._filelock.acquire()

                # Outpus auf Bus schreiben
                try:
                    self._myfh.seek(dev._slc_outoff.start)
                    self._myfh.write(dev._ba_devdata[dev._slc_out])
                except IOError:
                    workokay = False

                dev._filelock.release()

        if self._buffedwrite:
            try:
                self._myfh.flush()
            except IOError:
                workokay = False

        if not workokay:
            self._gotioerror("write")

        return workokay

    configrsc = property(_get_configrsc)
    cycletime = property(_get_cycletime, _set_cycletime)
    ioerrors = property(_get_ioerrors)
    length = property(_get_length)
    maxioerrors = property(_get_maxioerrors, _set_maxioerrors)
    monitoring = property(_get_monitoring)
    procimg = property(_get_procimg)
    simulator = property(_get_simulator)


class RevPiModIOSelected(RevPiModIO):

    """Klasse fuer die Verwaltung einzelner Devices aus piCtory.

    Diese Klasse uebernimmt nur angegebene Devices der piCtory Konfiguration
    und bilded sie inkl. IOs ab. Sie uebernimmt die exklusive Verwaltung des
    Adressbereichs im Prozessabbild an dem sich die angegebenen Devices
    befinden und stellt sicher, dass die Daten synchron sind.

    """

    def __init__(
            self, deviceselection, autorefresh=False, monitoring=False,
            syncoutputs=True, procimg=None, configrsc=None, simulator=False):
        """Instantiiert nur fuer angegebene Devices die Grundfunktionen.

        Der Parameter deviceselection kann eine einzelne
        Device Position / einzelner Device Name sein oder eine Liste mit
        mehreren Positionen / Namen

        @param deviceselection Positionsnummer oder Devicename
        @see #RevPiModIO.__init__ RevPiModIO.__init__(...)

        """
        super().__init__(
            autorefresh, monitoring, syncoutputs, procimg, configrsc, simulator
        )

        # Device liste erstellen
        if type(deviceselection) == list:
            for dev in deviceselection:
                self._lst_devselect.append(dev)
        else:
            self._lst_devselect.append(deviceselection)

        for vdev in self._lst_devselect:
            if type(vdev) != int and type(vdev) != str:
                raise ValueError(
                    "need device position as <class 'int'> or device name as "
                    "<class 'str'>"
                )

        self._configure(self.get_jconfigrsc())

        if len(self.device) == 0:
            if type(self) == RevPiModIODriver:
                raise RuntimeError(
                    "could not find any given VIRTUAL devices in config"
                )
            else:
                raise RuntimeError(
                    "could not find any given devices in config"
                )
        elif len(self.device) != len(self._lst_devselect):
            if type(self) == RevPiModIODriver:
                raise RuntimeError(
                    "could not find all given VIRTUAL devices in config"
                )
            else:
                raise RuntimeError(
                    "could not find all given devices in config"
                )


class RevPiModIODriver(RevPiModIOSelected):

    """Klasse um eigene Treiber fuer die virtuellen Devices zu erstellen.

    Mit dieser Klasse werden nur angegebene Virtuelle Devices mit RevPiModIO
    verwaltet. Bei Instantiierung werden automatisch die Inputs und Outputs
    verdreht, um das Schreiben der Inputs zu ermoeglichen. Die Daten koennen
    dann ueber logiCAD an den Devices abgerufen werden.

    """

    def __init__(
            self, virtdev, autorefresh=False, monitoring=False,
            syncoutputs=True, procimg=None, configrsc=None):
        """Instantiiert die Grundfunktionen.

        Parameter 'monitoring' und 'simulator' stehen hier nicht zur
        Verfuegung, da diese automatisch gesetzt werden.

        @param virtdev Virtuelles Device oder mehrere als <class 'list'>
        @see #RevPiModIO.__init__ RevPiModIO.__init__(...)

        """
        # Parent mit monitoring=False und simulator=True laden
        super().__init__(
            virtdev, autorefresh, False, syncoutputs, procimg, configrsc, True
        )


# Nachträglicher Import
from .netio import RevPiNetIODriver
