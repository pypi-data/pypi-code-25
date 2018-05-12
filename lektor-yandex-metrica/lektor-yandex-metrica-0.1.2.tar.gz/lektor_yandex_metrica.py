# -*- coding: utf-8 -*-


import markupsafe
from lektor.pluginsystem import Plugin


SCRIPT = '''
<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function (d, w, c) { (w[c] = w[c] || []).push(function() {
        try {
            w.yaCounter%(id)s = new Ya.Metrika({ id:%(id)s, clickmap:true, trackLinks:true, accurateTrackBounce:true });
        } catch(e) { } });
        var n = d.getElementsByTagName("script")[0], s = d.createElement("script"), f = function () { n.parentNode.insertBefore(s, n); };
        s.type = "text/javascript"; s.async = true; s.src = "https://mc.yandex.ru/metrika/watch.js";
        if (w.opera == "[object Opera]") { d.addEventListener("DOMContentLoaded", f, false); } else { f(); }
    })(document, window, "yandex_metrika_callbacks");
</script>
<noscript>
    <div><img src="https://mc.yandex.ru/watch/%(id)s" style="position:absolute; left:-9999px;" alt="" /></div>
</noscript>
<!-- /Yandex.Metrika counter -->
'''


class YandexMetricaPlugin(Plugin):
    name = 'lektor-yandex-metrica'
    description = 'Adds support for Yandex Metrica to Lektor CMS'

    def on_setup_env(self, **extra):
        _id = self.get_config().get('id')
        if _id is None:
            raise RuntimeError('Yandex Metrica id is not configured')

        def generate_yandex_metrica():
            return markupsafe.Markup(SCRIPT) % dict(id=_id)

        self.env.jinja_env.globals.update(
            generate_yandex_metrica=generate_yandex_metrica
        )
