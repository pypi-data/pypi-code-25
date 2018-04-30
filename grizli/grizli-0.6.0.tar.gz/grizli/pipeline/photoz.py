### photo-z with EAZY

def sep_catalog(root, aper_radius=0.3, subtract_background=True):

    import sep
    phot = utils.GTable.gread('{0}_phot.fits'.format(root))
    
    files=glob.glob('{0}-f*sci.fits'.format(root))
    seg = pyfits.open('{0}-ir_seg.fits'.format(root))
    
    filters = []
    for file in files:
        sci = pyfits.open(file)
        sci[0].data = sci[0].data.byteswap().newbyteorder()
        
        wht = pyfits.open(file.replace('sci','wht'))
        wht[0].data = wht[0].data.byteswap().newbyteorder()
        err = 1/np.sqrt(wht[0].data)
        err[~np.isfinite(err)] = 0
        
        mask = (err == 0) | (seg[0].data > 0)
        
        if subtract_background:
            bkg = sep.Background(sci[0].data, mask=mask, bw=64, bh=64, fw=3, fh=3)
            bkg_data = bkg.back()
            
            #flux, flux_err, flags = sep.sum_circle(sci[0].data-bkg.back(), phot['xcentroid'], phot['ycentroid'], aper_radius/0.06, err=err, mask=(err == 0))
            
        else:
            bkg_data = 0.
            
        flux, flux_err, flags = sep.sum_circle(sci[0].data - bkg_data, phot['xcentroid'], phot['ycentroid'], aper_radius/0.06, err=err, mask=(err == 0), gain=0.)
                    
        filt = utils.get_hst_filter(sci[0].header).lower()
        print(filt)
        filters.append(filt)
        
        fr, fr_flag = sep.flux_radius(sci[0].data - bkg_data, phot['xcentroid'], phot['ycentroid'], phot['semimajor_axis_sigma']*6, 0.5, normflux=phot[filt+'_source_sum'])

        phot['{0}_flux_radius'.format(filt)] = fr        
        phot['{0}_aper_sum'.format(filt)] = flux
        phot['{0}_aper_err'.format(filt)] = flux_err
        phot['{0}_aper_flag'.format(filt)] = flags
        
    #total = phot['f160w_source_sum']/phot['f160w_aper_sum']
    
    return phot
    
def test():
    
    import eazy
    from eazy import filters
    
    from grizli import utils
    
    #root = 'j011008-022356'
    
    os.system('ln -s /usr/local/share/eazy-photoz/filters/FILTER.RES.latest* /usr/local/share/eazy-photoz/templates .')
    
    tab = utils.GTable.gread('../../{0}_footprint.fits'.format(root))

    params = {}
    params['CATALOG_FILE'] = '{0}_eazy.fits'.format(root)
    params['Z_STEP'] = 0.01
    params['MAIN_OUTPUT_FILE'] = '{0}.eazypy'.format(root)
    params['PRIOR_FILTER'] = 205

    params['MW_EBV'] = tab.meta['MW_EBV']
    params['SYS_ERR'] = 0.03   
    
    params['Z_MAX'] = 6
    params['TEMPLATES_FILE'] = 'templates/fsps_full/tweak_fsps_QSF_12_v3.param'
    
    if False:
        zpfile = '{0}_3dhst.{1}.eazypy.zphot.zeropoint'.format(field, version)
        load_products = True
    else:
        zpfile = None
        load_products = False
        
    # Translate and zeropoint files
    #phot = utils.GTable.gread('{0}_phot.fits'.format(root))
    phot = sep_catalog(root, aper_radius=aper_radius, subtract_background=subtract_backround)
    
    res = filters.FilterFile('FILTER.RES.latest')
    
    zpfile = '{0}.zphot.zeropoint'.format(root)
    fpt = open('{0}.zphot.translate'.format(root), 'w')
    fpz = open('{0}.zphot.zeropoint'.format(root), 'w')
    
    for c in phot.colnames:
        #if c.endswith('source_sum') & c.startswith('f'):
        if c.endswith('aper_sum') & c.startswith('f'):
            filt = c.split('_')[0]
            fnumber = res.search(filt, verbose=False)[-1]+1
            print(c, filt, fnumber)
            
            mask = phot[c] == 0
            phot[c][mask] = -99
            #phot[c.replace('_sum', '_sum_err')][mask] = -99
            phot[c.replace('aper_sum', 'aper_err')][mask] = -99
            
            fpt.write('{0} F{1}\n'.format(c, fnumber))
            #fpt.write('{0} E{1}\n'.format(c.replace('_sum', '_sum_err'),  fnumber))
            fpt.write('{0} E{1}\n'.format(c.replace('aper_sum', 'aper_err'),  fnumber))
            fpz.write('F{0} {1:.3f}\n'.format(fnumber, 10**(0.4*(25-phot.meta['ZP'+filt.upper()]))))
    
    fpz.close()
    fpt.close()
    
    phot['z_spec'] = phot['id']*0-1
    phot.write('{0}_eazy.fits'.format(root), overwrite=True)
    
    self = eazy.photoz.PhotoZ(param_file=None, translate_file='{0}.zphot.translate'.format(root), zeropoint_file=zpfile, params=params, load_prior=True, load_products=False)
    
    hmag = phot.meta['ZPF160W'] - 2.5*np.log10(self.cat['f160w_source_sum'])
    
    self.fit_parallel(prior=True)
    self.best_fit(prior=True)
    self.standard_output(prior=True)
    
    fit = utils.GTable.gread('{0}.eazypy.zout.fits'.format(root))
    red = (hmag > 12) & (self.zbest > 1) & (hmag < 23) & (phot['f160w_flux_radius'] > 2.5) #& (fit['mass'] > 10**10.5)

    red = (hmag > 12) & (self.zbest > 3) & (hmag < 25) & (phot['f160w_flux_radius'] > 2.5) #& (fit['mass'] > 10**10.5)

    ids = self.cat['id'][red]
    
    