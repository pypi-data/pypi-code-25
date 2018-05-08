import gi
import sqlite3
import cairo 
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from operator import itemgetter
from graph_tool.all import *
from tkinter import * 

from galaxies.src.gui.gui_tools import *


WINDOW_TITLE = "Galaxie Vizualisation"


#Tester d'ouvrir 1 graphe, faire des filtres et ouvrir un autre graph différent
class WindowsGalaxieVizualisation:
	def __init__(self):
		self.list_filter = [None]
		self.list_button = [None]
		self.list_bool_already = [None]
		self.already_filter_date = False
		self.already_filter_author = False
		self.path = None
		self.first_creation = True
		self.window = Gtk.Window(title=WINDOW_TITLE)
		self.window.maximize()
	
			
		self.menubar = Gtk.MenuBar()
		
		self.menu1 = Gtk.Menu()
		self.menu1_file = Gtk.MenuItem("Fichier")
		self.menu1_file.set_submenu(self.menu1)
		
		self.menu2 = Gtk.Menu()
		self.menu2_filtre = Gtk.MenuItem("Filtre")
		self.menu2_filtre.set_submenu(self.menu2)
		
		self.menu3 = Gtk.Menu()
		self.menu3_aide = Gtk.MenuItem("Aide")
		
		
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
		self.filtre_auteur.connect('activate', lambda x=0, y=0: self.filtre(x, y))
		self.menu2.append(self.filtre_auteur)
		self.filtre_annee = Gtk.MenuItem("Filtrer Année")
		self.filtre_annee.connect('activate', lambda x=0, y=1 : self.filtre(x, y))
		self.menu2.append(self.filtre_annee)
		
		self.menubar.append(self.menu1_file)
		self.menubar.append(self.menu2_filtre)
		self.menubar.append(self.menu3_aide)
		
		self.vbox = Gtk.VBox(False, 2)
		self.vbox.pack_start(self.menubar, False, False, 0)
		self.window.add(self.vbox)
		
		self.hbox = Gtk.HBox(False, 0)
		
		#barre horizontal
		self.sw = Gtk.ScrolledWindow()
		#barre vertical
		self.sw2 = Gtk.ScrolledWindow()
		
		
		self.vbox2 = Gtk.VBox(False, 2)

		self.g = Graph()

		position = sfdp_layout(self.g)
		self.l= GraphWidget(self.g, pos=position, vertex_font_size=15)
		
		self.l.set_size_request(self.window.get_screen().get_width() -200, self.window.get_screen().get_height () -400)
		
		self.sw.add_with_viewport(self.vbox2)
		
		self.hbox.pack_start(self.sw, True, True, 0)
		self.hbox.pack_start(self.l, False, False, 0)
		
		color = Gdk.color_parse('#d3d3d3')
		color2 = Gdk.color_parse('#595959')
		self.sw.modify_bg(Gtk.StateType.NORMAL, color)
		self.sw2.modify_bg(Gtk.StateType.NORMAL, color)
		
		self.vbox.add(self.hbox)
		self.vbox.add(self.sw2)
		
		self.window.connect("delete-event", Gtk.main_quit)
		self.window.show_all()
		
		Gtk.main()

	def charger_reu(self, event):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.path = dialog.get_filename()
			rows = get_father_son(self.path)
			self.list_list_edges = [rows]
			self.redraw_graphe(rows)
		dialog.destroy()

	def display_get_info(self, list_edges):
		self.no_name_h = Gtk.HBox()
		self.no_name_v = Gtk.VBox()
		liste = Gtk.ListStore(str)
		l = []
		for i in list_edges:
			if i[0] not in l:
				l.append(i[0])
				liste.append([str(i[0])])

		self.cb = Gtk.ComboBox().new_with_model_and_entry(liste)
		self.cb.set_entry_text_column(0)
		label = Gtk.Label("Choix d'un noeud")
		self.button_info = Gtk.Button("Valider")
		self.button_info.connect("clicked", self.draw_graph_vertex)
		self.label_node_info = Gtk.Label("Choisissez un noeud pour avoir ses informations et ceux de ses fils")
		self.no_name_v.pack_start(label, False, False, 10)
		self.no_name_v.pack_start(self.cb, False, False, 0)
		self.no_name_v.pack_start(self.button_info, False, False, 5)
		self.no_name_h.pack_start(self.no_name_v , False, False, 20)
		self.no_name_h.pack_start(self.label_node_info, False, False, 10)
		self.sw2.add_with_viewport(self.no_name_h)
		self.window.show_all()

	def redraw_graphe(self, list_edges):	
		self.g = Graph()
		vertex_id = 0
		self.dico_id_vertex = {}
		maxi = max(max(list_edges, key=itemgetter(1))[1], max(list_edges)[0])
		tab_vertex = [None] * (maxi + 1)
		tab_edges = []
		for e in list_edges:
			if tab_vertex[e[0]] == None:
				tab_vertex[e[0]] = self.g.add_vertex()
				self.dico_id_vertex[vertex_id] = e[0]
				vertex_id += 1
			if tab_vertex[e[1]] == None:
				tab_vertex[e[1]] = self.g.add_vertex()
				self.dico_id_vertex[vertex_id] = e[1]
				vertex_id += 1
		
			tab_edges.append(self.g.add_edge(tab_vertex[e[0]], tab_vertex[e[1]]))

		property_vertex_color = self.g.new_vertex_property("string")
		property_vertex_size = self.g.new_vertex_property("int32_t")
		for v in self.g.vertices():
			if v.out_degree() < 4 :
				property_vertex_color[v] = "turquoise"
				property_vertex_size[v] = 10
			elif v.out_degree() < 6 :
				property_vertex_color[v] = "blue"
				property_vertex_size[v] = 15
			else:
				property_vertex_color[v] = "red"
				property_vertex_size[v] = 30

		self.l.destroy()
		position = sfdp_layout(self.g)
		#vertex_size=property_vertex_size
		self.l= GraphWidget(self.g, pos=position, vertex_fill_color=property_vertex_color)
		self.l.set_size_request(self.window.get_screen().get_width() -200, self.window.get_screen().get_height () -400)
		self.hbox.pack_start(self.l, False, False, 0)
		if self.first_creation:
			self.display_get_info(list_edges)
			self.first_creation = False
		self.window.show_all()
		
	def filtre(self, event, choix):
		if self.path is not None:
			author, date = get_authors_date(self.path)
			dialog = Gtk.Dialog("Filtre", self.window, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
			v = dialog.get_content_area()
			
			if choix == 0:
				type_filter = "auteur"
				liste = Gtk.ListStore(str)
				for i in author:
					liste.append([i[0]])
			else:
				type_filter = "année"
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

					if  ((type_filter == "auteur" and self.already_filter_author) or (type_filter == "année" and self.already_filter_date)):
						self.message_dial("Filtre " + type_filter +" déjà existant, veuillez le supprimer")
						dialog.destroy()
						return
				
					fil = cb.get_model()[i][0]
					list_edges = get_filtre(self.path, type_filter, check_b.get_active(), fil)
					if len(list_edges) == 0:
						self.message_dial("Aucun résultat")
						dialog.destroy()
						return
					self.list_list_edges.append(list_edges)
					list_edges = intersection(self.list_list_edges)
					self.redraw_graphe(list_edges)
					self.modif_cells(list_edges)
					self.list_filter.append(Gtk.VBox(False, 2))
					self.list_filter[-1].set_border_width(5)
					self.list_filter[-1].override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255,255,255))
					self.list_filter[-1].pack_start(Gtk.Label("Filtre "+ inv + type_filter), False, False, 0)
					if type(fil) == str and len(fil) > 16:
						fil = fil[:16] + "..."
					self.list_filter[-1].pack_start(Gtk.Label(fil), False, False, 0)
					self.list_button.append(Gtk.Button.new_with_label("Supprimer")) 
					self.list_filter[-1].pack_start(self.list_button[-1], False, False, 0)
					self.list_button[-1].connect("clicked", self.supprimer_filtre)
					self.vbox2.pack_start(self.list_filter[-1], False, False, 0)

					if  not check_b.get_active() and type_filter == "année":
						self.already_filter_date = True
						self.list_bool_already.append((True, type_filter))

					elif not check_b.get_active() and type_filter == "auteur":
						self.already_filter_author = True
						self.list_bool_already.append((True, type_filter))
					else:
						self.list_bool_already.append((None, None))
					
					self.window.show_all()
					
			dialog.destroy()


	def supprimer_filtre(self, button):
		i = self.list_button.index(button)
		self.list_button.pop(i)
		self.list_list_edges.pop(i)
		vbox_to_del = self.list_filter.pop(i)
		vbox_to_del.destroy()
		boolean, fil = self.list_bool_already.pop(i)
		if boolean is not None:
			if fil == "année":
				self.already_filter_date = False
			elif fil == "auteur":
				self.already_filter_author = False
		list_edges = intersection(self.list_list_edges)
		self.redraw_graphe(list_edges)
		self.modif_cells(list_edges)
		self.window.show_all()


	def draw_graph_vertex(self, event):
		i = self.cb.get_active_iter()
		if i == None:
			try:
				node = int(self.cb.get_child().get_text())
			except:
				self.message_dial("Entrez un entier")
				return
		else:
			node = int(self.cb.get_model()[i][0])

		dico_text = {}
		if node not in self.dico_id_vertex:
			self.message_dial("Ce noeud n'existe pas")

		i = 1
		g2 = Graph()
		node_list = [g2.add_vertex()]
		dico_text = {}
		dico_text2 = {}
		for v in self.g.vertex(node).out_neighbors():
			dico_text[0] = get_text(self.path, self.dico_id_vertex[node], self.dico_id_vertex[v])[0]
			dico_text2[node] = dico_text[0]
			node_list.append(g2.add_vertex())
			dico_text[i] = get_text(self.path, self.dico_id_vertex[node], self.dico_id_vertex[v])[1]
			dico_text2[v] = dico_text[i]
			i += 1

		prop = g2.new_vertex_property("string")
		try:
			prop[node_list[0]] = dico_text[0]
		except:
			self.message_dial("Entrez le noeud pere")
			return
		
		for i in range(1, len(node_list)):
			g2.add_edge(node_list[0], node_list[i])
			prop[node_list[i]] = dico_text[i]

		pos = sfdp_layout(g2)
		self.display_node_info(node, dico_text2)
		graph_draw(g2, pos=pos,  vertex_shape="none", vertex_text=prop, vertex_text_color="black", vertex_pen_width=0.3, vertex_font_size=20, vertex_halo_size=0.0)
      

	def message_dial(self, message):
		dialog = Gtk.Dialog(message, self.window, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
		v = dialog.get_content_area()
		v.pack_start(Gtk.Label(message), False, False, 0)
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			dialog.destroy()


	def modif_cells(self, list_edges):
		self.cb.destroy()
		self.button_info.destroy()
		liste = Gtk.ListStore(str)
		l = []
		for key in self.dico_id_vertex:
			for i in list_edges:
				if self.dico_id_vertex[key] == i[0]:
					l.append(key)
					liste.append([str(key)])
		self.cb = Gtk.ComboBox().new_with_model_and_entry(liste)
		self.cb.set_entry_text_column(0)
		self.no_name_v.pack_start(self.cb, False, False, 0)
		self.button_info = Gtk.Button("Valider")
		self.button_info.connect("clicked", self.draw_graph_vertex)
		self.no_name_v.pack_start(self.button_info, False, False, 5)


	def display_node_info(self, x, dico_text):
		label = "Noeud : Titre /// Auteur /// Date /// Texte\n\n\n"
		info = get_node_info(self.path, self.dico_id_vertex[x], self.dico_id_vertex[x+1])
		titre = info[0]
		auteur = info[1]
		date = info[2]
		text = dico_text[x]
		label += "Noeud " + str(x) + " : " + titre + " /// " + auteur + " /// " + str(date) + " /// " + text + " \n"
		for y in dico_text:
			if y != x:
				info = get_node_info(self.path, self.dico_id_vertex[x], self.dico_id_vertex[y])
				titre = info[3]
				auteur = info[4]
				date = info[5]
				text = dico_text[y]
				label += "Noeud " + str(y) + " : " + titre + " /// " + auteur + " /// " + str(date) + " /// " + text + " \n"
		self.label_node_info.set_text(label)


if __name__ == "__main__":
	menu = WindowsGalaxieVizualisation()

