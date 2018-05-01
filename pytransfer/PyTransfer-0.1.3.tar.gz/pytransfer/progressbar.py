from tqdm import tqdm


class AdvancedTqdm(tqdm):
    def finish(self, message):
        self.clear()
        self._lock.acquire()
        self.moveto(abs(self.pos))
        self.sp(message)
        self.fp.write('\r')  # place cursor back at the beginning of line
        self.moveto(-abs(self.pos))
        self._lock.release()
        self.disable = True
