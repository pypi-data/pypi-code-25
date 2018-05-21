def main():

    import os
    import traceback

    absolute_path = os.path.realpath(__file__)
    root_path = '/'.join(absolute_path.split('/')[0:-3])

    from flamepy_sg.scripts.customprints.ansi_colors import sg_colors

    # print "RUNNING SNIPPET = CONNECTED DUPLICATE"
    print sg_colors.blue2 + "--- Begining of connected_duplicate_02a.py --- ", root_path + sg_colors.grey3
    print "Modules path: " + "{root}/flame_hooks_sg/modules".format(root=root_path)
    print '-' * 5
    print "Dulicates the selected node while keeping it's incoming connections"
    print "Only works for most common Front/Back/Matte types of nodes and mux ones."
    print "No Z-Depth or Forward vectors (...) yet = Todo"
    print '-' * 5 + sg_colors.endc

    import flame

    # ########## DUPLICATE ORIGINAL ###########
    print sg_colors.red2 + "--- remember: 2018.3 doesn't need '.get_value()', 2019 does. ---" + sg_colors.endc

    try:
        original = flame.batch.current_node.get_value()  # for 2019 and up
    except:
        traceback.print_exc()
        original = flame.batch.current_node  # for 2918.3

    original_type = str(original.type)

    duplicate = flame.batch.create_node(original_type.replace("'", ''))
    duplicate.pos_x = original.pos_x + 50
    duplicate.pos_y = original.pos_y + 300
    duplicate.name = original.name + '_copy'

    # ########## PRINT INFOS ############
    print ''
    print sg_colors.yellow1 + "-" + " Original: Sockets: " + sg_colors.grey3
    print (original.sockets), sg_colors.endc
    # print sg_colors.endc

    # ############ USING: If ... In keys ############
    front_in = None
    back_in = None
    matte_in = None
    input_0_in = None
    matte_0_in = None

    if "Front" in original.sockets['input'].keys():
        front_in = original.sockets['input']['Front']
    if "Back" in original.sockets['input'].keys():
        back_in = original.sockets['input']['Back']
    if "Matte" in original.sockets['input'].keys():
        matte_in = original.sockets['input']['Matte']

    if "Input_0" in original.sockets['input'].keys():
        input_0_in = original.sockets['input']['Input_0']
    if "Matte_0" in original.sockets['input'].keys():
        matte_0_in = original.sockets['input']['Matte_0']

    # ########## CONNECTIONS ###########
    print ''
    print sg_colors.yellow1 + "-" + " duplicate: Input connections: " + sg_colors.grey3

    # For 'Front/Back/Matte input nodes:'
    if front_in != None:
        node_in_front = flame.batch.get_node(str(front_in[0]))
    if back_in != None:
        node_in_back = flame.batch.get_node(str(back_in[0]))
    if matte_in != None:
        node_in_matte = flame.batch.get_node(str(matte_in[0]))
    # For Mux nodes:
    if input_0_in != None:
        node_in_input0 = flame.batch.get_node(str(input_0_in[0]))
    if matte_0_in != None:
        node_in_matte0 = flame.batch.get_node(str(matte_0_in[0]))

    if front_in != None:
        print "front in = " + front_in[0]
        flame.batch.connect_nodes(node_in_front, "Default", duplicate, "Front")
    if back_in != None:
        print "back in = " + back_in[0]
        flame.batch.connect_nodes(node_in_back, "Default", duplicate, "Back")
    if matte_in != None:
        print "matte in = " + matte_in[0]
        flame.batch.connect_nodes(node_in_matte, "Default", duplicate, "Matte")

    if input_0_in != None:
        print "input_0 in = " + input_0_in[0]
        flame.batch.connect_nodes(node_in_input0, "Default", duplicate, "Input_0")
    if matte_0_in != None:
        print "matte_0 in = " + matte_0_in[0]
        flame.batch.connect_nodes(node_in_matte0, "Default", duplicate, "Matte_0")
    print sg_colors.endc

    print sg_colors.orange1 + "--- End of connected_dupliscate_02a.py ---" + sg_colors.endc
