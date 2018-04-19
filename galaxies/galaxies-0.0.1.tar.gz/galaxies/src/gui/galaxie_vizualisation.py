import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk

from galaxies.src.gui.gui_tools import *


WINDOW_TITLE = "Galaxie Vizualisation"


class WindowsGalaxieVizualisation:
    def __init__(self):
        self.list_filter = []
        self.list_button = []
        self.path = None
        self.window = Gtk.Window(title=WINDOW_TITLE)
        self.window.maximize()

        # self.window.set_position(Gtk.WIN_POS_CENTER)

        # self.grid = Gtk.Grid()

        self.menubar = Gtk.MenuBar()

        self.menu1 = Gtk.Menu()
        self.menu1_file = Gtk.MenuItem("Fichier")
        self.menu1_file.set_submenu(self.menu1)

        self.menu2 = Gtk.Menu()
        self.menu2_filtre = Gtk.MenuItem("Filtre")
        self.menu2_filtre.set_submenu(self.menu2)

        self.menu3 = Gtk.Menu()
        self.menu3_aide = Gtk.MenuItem("Aide")
        self.menu3_aide.set_submenu(self.menu2)

        self.charger_reutilisation = Gtk.MenuItem("Charger Réutilisation")
        self.charger_reutilisation.connect('activate', self.charger_reu)
        self.menu1.append(self.charger_reutilisation)
        self.charger_graphe = Gtk.MenuItem("Charger Graphe")
        self.menu1.append(self.charger_graphe)
        self.menu1.append(Gtk.SeparatorMenuItem())
        self.save_graphe = Gtk.MenuItem("Sauvegarder Graphe")
        self.menu1.append(self.save_graphe)
        self.menu1.append(Gtk.SeparatorMenuItem())
        self.exit = Gtk.MenuItem("Exit")
        self.exit.connect('activate', Gtk.main_quit)
        self.menu1.append(self.exit)

        self.filtre_auteur = Gtk.MenuItem("Filtrer Auteur")
        self.filtre_auteur.connect('activate',
                                   lambda x=0, y=0: self.filtre(x, y))
        self.menu2.append(self.filtre_auteur)
        self.filtre_annee = Gtk.MenuItem("Filtrer Année")
        self.filtre_annee.connect('activate',
                                  lambda x=0, y=1: self.filtre(x, y))
        self.menu2.append(self.filtre_annee)

        self.menubar.append(self.menu1_file)
        self.menubar.append(self.menu2_filtre)
        self.menubar.append(self.menu3_aide)

        self.vbox = Gtk.VBox(False, 2)
        self.vbox.pack_start(self.menubar, False, False, 0)
        self.window.add(self.vbox)

        self.hbox = Gtk.HBox(False, 0)

        self.sw = Gtk.ScrolledWindow()
        self.sw2 = Gtk.ScrolledWindow()

        self.vbox2 = Gtk.VBox(False, 2)

        # self.but = Gtk.Button(label="Filtre 1\nFiltre Auteur: Shakespear")
        # self.but2 = Gtk.Button(label="Filtre 2\nFiltre Auteur: Flaubert")
        #		self.but3 = Gtk.Button(label="Filtre 3\nFiltre Auteur: Maupassant")

        #	self.but4 = Gtk.Button(label="Filtre 3\nFiltre Auteur: Shakespear")
        #	self.but5 = Gtk.Button(label="Filtre 4\nFiltre Auteur: Flaubert")
        #	self.but6 = Gtk.Button(label="Filtre 5\nFiltre Auteur: Maupassant")

        #	self.but7 = Gtk.Button(label="Filtre 6\nFiltre Auteur: Shakespear#")
        #	self.but8 = Gtk.Button(label="Filtre 7\nFiltre Auteur: Flaubert")
        #	self.but9 = Gtk.Button(label="Filtre 8\nFiltre Auteur: Maupassant")

        # self.label = Gtk.Label(label="BlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablabl\nablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablabla\nBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablabla")

        self.g = Graph()

        position = sfdp_layout(self.g)
        self.l = GraphWidget(self.g, pos=position, vertex_font_size=15)

        self.l.set_size_request(self.window.get_screen().get_width() - 200,
                                self.window.get_screen().get_height() - 400)
        # self.vbox2.pack_start(self.but,  False, True, 5)
        # self.vbox2.pack_start(self.but2, False, True, 5)
        # self.vbox2.pack_start(self.but3, False, True, 5)

        # self.vbox2.pack_start(self.but4, False, True, 5)
        # self.vbox2.pack_start(self.but5, False, True, 5)
        # self.vbox2.pack_start(self.but6, False, True, 5)

        # self.vbox2.pack_start(self.but7, False, True, 5)
        # self.vbox2.pack_start(self.but8, False, True, 5)
        # self.vbox2.pack_start(self.but9, False, True, 5)

        self.sw.add_with_viewport(self.vbox2)
        self.hbox.pack_start(self.sw, True, True, 0)
        self.hbox.pack_start(self.l, False, False, 0)

        color = Gdk.color_parse('#d3d3d3')
        color2 = Gdk.color_parse('#595959')
        self.sw.modify_bg(Gtk.StateType.NORMAL, color)
        self.sw2.modify_bg(Gtk.StateType.NORMAL, color)
        # self.sw2.add_with_viewport(self.label)

        self.vbox.add(self.hbox)
        self.vbox.add(self.sw2)

        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()

        Gtk.main()

    def charger_reu(self, event):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # self.add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.path = dialog.get_filename()
            maxi, rows = get_father_son(self.path)
            self.redraw_graphe(maxi[0] + 1, rows)
        dialog.destroy()

    def redraw_graphe(self, number_nodes, list_edges):
        tab = [self.g.add_vertex() for i in range(number_nodes)]
        tab2 = [self.g.add_edge(tab[edge[0]], tab[edge[1]]) for edge in
                list_edges]
        self.l.destroy()
        position = sfdp_layout(self.g)
        self.l = GraphWidget(self.g, pos=position, vertex_font_size=15)
        self.l.set_size_request(self.window.get_screen().get_width() - 200,
                                self.window.get_screen().get_height() - 400)
        self.hbox.pack_start(self.l, False, False, 0)
        self.window.show_all()

    def filtre(self, event, choix):
        if self.path is not None:
            author, date = get_authors_date(self.path)
            dialog = Gtk.Dialog("Filtre", self.window, 0, (
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK,
            Gtk.ResponseType.OK))
            v = dialog.get_content_area()

            if choix == 0:
                type_filter = "auteur:"
                liste = Gtk.ListStore(str)
                for i in author:
                    liste.append([i[0]])
            else:
                type_filter = "année:"
                liste = Gtk.ListStore(int)
                for i in date:
                    liste.append([i[0]])

            cb = Gtk.ComboBox().new_with_model(liste)
            rt = Gtk.CellRendererText()
            cb.pack_start(rt, True)
            cb.add_attribute(rt, "text", 0)

            check_b = Gtk.CheckButton("Inverser")
            v.pack_start(cb, False, False, 0)
            v.pack_start(check_b, False, False, 0)

            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                i = cb.get_active_iter()
                if i is not None:
                    if check_b.get_active():
                        inv = "inversé "
                    else:
                        inv = " "
                    fil = cb.get_model()[i][0]
                    self.list_filter.append(Gtk.VBox(False, 2))
                    self.list_filter[-1].set_border_width(5)
                    self.list_filter[-1].override_background_color(
                        Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255))
                    self.list_filter[-1].pack_start(
                        Gtk.Label("Filtre " + inv + type_filter), False, False,
                        0)
                    self.list_filter[-1].pack_start(Gtk.Label(fil), False,
                                                    False, 0)
                    self.list_button.append(
                        Gtk.Button.new_with_label("Supprimer"))
                    self.list_filter[-1].pack_start(self.list_button[-1], False,
                                                    False, 0)
                    self.list_button[-1].connect("clicked",
                                                 self.supprimer_filtre)
                    self.vbox2.pack_start(self.list_filter[-1], False, False, 0)
                    self.window.show_all()

            dialog.destroy()

    def supprimer_filtre(self, button):
        i = self.list_button.index(button)
        self.list_button.pop(i)
        vbox_to_del = self.list_filter.pop(i)
        vbox_to_del.destroy()
        self.window.show_all()


if __name__ == "__main__":
    pass
