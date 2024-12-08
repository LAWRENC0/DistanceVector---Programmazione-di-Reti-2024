from typing import List
from Router import Router
import tkinter as tk
import configparser

class NetworkVisualization:
    
    def __init__(self):
        self.running = True
        self.root = tk.Tk()
        self.root.title("Router Network Visualization")
        self.root.state("normal")
        self.width = int(self.root.winfo_screenwidth() * 0.6)
        self.height = int(self.root.winfo_screenheight() * 0.85)
        self.iteration = 0
        # read the configuration files
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.router_color = config['router_settings']['router_color']
        self.router_text_color = config['router_settings']['router_text_color']
        self.router_outline_color = config['router_settings']['router_outline_color']
        self.router_outline_h_color = config['router_settings']['router_outline_h_color']
        self.link_color = config['router_settings']['link_color']
        self.link_h_color = config['router_settings']['link_h_color']
        self.link_text_color = config['router_settings']['link_text_color']
        self.canvas_bg_color = config['router_settings']['canvas_bg_color']
        self.buttons_color = config['router_settings']['buttons_color']
        self.button_frame_color = config['router_settings']['button_frame_color']
        self.logger_color = config['router_settings']['logger_background']
        self.router_radius: int = int(config['gui']['router_radius'])
        # override the closing window method for breaking out of the main loop
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # generate the upper frame, which will contain a further container for the buttons
        button_frame = tk.Frame(self.root, bg=self.button_frame_color, height=self.height / 10)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        button_frame.pack_propagate(False)
        button_container = tk.Frame(button_frame, bg=self.button_frame_color)
        button_container.pack(anchor="center")
        next_button = tk.Button(
            button_container, 
            text="Next", 
            command=self.update_routers, 
            font=("Helvetica", 20, "bold"),
            width=10, 
            height=2, 
            background=self.buttons_color,
            foreground="white",
            activebackground=self.buttons_color,
            activeforeground="white",
            relief="raised",
            borderwidth=3
        )
        next_button.pack(side=tk.LEFT, padx=10, pady=2)
        print_button = tk.Button(
            button_container, 
            text="Print", 
            command=self.print_routing_tables, 
            font=("Helvetica", 20, "bold"),
            width=10, 
            height=2, 
            background=self.buttons_color,
            foreground="white",
            activebackground=self.buttons_color,
            activeforeground="white",
            relief="raised",
            borderwidth=3
        )
        print_button.pack(side=tk.LEFT, padx=10, pady=2)
        restart_button = tk.Button(
            button_container, 
            text="Restart", 
            command=self.stop, 
            font=("Helvetica", 20, "bold"),
            width=10, 
            height=2, 
            background=self.buttons_color,
            foreground="white",
            activebackground=self.buttons_color,
            activeforeground="white",
            relief="raised",
            borderwidth=3
        )
        restart_button.pack(side=tk.LEFT, padx=10, pady=2)
        # generate the lower frame, which will contain the canvas and logger
        lower_frame = tk.Frame(self.root, bg=self.canvas_bg_color)
        lower_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(
            lower_frame, 
            bd=3,
            relief="ridge",
            bg=self.canvas_bg_color,
            width=int(self.width)
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logger_frame = tk.Frame(lower_frame, bg=self.canvas_bg_color,bd=3,relief="ridge")
        logger_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.text_area = tk.Text(
            logger_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.logger_color,
            font=("Courier", 12),
            relief="flat",
            width=int(self.width / 20 ),
            padx=20,
            pady=20
        )
        scrollbar = tk.Scrollbar(logger_frame, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def get_screen_size(self):
        return (self.width, self.height)
        
    def add_routers(self, router_list):
        self.router_list: List[Router] = router_list
        # this dictionaries' values are the graphical segments (the edges visualization) which link router couples
        self.segments_dict: dict[tuple[Router, Router], int] = {}
        # this dictionaries' values are the texts associated to graphical segments
        self.segments_text_dict: dict[tuple[Router, Router], int] = {}
        # this dictionaries' values are the circles necessary for highlighting the selected routers
        self.highlight_circle_dict: dict[Router, int] = {}
        self.selected_router = None
    
    # generate the router visualizaton on canvas
    def create_routers(self):
        for i in range(len(self.router_list)):
            router = self.router_list[i]
            x = router.position[0]
            y = router.position[1]
            r = self.router_radius

            bg = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.router_color)
            txt = self.canvas.create_text(x, y, text=router.print(), fill=self.router_text_color, font=("Helvetica",int(self.router_radius / 1.3),"bold"))
            hl = self.highlight_circle_dict[router] = self.canvas.create_oval(x-r, y-r, x+r, y+r, outline=self.router_outline_color, width=3)
            self.canvas.tag_bind(bg, "<Button-1>", lambda event, r=router: self.router_interaction(r))
            self.canvas.tag_bind(txt, "<Button-1>", lambda event, r=router: self.router_interaction(r))
            self.canvas.tag_bind(hl, "<Button-1>", lambda event, r=router: self.router_interaction(r))
    
    # generate the link visualization on canvas
    def create_links(self):
        for r1 in self.router_list:
            for r2 in r1.link_dict.keys():
                edge = r2.link_dict[r1]
                segment_id = self.canvas.create_line(r1.position[0], r1.position[1], r2.position[0], r2.position[1], fill=self.link_color, width=2)
                x = (r1.position[0] + r2.position[0]) / 2
                y = (r1.position[1] + r2.position[1]) / 2
                self.segments_text_dict[(r1,r2)] = self.canvas.create_text(x, y, text=str(edge.weight), fill=self.link_text_color, font=("Helvetica",int(self.router_radius / 1.3),"bold"))
                self.segments_text_dict[(r2,r1)] = self.canvas.create_text(x, y, text=str(edge.weight), fill=self.link_text_color, font=("Helvetica",int(self.router_radius / 1.3),"bold"))
                
                self.segments_dict[(r1,r2)] = segment_id
                self.segments_dict[(r2,r1)] = segment_id
    
    # function called on interaction with routers
    def router_interaction(self, router: Router):
        self.reset_highlights()
        self.toggle_highlights(router)
        self.selected_router = router
    
    # function called on "next" button interaction
    def update_routers(self):
        self.iteration = self.iteration + 1
        self.print_log("--------------------------------------") 
        self.print_log("\t\tITERATION " + str(self.iteration)) 
        self.print_log("--------------------------------------") 
        self.reset_highlights()
        for router in self.router_list:
            router.share_dv()
        for router in self.router_list:
            router.update_routing_table()
    
    # higlights grafical components
    def toggle_highlights(self, router: Router):
        # highlight the clicked router
        self.canvas.itemconfig(self.highlight_circle_dict[router], outline=self.router_outline_h_color)
        # highlight its neighbours and the text on the links
        for r in router.link_dict.keys():
            self.canvas.itemconfig(self.highlight_circle_dict[r], outline=self.router_outline_h_color)
            self.canvas.itemconfig(self.segments_text_dict[(r,router)], fill=self.router_outline_h_color)
            self.canvas.itemconfig(self.segments_text_dict[(router,r)], fill=self.router_outline_h_color)
        self.print_log("\n")
        # calculate the path from the router to all the routers in its routing table
        for r_dest in router.routing_table.keys():
            if(r_dest != router):
                self.print_log("PATH FROM " + router.print() +" TO " + r_dest.print() +": " + str(router.routing_table[r_dest][0]))
                lines_route = self.get_line_route(router, r_dest)
                # highlight each line in the path calculated above
                for line in lines_route:
                    self.canvas.itemconfig(line, fill=self.link_h_color)
    
    # find the path from router start to router dest
    def get_line_route(self, start: Router, dest: Router):
        lines_route = set()
        s = start
        d = dest
        while True:
            hop = s.routing_table.get(d)[1]
            if hop:
                line = self.segments_dict.get((s,hop))
                edge = s.link_dict[hop]
                self.print_log("\t" + s.print() + " -> " + hop.print() + ": " + str(edge.weight))
                lines_route.add(line)
                # if reached the end break
                if(hop == d): 
                    break
                s = hop
            else:
                break
        return lines_route

    def reset_highlights(self):
        for line in self.segments_dict.values():
            self.canvas.itemconfig(line, fill=self.link_color)
        for text in self.segments_text_dict.values():
            self.canvas.itemconfig(text, fill=self.link_text_color)
        for h_circle in self.highlight_circle_dict.values():
            self.canvas.itemconfig(h_circle, outline=self.router_outline_color)
            
    def print_routing_tables(self):
        self.print_log("--------------------------------------" + "\n") 
        for router in self.router_list:
            self.print_log(router.print_dv())
            
    def print_log(self, log_message):
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, log_message)
        self.text_area.insert(tk.END, "\n")
        self.text_area.configure(state=tk.DISABLED)
        self.text_area.see(tk.END)
        
    def run(self):
        self.root.mainloop()
        
    def stop(self):
        self.running = True
        self.root.destroy()
        
    def on_close(self):
        self.running = False
        self.root.destroy()
        
    def is_running(self):
        return self.running

