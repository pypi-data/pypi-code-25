
import heapq

def dijkstra_search(edge_func, child_func, start_id, end_id):
    """
    Search for the shortest path between two points given the start id to the end id

    paramaters
    ----------
    edge_func : function(C,A,B)
        function that has calculates the score from A to B. C is the parent of A
    child_func : function(A)
        function that returns all the child of the given the id of the node, A.
    start_id : string
        starting node id
    end_id : string
        ending node id 

    return
    ------
    list
        A list of the IDs that starts from the start id to end id. If no path was found, an empty list is returned.
    """
    #initialize the support dicts
    parent_list = dict()
    cost_list = dict()
    pheap = [] #priority heap
    found_flag = False

    parent_list[start_id] = start_id
    #initialize the starting cost 
    cost_list[start_id] = 0
    #push the start node onto the heap
    heapq.heappush(pheap, (0, start_id))
        
    #start looping through the priority queue
    while len(pheap) != 0:
        #pop the smaller item
        dist_to_id, curr_id = heapq.heappop(pheap)
        #quit if we reach target
        if curr_id == end_id:
            found_flag = True
            break
        #get the list of child ids given current id
        children = child_func(curr_id)
        #get the parent ID
        parent_id = parent_list[curr_id]
        for child_id in children:
            #calculate the cost to move from the current id to the child id
            cost = edge_func(parent_id, curr_id, child_id)
            #get real cost from the beginning
            cost += cost_list[curr_id]
            #we already visited the children before
            if child_id in cost_list:
                #update if the cost is less
                if cost < cost_list[child_id]:
                    #update existing data
                    parent_list[child_id] = curr_id
                    cost_list[child_id] = cost                
                    #update heap queue
                    for h in pheap:
                        if h[1] == child_id:
                            pheap.remove(h) #remove the current child from the list
                            heapq.heappush(pheap, (cost, child_id)) #push the new cost
                            break
            else:
                #update data
                parent_list[child_id] = curr_id
                cost_list[child_id] = cost
                #push to heap queue
                heapq.heappush(pheap, (cost, child_id))

    if found_flag:
        curr_id = end_id
        travel_list = [curr_id]
        while curr_id != start_id:
            curr_id = parent_list[curr_id]
            travel_list.insert(0, curr_id)
        return travel_list
    else:
        return []