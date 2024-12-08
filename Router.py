from hmac import new
from typing import List,Dict
from Edge import Edge

class Router:
    __slots__: List[str] = ['name', 'link_dict', 'position', 'routing_table', 'temp_routing_table']
    
    def __init__ (self, name: str, position: tuple[int,int]) -> None:
        self.name: str = name
        self.link_dict: dict[Router,Edge] = {}
        self.position = position
        self.routing_table: dict[Router, tuple[int, Router]] = {}
        self.temp_routing_table: dict[Router, tuple[int, Router]] = {}
        self.temp_routing_table[self] = (0, None)
        self.update_routing_table()
        
    def add_link(self, r1: 'Router', e1: Edge) -> None:
        self.link_dict[r1] = e1
        
    def print(self) -> str:
        return self.name
    
    def print_dv(self) -> str:
        out:str = "ROUTING TABLE OF ROUTER: " + self.print() + "\n"
        out += f"{'DEST':<10} {'DISTANCE':<10} {'HOP':<10}\n"
        for key,value in self.routing_table.items():
            source_str = key.print() if key else "None"
            router_str = value[1].print() if value[1] else "None"
            out += f"{source_str:<10} {value[0]:<10} {router_str:<10}\n"
        return out
    
    # function to be called for updating distance vector. 'source_r' sends 'source_r_table' (its distance vector) 
    # to the target router (which must be one of 'source_r' neighbours)
    def update_dv(self, source_r: 'Router', source_r_table: dict['Router', tuple[int, 'Router']]) -> None:
        edge = self.link_dict[source_r]
        for dest_r in source_r_table.keys():
            new_cost = source_r_table[dest_r][0]
            if dest_r not in self.routing_table.keys(): #destination router not present
                self.temp_routing_table[dest_r] = (new_cost + edge.weight, source_r)
            else:
                curr_cost = self.routing_table[dest_r][0]
                if new_cost + edge.weight < curr_cost:
                    self.temp_routing_table[dest_r] = (new_cost + edge.weight, source_r)
                    
    
    def share_dv(self) -> None:
        for neighbour in self.link_dict:
            neighbour.update_dv(self, self.routing_table)
            
    def update_routing_table(self) -> None:
        self.routing_table = dict(self.temp_routing_table)