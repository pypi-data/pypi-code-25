# -*- coding: utf-8 -*-
# Author: Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
# Copyright: This module has been placed in the public domain.
"""
This module defines the span role and div directive.

It sets up command line options and splices the various definitions
into the docutils modules.
"""

# --------------------------------------------------
# |||:sec:||| CONFIGURATION
# --------------------------------------------------

from docutils import frontend
import docutils.parsers.rst

span_settings = [
    ('Disable the "span" role and "div" directive; " '
     'replaced with a "warning system message.',
     ['--no-span'],
     {'action': 'store_false', 'default': 1, 'dest': 'span_enabled',
      'validator': frontend.validate_boolean}),
    ('Enable the "span" role and "div" directive.  Enabled by default.',
     ['--span-enabled'],
     {'action': 'store_true'}),
    ('Disable "span" role recursive parsing. '
     'Disbled by default.',
     ['--no-span-recursive'],
     {'action': 'store_false', 'default': 0, 'dest': 'span_recursive',
      'validator': frontend.validate_boolean}),
    ('Enable "span" role recursive parsing.',
     ['--span-recursive'],
     {'action': 'store_true'}),
    ]

ss = list(docutils.parsers.rst.Parser.settings_spec)
opts = list(ss[2])
opts.extend(span_settings)
ss[2] = tuple(opts)
docutils.parsers.rst.Parser.settings_spec = tuple(ss)

# --------------------------------------------------
# |||:sec:||| SETUP
# --------------------------------------------------

# install `span` and `div` nodes
import ws_docutils.span.nodes
# install `span` role
import ws_docutils.span.role
# install `div` directive
import ws_docutils.span.directive
# install writer support
import ws_docutils.span.writer

def setup (app):
    """Fix warning from sphinx extension.

    From Sphinx manual:

    version
      a string that identifies the extension version. It is
      used for extension version requirement checking (see
      needs_extensions) and informational purposes. If not given,
      "unknown version" is substituted.

    env_version
      an integer that identifies the version of env data structure if
      the extension stores any data to environment. It is used to
      detect the data structure has been changed from last build. The
      extensions have to increment the version when data structure has
      changed. If not given, Sphinx considers the extension does not
      stores any data to environment.

    parallel_read_safe
      a boolean that specifies if parallel reading of source files can
      be used when the extension is loaded. It defaults to False,
      i.e. you have to explicitly specify your extension to be
      parallel-read-safe after checking that it is.

    parallel_write_safe
      a boolean that specifies if parallel writing of output files can
      be used when the extension is loaded. Since extensions usually
      don’t negatively influence the process, this defaults to True.
    """

    return dict(
        version='0.4',
        parallel_read_safe=True,
        parallel_write_safe=True,
    )

# --------------------------------------------------
# |||:sec:||| END
# --------------------------------------------------
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# :ide: CLN: Clean file (remove excess blank lines and whitespace)
# . (let () (save-excursion (goto-char (point-min)) (set-buffer-modified-p t) (replace-regexp "\n\n\n+" "\n\n" nil) (c-beautify-buffer) (save-buffer)))

# :ide: CSCOPE ON
# . (cscope-minor-mode)

# :ide: CSCOPE OFF
# . (cscope-minor-mode (quote ( nil )))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))
#
# Local Variables:
# mode: python
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
