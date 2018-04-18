
import logging, os, sys, subprocess
from glob import glob
from bl.file import File
import re

log = logging.getLogger(__name__)

class PDF(File):

    def gswrite(self, fn=None, device='jpeg', res=600, alpha=4, quality=90, gs=None):
        "use ghostscript to create output file(s) from the PDF"
        gs = (gs or self.gs or os.environ.get('gs') or 'gs')
        # count the number of pages
        if fn is None: 
            fn = os.path.splitext(self.fn)[0] + DEVICE_EXTENSIONS[device]
        fn = File(fn=fn).fn     # normalize path
        log.debug("PDF.gswrite():\n\tself.fn = %s\n\tout fn = %s" % (self.fn, fn))
        if os.path.splitext(self.fn)[-1].lower()=='.pdf':
            cmd = [gs, '-q', '-dNODISPLAY', '-c', 
                    "(%s) (r) file runpdfbegin pdfpagecount = quit" % self.fn]
            log.debug(cmd)
            pages = int(subprocess.check_output(cmd).decode('utf-8').strip())
            log.debug("%d page(s)" % pages)
        else:
            pages = 1
        if pages > 1:
            # add a counter to the filename, which tells gs to create a file for every page in the input
            fb, ext = os.path.splitext(fn)
            n = len(re.split('.', str(pages))) - 1
            counter = "-%%0%dd" % n
            fn = fb + counter + ext

            # remove any existing output filenames that match the pattern
            for existingfn in glob(fb+'*'+ext):
                log.debug("REMOVING %s" % existingfn)
                os.remove(existingfn)

        callargs = [gs, '-q', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-dUseCropBox',
                    '-sDEVICE=%s' % device, '-r%d' % res]
        if device=='jpeg': 
            callargs += ['-dJPEGQ=%d' % quality]
        if 'png' in device or 'jpeg' in device or 'tiff' in device: 
            callargs += [
                '-dTextAlphaBits=%d' % alpha,
                '-dGraphicsAlphaBits=%d' % alpha]
        callargs += ['-sOutputFile=%s' % fn, self.fn]
        try:
            log.debug(callargs)
            subprocess.check_output(callargs)
        except subprocess.CalledProcessError as e:
            log.error(callargs)
            log.error(str(e.output, 'utf-8'))
        fns = sorted(glob(re.sub('%\d+d','*', fn)))
        log.debug('\n\t'+'\n\t'.join(fns))
        return fns

DEVICE_EXTENSIONS = {
    'png16m':'.png', 
    'png256':'.png', 
    'png16':'.png', 
    'pngmono':'.png', 
    'pngmonod':'.png', 
    'pngalpha':'.png',
    'pnggray':'.png',
    'jpeg':'.jpg', 
    'jpeggray':'.jpg',
    'tiff48nc':'.tiff',     # rgb, 16bit per channel
    'tiff24nc':'.tiff',     # rgb, 8bit per channel
    'tiff12nc':'.tiff',     # rgb, 4bit per channel
    'tiffgray':'.tiff',     # grayscale, 8bit per channel
    'tiff64nc':'.tiff',     # cmyk, 16bit
    'tiff32nc':'.tiff',     # cmyk, 8bit
    'tiffsep':'.tiff',      # cmyk separation into 4 files + 1 composite
    'tiffsep1':'.tiff', 
    'tiffscaled':'.tiff', 
    'tiffscaled4':'.tiff', 
    'tiffscaled8':'.tiff', 
    'tiffscaled24':'.tiff', 
    'tiffscaled32':'.tiff', 
    'tiffcrle':'.tiff', 
    'tiffg3':'.tiff', 
    'tiffg32d':'.tiff', 
    'tiffg4':'.tiff', 
    'tifflzw':'.tiff', 
    'tiffpack':'.tiff', 
    'txtwrite':'.txt',
    'psdrgb':'.psd',
    'psdcmyk':'.psd', 
    'pdfwrite':'.pdf',
}
EXTENSION_DEVICES = {
    key:[val for val in DEVICE_EXTENSIONS.keys() if DEVICE_EXTENSIONS[val]==key]
    for key in
    list(set(DEVICE_EXTENSIONS.values()))
}
EXTENSION_DEVICES_PRIMARY = {
    key:vals[0] for key,vals in EXTENSION_DEVICES.items()
}
