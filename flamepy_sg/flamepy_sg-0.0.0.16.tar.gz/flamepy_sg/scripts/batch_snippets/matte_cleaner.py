def main():

    import os
    import traceback

    # absolute_path = os.path.realpath(__file__)
    # root_path = '/'.join(absolute_path.split('/')[0:-3])

    from flamepy_sg.scripts.customprints.ansi_colors import sg_colors

    # print "RUNNING SNIPPET = MATTE CLEANER"
    print sg_colors.blue2 + "--- Begining of matte_claener_01a --- " + sg_colors.grey3
    print ''
    print "A mini toolkit to cleanup crap around a more solid matte without having to garbage mask."
    print "Could also be used to remove or isolate different sizes of floating particles."
    print "Extend the principle to your liking ..." + sg_colors.endc

    import flame

    print sg_colors.red2 + "--- remember: 2018.3 doesn't need '.get_value()', 2019 does. ---" + sg_colors.grey3

    try:
        selected = flame.batch.current_node.get_value()  # for 2019 and up
    except:
        traceback.print_exc()
        selected = flame.batch.current_node  # for 2018.3

    # print selected.attributes

    mux_in = flame.batch.create_node("Mux")
    mux_in.name = "cleanMatte_IN"
    mux_in.pos_x = selected.pos_x + 250
    mux_in.pos_y = selected.pos_y

    matte_edge1 = flame.batch.create_node("Matte Edge")
    matte_edge1.name = "shrink"
    matte_edge1.pos_x = mux_in.pos_x + 100
    matte_edge1.pos_y = mux_in.pos_y - 150
    matte_edge1.load_node_setup("/opt/flame_dev/house_projects/17P998flame_hooks_sg_console/devl/snippets_setups/edge/shrink_4.edge_node")

    matte_edge2 = flame.batch.create_node("Matte Edge")
    matte_edge2.name = "expand"
    matte_edge2.pos_x = matte_edge1.pos_x + 200
    matte_edge2.pos_y = matte_edge1.pos_y + 0
    matte_edge2.load_node_setup("/opt/flame_dev/house_projects/17P998flame_hooks_sg_console/devl/snippets_setups/edge/expand_4.edge_node")

    comp1 = flame.batch.create_node("Comp")
    comp1.name = "clean_around"
    comp1.pos_x = matte_edge2.pos_x + 100
    comp1.pos_y = matte_edge1.pos_y + 150

    flame.batch.connect_nodes(selected, "Default", mux_in, "Default")
    flame.batch.connect_nodes(mux_in, "Default", matte_edge1, "Default")
    flame.batch.connect_nodes(matte_edge1, "Default", matte_edge2, "Default")
    flame.batch.connect_nodes(mux_in, "Default", comp1, "Front")
    flame.batch.connect_nodes(matte_edge1, "Default", comp1, "Back")
    flame.batch.connect_nodes(matte_edge2, "Default", comp1, "Matte")

    # print "\x1b[38;5;202m --- End of matte_claener_01a --- \x1b[0m"
    print sg_colors.orange1 + "--- End of matte_claener_01a ---" + sg_colors.endc
