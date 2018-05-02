    ##############################################

    def _check_qml_initialisation(self, engine):

        print(engine)
        if self._qml_engine is None:
            self._initialise_qml(engine)
        elif self._qml_engine != engine:
            raise NotImplementedError('QML engine mismatch')
