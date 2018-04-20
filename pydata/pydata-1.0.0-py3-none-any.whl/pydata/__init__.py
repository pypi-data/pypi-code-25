#!/usr/bin/env python
# coding: utf-8

import sys
import traceback
from pydata.list import PyData
from pydata.command import parsers


def main():
    argv = sys.argv
    argv = argv[1:]

    if len(argv) == 0:
        body = u'''
                    (&..
                    (VVVW+,
                    (VyVVVVVk-.
                    (VVyVVyVVVVVn..
                    (VVVyVVVVVVVVVVW&.
                    (VyVVVVyVyVVVVVVVV$
                    (VVVVVVVVVVVVVVVVV$
                    (VVVyVVVyVVyVyVyVV$
                    (VVVVyVVVVVVVVVVVV$
                    (VyVVVyVVyVVyVVyVV$ 
                     ?TWVVVyVVyVVyVVVV$
                ..dfn..  74VVVVVVVVVVV$                                                                                                                                                              
            ..ufVVVfVVfW&.  _7WVVVyVVV$
         .JffVVVVVVVVVVVVVVk+,  ?TWVVV$
     .(XVVVVVVVVVVVVVVVVVyVVVVVk-.  ?4$
 ..dVVVVVVVVVVVyVyVyVVyVVVyVyVVVVVVn..        ...............                                        
.  74VVyVVVyVVyVVVVVyVVyVVVVVVVVVVY=` .       HHMMMMMMMMMMMMHHMm..                                    (VVVVVVVVVVVXkw+..                                             ..
HNa,  _7WVVVyVVVVyVVVVVVyVVyVVV"` ..&M@       @@}             ?TMHh,                                  (VS`````````~??"TWfW&,                                         ff`
@HH@HNJ,  ?TWVVVyVVyVyVVVVV7!  .(MMMMM@       H@}                ?H@,                                 (VS                ?Ufk,                                       fV`
@H@H@H@H@m..  74VVVVVVXY^  ..MMMMMMNNM@       H@}                 (HN.                                (VS                  .4Vh.                                     VV`
H@H@H@H@HH@HMa,. _7Y=` ..gMMNMMNMNMMNM@       H@}                  @H)   ,HH,               `.HH'     (VS                    ?fV,            ...(JJJ...          ....VV-........        ...(JJJ-..
@H@H@H@H@@HH@H@HN&. .JMMNMMNMNMMNMNMMN@       H@}                 .H@:    /HM,              .HH%      (VS                     jVW.        dffVY"""""TWff&.       ,TTTfVYTTTTTTT!      (WVWY7""""T4ffn,
H@H@H@H@H@H@H@H@H@) JMMNMNMMNMMNMMMNMM@       H@}                 J@@      ?HN,             dHF       (VS                      WVr        _`           ?Wf;          VV`              .!           (4fn
@H@H@H@H@H@H@H@H@H) JMNMMMNMMNMMNMMNMM@       H@}               .HH@        ?HN.          `(@F        (VS                      (Vk                      .Wf-         VV`                             zf[
H@H@H@H@H@H@H@H@H@) JMNMNMMNMMNMMNMMNN@       HH)         ....gH@Y^          vHN.         .H#         (VS                      ,VW                       (Vr         VV`                             .Vk
@H@H@H@H@H@H@H@H@H) JMMNMMNMNMMNMMNMMM@       H@H@H@@H@@H@HMMY"^              O@h        .HM!         (VS                      (Vf         ..JdXVVVVWkw+.,V$         Vy`                ..&wXVVVWkA&-.VW
MH@H@H@H@H@H@H@H@H) JNMMMNMMMNMMNMMNMN@       H@}                              4Hb      .HM^          (VS                     .XV\       .XfY"!`     ~?7"4V$         VV`             .dfV"!`     `??"TyW
 ."WH@H@H@H@H@H@H@) JMNMNMMNMMNMNMM#"`        H@}                               4@L     dHt           (VS                     JVf       Jff`             ,V$         VV`            .fX'             .VW
Na,  (TMH@H@H@H@H@) JMMNMMNMNMMM"!            H@}                                4HL   .HF            (VS                   .dVf       .VV`              ,V$         yV`            fV\              .VW
@H@HHJ,  ?YM@H@H@H) JMNMMNMM9^                H@}                                 WH| .H@             (VS                 ..VW=        .VV.             .VV$         VV.            WV)              gVW
H@H@H@HHm,.  7W@H@) JMNMY"                    H@}                                  WHJHM`             (VS              ..dVX=           TVk,          ..V4V$         4fl            (VV,           .XUVW
@H@H@H@HH@HMa,  _"\ J"!                       H@}                                   H@M^              (VkJJJJJJJJJ+&wffWY"`              ?WVW&......+XW=`,V$         .4fk+....+.     .4VVn-.....JdVY'.VW
H@H@H@@H@HHHH@HN+,                                                                 .dH%               ("""""""""""77?`                      ?"TUUUY77`   ,"^            7TTTY"=         ?7TTUUYY"!   .""
@H@H@HH@@H@@H@H@HH)                                                               .dHt
H@H@H@H@H@H@@H@H@@)                                                       .J.....+H#^
@H@H@H@H@H@HH@H@HH)                                                       7YHMMMHY^
H@H@H@H@H@H@H@H@@H)
@H@H@H@H@H@H@H@H@@)
."WH@H@H@H@H@H@HHH)
    ?TMH@@H@H@H@@H)
        ?YMH@H@H@@)
           .7WH@HH)
               _"H)

        '''
        print(body)

    args = parsers.parse_args(argv)

    try:
        if args.l:
            PyData.scraping()

    except Exception as e:
        t, v, tb = sys.exc_info()
        error = traceback.format_exception(t, v, tb)
        print(error[0])
        print(error[1])
        print(error[2])


if __name__ == "__main__":
    main()
