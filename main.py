from math import sqrt
from Router import Router
from Edge import Edge
from typing import List
import random
from math import comb
from NetworkVisualization import NetworkVisualization
import configparser

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    num_routers: int = int(config['network']['num_routers'])
    num_edges: int = int(config['network']['num_edges'])
    router_radius: int = int(config['gui']['router_radius'])
    router_spacing: int = int(config['gui']['router_spacing'])
    if comb(num_routers, 2) < num_edges:
        num_edges = comb(num_routers,2)
        print("IMPOSSIBLE CONFIGURATION: setting num_edges to the max")
        print("num_edges = " + str(num_edges))
    # main loop
    while(True):
        network = NetworkVisualization()
        gui_width = network.get_screen_size()[0]
        gui_height = network.get_screen_size()[1]
        router_list: List[Router] = []
        edge_list: List[Edge] = []
        # generate routers
        for i in range(0,num_routers):
            while True:
                position = generate_position(router_radius, gui_width, gui_height)
                if(is_available(position,router_radius,router_list,router_spacing)):
                    break
            router_list.append(Router(str(i), position))
        # generate router links
        edge_check: List[tuple[int,int]] = []
        for i in range(0,num_edges):
            while True:
                a = random.randint(0,num_routers-1)
                b = random.randint(0,num_routers-1)
                if b != a and ((a,b) not in edge_check):
                    break
            edge_check.append((a,b))
            edge_check.append((b,a))
            d = int(distance(router_list[a].position, router_list[b].position) * random.uniform(0.1,1.9))
            edge = Edge("e" + str(i), d)
            edge_list.append(edge)
            router_list[a].add_link(router_list[b],edge)
            router_list[b].add_link(router_list[a],edge)
        network.add_routers(router_list)
        network.create_links()
        network.create_routers()
        # start the gui
        network.run()
        if network.is_running() == False:
            break
        
def distance(pos1: tuple[int,int], pos2: tuple[int,int]) -> int:
    return int(sqrt(pow(pos1[0] - pos2[0],2) + pow(pos1[1] - pos2[1],2)))

def generate_position(radius: int, width: int, height:int) -> tuple[int,int]:
    return (random.randint(int(radius*2), width-int(radius*2)),random.randint(int(radius*2),height-int(radius*2)))

def is_available(position: tuple[int,int], radius:int, router_list: List[Router], router_spacing: int) -> bool:
    for router in router_list:
        p1 = router.position
        if (abs(p1[0]-position[0]) <= radius*router_spacing) and (abs(p1[1]-position[1]) <= radius*router_spacing):
            return False
    return True
    
if __name__ == "__main__":
    main()
    