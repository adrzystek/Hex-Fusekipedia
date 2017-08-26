# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 00:11:22 2017

@author: adrzystek
"""


import time
import urllib.request
import re
import tkinter as tk
import sqlite3
import webbrowser
from bs4 import BeautifulSoup
from tkinter import font
from tkinter import messagebox


class Hex_Fusekipedia(tk.Frame):
    
    def __init__(self, parent, rows=13, columns=13, technical_size=48, color1="red", color2="blue"):
        self.rows = rows
        self.columns = columns
        self.size = rows
        self.technical_size = technical_size
        self.color1 = color1
        self.color2 = color2
        self.a = self.technical_size / (3**0.5)
        self.hexes_dict = {}
        self.games_in_question = []
        self.move_number = 1
        self.moves_list = []
        self.static_moves_history_list = []
        self.dynamic_moves_history_list = []
        self.static_games_history_list = []
        self.dynamic_games_history_list = []
        self.TEST = False
        self.mode = "championships"
        
        # menubar
        self.setup_menu(parent)
        
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack()
        #tk.Frame.__init__(self, parent)
        #self.pack()
        self.canvas = tk.Canvas(self.main_frame, borderwidth=0, highlightthickness=0, background="white",
                                width = self.a * (3 ** 0.5) * (self.columns + 0.5 * (self.rows - 1)) + self.a * (3 ** 0.5),
                                height = 2 * self.a * (self.rows // 2 + 1) + self.a * (self.rows // 2) + 2 * self.a)
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-3>", lambda event: self.undo_a_move())
        self.canvas.focus_set()    # crucial for below key-bindings
        self.canvas.bind("f", lambda event: self.undo_all_moves())
        self.canvas.bind("p", lambda event: self.undo_a_move())
        self.canvas.bind("n", lambda event: self.play_the_next_move())
        self.canvas.bind("l", lambda event: self.play_all_next_moves())
        
        if self.TEST:
            self.right_side_frame = tk.Frame(self.main_frame, bg="yellow")
            self.right_side_frame_top = tk.Frame(self.right_side_frame, bg="grey")
            self.right_side_frame_bottom = tk.Frame(self.right_side_frame, bg="red")
            self.control_frame = tk.Frame(self.right_side_frame_top, bg="cyan")
            self.info_frame = tk.Frame(self.right_side_frame_top, bg="tan")
            self.frame_for_canvas = tk.Frame(self.right_side_frame_top, bg="blue")
            self.moves_canvas = tk.Canvas(self.frame_for_canvas, width=1, height=300, bg="gold")    # height=300 - just proper for 48 (technical) size
            self.scrollbar = tk.Scrollbar(self.frame_for_canvas, orient="vertical", command=self.moves_canvas.yview)    # parent=self.moves_canvas possibly?
            self.moves_frame = tk.Frame(self.moves_canvas, bg="white")
            self.position_info = tk.LabelFrame(self.right_side_frame_bottom, text="Position info", bg="green")
        else:
            self.right_side_frame = tk.Frame(self.main_frame)
            self.right_side_frame_top = tk.Frame(self.right_side_frame)
            self.right_side_frame_bottom = tk.Frame(self.right_side_frame)
            self.control_frame = tk.Frame(self.right_side_frame_top)
            self.info_frame = tk.Frame(self.right_side_frame_top)
            self.frame_for_canvas = tk.Frame(self.right_side_frame_top)
            self.moves_canvas = tk.Canvas(self.frame_for_canvas, width=1, height=300)    # height=300 - just proper for 48 (technical) size
            self.scrollbar = tk.Scrollbar(self.frame_for_canvas, orient="vertical", command=self.moves_canvas.yview)    # parent=self.moves_canvas possibly?
            self.moves_frame = tk.Frame(self.moves_canvas)
            self.position_info = tk.LabelFrame(self.right_side_frame_bottom, text="Position info")
            
        self.right_side_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        self.right_side_frame_top.pack(side="top", fill="both", padx=10, pady=10, anchor="n")
        self.right_side_frame_bottom.pack(side="bottom", expand=True, fill="both", padx=10, pady=10, anchor="s")        
        self.control_frame.pack(side="top", expand=True, fill="x", padx=10, pady=10, anchor="n")
        self.info_frame.pack(side="top", expand=True, fill="x", pady=10, anchor="n")
        self.frame_for_canvas.pack(side="top", expand=True, fill="x", pady=(10,0), anchor="n")
        self.moves_canvas.pack(side="left", expand=True, fill="both", anchor="n")
        self.position_info.pack(side="bottom", pady=10, anchor="s")
        
        self.canvas_frame = self.moves_canvas.create_window((0,0), window=self.moves_frame, anchor='nw') 
        
        self.moves_canvas.config(yscrollcommand=self.scrollbar.set)
        
        self.moves_frame.bind("<Configure>", self.onFrameConfigure)
        self.moves_canvas.bind("<Configure>", self.set_canvas_width)
        #self.frame_for_canvas.bind('<Configure>', self.configure_window)    # unused but possible (see below)
        self.frame_for_canvas.bind("<Enter>", self.bound_to_mousewheel)
        self.frame_for_canvas.bind("<Leave>", self.unbound_to_mousewheel)
                
        self.moves_frame.grid_columnconfigure(0, weight=1)
        self.moves_frame.grid_columnconfigure(1, weight=1)
        self.moves_frame.grid_columnconfigure(2, weight=1)
        
        self.draw_board()
        
        self.prev_prev_button = tk.Button(self.control_frame, text="<<", relief="raised", command=self.undo_all_moves, state=tk.DISABLED)
        self.prev_prev_button.pack(side="left", expand=True, anchor="w", padx=10, pady=10)
        self.prev_button = tk.Button(self.control_frame, text="<", relief="raised", command=self.undo_a_move, state=tk.DISABLED)
        self.prev_button.pack(side="left", expand=True, anchor="w", padx=10, pady=10)
        
        self.next_next_button = tk.Button(self.control_frame, text=">>", relief="raised", command=self.play_all_next_moves, state=tk.DISABLED)
        self.next_next_button.pack(side="right", expand=True, anchor="e", padx=10, pady=10)
        self.next_button = tk.Button(self.control_frame, text=">", relief="raised", command=self.play_the_next_move, state=tk.DISABLED)
        self.next_button.pack(side="right", expand=True, anchor="e", padx=10, pady=10)
        
        self.prepare_dicts()    # contains self.load_games_data() and self.arrange_next_moves()
        
        
    def setup_menu(self, parent):
        menubar = tk.Menu(parent)
        options_menu = tk.Menu(menubar, tearoff=0)
        change_size_submenu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Change size", menu=change_size_submenu)
        self.size_choice = tk.IntVar()
        change_size_submenu.add_radiobutton(label="11x11", variable=self.size_choice, value=11, command=self.change_size)
        change_size_submenu.add_radiobutton(label="13x13", variable=self.size_choice, value=13, command=self.change_size)
        change_size_submenu.add_radiobutton(label="19x19", variable=self.size_choice, value=19, command=self.change_size)
        self.size_choice.set(13)
        #options_menu.add_command(label="Change size", command=self.invoke_change_size_window)
        options_menu.add_separator()
        options_menu.add_command(label="Select games", command=self.invoke_select_games_window)
        menubar.add_cascade(label="Options", menu=options_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About Hex", command=self.invoke_help_hex_window)
        help_menu.add_command(label="About Hex Fusekipedia", command=self.invoke_help_hex_fusekipedia_window)
        help_menu.add_separator()
        help_menu.add_command(label="Credits", command=self.invoke_credits_window)
        menubar.add_cascade(label="Info", menu=help_menu)
        parent.config(menu=menubar)
        
    
    def invoke_select_games_window(self):
        list_of_sources = list(self.d4.items())
        list_of_sources.sort(key=lambda x: x[1][2])
        self.select_games_top_window = tk.Toplevel(root)
        self.select_games_top_window.title("Select games")
        _main_frame = tk.Frame(self.select_games_top_window)
        _main_frame.pack(padx=10, pady=10)
        _labelframe = tk.LabelFrame(_main_frame, text="Select games source")
        _labelframe.grid(row=0, sticky="nwse")
        self.source_choice = tk.StringVar()
        if self.size in (13, 19):
            tk.Radiobutton(_labelframe, text="Championships", variable=self.source_choice, value="championships", command=self.show_source_info).pack(anchor="w")
        elif self.size == 11:
            tk.Radiobutton(_labelframe, text="Top ~100 players", variable=self.source_choice, value="11x11_top", command=self.show_source_info).pack(anchor="w")
        for source in list_of_sources:
            if source[0] not in ("championships", "11x11_top"):
                tk.Radiobutton(_labelframe, text=source[1][2], variable=self.source_choice, value=source[0], command=self.show_source_info).pack(anchor="w")
        self.source_choice.set("0")
        buttons_frame = tk.Frame(_main_frame)
        buttons_frame.grid(row=1, sticky="nwse", pady=10)
        tk.Button(buttons_frame, text="Add", command=self.invoke_type_player_id_window, width=6).pack(side="right")
        self.update_button = tk.Button(buttons_frame, text="Update", command=self.update_source_data, width=6, state=tk.DISABLED)
        self.update_button.pack(side="right", padx=10)
        self.tournament_only_checkbutton = tk.IntVar()
        tk.Checkbutton(_main_frame, text="Tournament games only", variable=self.tournament_only_checkbutton, command=self.show_source_info).grid(row=2, sticky="w")
        self.source_info_text = tk.Text(_main_frame, height=3, width=25, wrap=tk.WORD)
        self.source_info_text.grid(row=3, pady=10)
        self.recent_games_entry = tk.Entry(_main_frame, width=4)
        self.recent_games_entry.grid(row=4, sticky="w")
        tk.Label(_main_frame, text="recent games (leave empty for all)").grid(row=4, sticky="e")
        self.ok_button = tk.Button(_main_frame, text="OK", command=self.select_games, width=10, state=tk.DISABLED)
        self.ok_button.grid(sticky="e", pady=10)
        
        
    def show_source_info(self):
        self.update_button.config(state="normal")
        _source = self.source_choice.get()
        print("_SOURCE:", _source)
        if _source != "0":
            self.source_info_text.delete(1.0, tk.END)            
            games_cnt = self.d4[_source][1]
            if self.tournament_only_checkbutton.get():
                games_cnt = len([k for k, v in self.d3_full.items() if v[3] != "null" and _source in v[4]])
            _text = str(games_cnt) + " games, last update " + self.d4[_source][0] + "."
            self.source_info_text.insert(tk.INSERT, _text)
            self.ok_button.config(state="normal")
            
            
    def select_games(self):
        self.mode = self.source_choice.get()
        self.prepare_dicts(conditional=True)
        self.select_games_top_window.withdraw()
    
    
    def invoke_help_hex_window(self):
        top_window = tk.Toplevel(root)
        top_window.title("About Hex")
        about_hex_text = tk.Text(top_window, height=15, width=70, wrap=tk.WORD)
        about_hex_text.pack()
        _text = """    Hex is a strategy board game for two players invented independently by Danish mathematician Piet Hein and Nobel prize winner John Nash. In spite of having very simple rules, the game has deep strategy, sharp tactics and a profound mathematical underpinning related to the Brouwer fixed point theorem.
        
    Rules of the game are very simple - players alternate placing stones on unoccupied spaces in an attempt to link their opposite sides of the board in an unbroken chain. One player must win; there are no draws.
        
    For more information please see:
- http://maarup.net/thomas/hex/
- https://en.wikipedia.org/wiki/Hex_(board_game)"""
        about_hex_text.insert(tk.INSERT, _text)
        about_hex_text.tag_add("link1", "6.2", "6.31")
        about_hex_text.tag_config("link1", foreground="blue", underline=1)
        about_hex_text.tag_bind("link1", "<Enter>", self.show_hand_cursor)
        about_hex_text.tag_bind("link1", "<Leave>", self.show_normal_cursor)
        about_hex_text.tag_bind("link1", "<Button-1>", lambda event, url=r"http://maarup.net/thomas/hex/": webbrowser.open_new(url))
        about_hex_text.tag_add("link2", "7.2", "7.48")
        about_hex_text.tag_config("link2", foreground="blue", underline=1)
        about_hex_text.tag_bind("link2", "<Enter>", self.show_hand_cursor)
        about_hex_text.tag_bind("link2", "<Leave>", self.show_normal_cursor)
        about_hex_text.tag_bind("link2", "<Button-1>", lambda event, url=r"https://en.wikipedia.org/wiki/Hex_(board_game)": webbrowser.open_new(url))

    
    def invoke_help_hex_fusekipedia_window(self):
        top_window = tk.Toplevel(root)
        top_window.title("About Hex Fusekipedia")
        about_fusekipedia_text = tk.Text(top_window, height=20, width=100, wrap=tk.WORD)
        about_fusekipedia_scroll = tk.Scrollbar(top_window, command=about_fusekipedia_text.yview)
        about_fusekipedia_text.configure(yscrollcommand=about_fusekipedia_scroll.set)
        about_fusekipedia_text.pack(side="left")
        about_fusekipedia_scroll.pack(side="right", fill=tk.Y)
        _text = """    Overview
        
    Hex Fusekipedia is a project aiming to at least partially fill the gap of human unawarness in the field of how the game of hex should be played. It is based on the information coming from the Little Golem site which probably gathers the greatest number of hex players in the world, and also presumably the best of them as well. 
        
        
    Why
        
    I have comitted this because in spite of having seen similar projects, I have not come across anything that took advantage of the quantity of information that Little Golem site offers (of course by no means I say that this application exploits everything that could be exploited). Moreover, it was a lot of fun and I learnt a lot as well while creating it.
        
        
    How
        
    The application has been entirely written in Python (version 3.5). It makes use of standard libraries like time, urllib, re, pickle, sqlite3, webbrowser, bs4 and tkinter. Especially, the scraping stuff was made with the urllib and bs4 packages and the whole GUI development was possible thanks to the tkinter module.
        
        
    For who
        
    Hex Fusekipedia is dedicated to everyone willing to broaden their knowledge in the beautiful abstraction of the game of hex.
        
        
    Instructions
        
    The user can choose the size of the board of analyzed games as well as the source of the games. The size of the board is overriding, i.e., each size has its own sources (not the other way around, always the size goes first and later come the games).
    
    The variety of board size includes 11x11, 13x13 and 19x19. The selection of games sources is as follows:
- "Championship" - only for 13x13 and 19x19 - collects games from first and second leagues of all previous championships (only finished leagues are taken; note that the whole championship needs not to be finished);
- "Top100" - only for 11x11 - collects games between top 100 players in the ranking list (of hex 13x13); please note that if the user update this source, the games within "new" top 100 will be added but the present games will not be removed (in other words, this source may contain games of players not currently being in top100);
- player mode - for all sizes - collected games of a particular player.
    
    Default value is board size 13x13 and the championship mode.
    
    Apart from championship (13x13 and 19x19) and top100 (11x11) games, the database has been pre-populated with each size top three players' games.
    
    Please note that the game must be finished and be at least 6 moves long in order to be collected. Also note that every game is, if needed, mirrored so that it starts in the upper-left half of the board. Moreover, if the swap occurred in the real game, players' colors are switched and subsequent moves are re-swapped in order to show the varations in the plain manner. Changing player nickname does not negatively impact the application behaviour (no crashes, game replication) but may lead to inaccurate game descriptions (these containg who played who).
        
    Available shortcuts:
- "f" for the first move ("<<" button)
- "p" or right-click on the board screen for the previous move ("<" button)
- "n" for the next move (">" button)
- "l" for the last move (">>" button)


    Beware!
    
    Adding or updating player's or championship's data is a matter of seconds (but, naturally, it depends on user's hardware and internet connection), however, updating source of Top100 players in 11x11 mode requires browsing through a bunch (exactly 100) players' htmls and, therefore, takes up at least 5 minutes (we want to be kind to the LG server, don't we?).
        """
        #"Stand-alone executable (the .exe file that you are running right now) was built with PyInstaller."
        about_fusekipedia_text.insert(tk.INSERT, _text)
        
        about_fusekipedia_text.tag_add("bold_tag", "1.4", "1.12", "6.4", "6.7", "11.4", "11.7", "16.4", "16.11", "21.4", "21.16", "43.4", "43.11")
        about_fusekipedia_text.tag_config("bold_tag", font = font.Font(weight="bold", size=11))
        
        about_fusekipedia_text.tag_add("overstrike_tag", "13.129", "13.136")
        about_fusekipedia_text.tag_config("overstrike_tag", font = font.Font(overstrike=1))
        
        about_fusekipedia_text.tag_add("LG_link_tag", "3.196", "3.208")
        about_fusekipedia_text.tag_config("LG_link_tag", foreground="blue", underline=1)
        about_fusekipedia_text.tag_bind("LG_link_tag", "<Enter>", self.show_hand_cursor)
        about_fusekipedia_text.tag_bind("LG_link_tag", "<Leave>", self.show_normal_cursor)
        about_fusekipedia_text.tag_bind("LG_link_tag", "<Button-1>", lambda event, url=r"https://littlegolem.net/jsp/main/": webbrowser.open_new(url))
        
    
    def invoke_credits_window(self):
        top_window = tk.Toplevel(root)
        top_window.title("Credits")
        lbl = tk.Label(top_window, text="Hex Fusekipedia v2.5\n\nAndrzej Drzystek 2017\n\nContact: andrzej.drzystek@gmail.com", cursor="hand2")
        lbl.pack()
        lbl.bind("<Button-1>", lambda event: webbrowser.open_new("mailto:andrzej.drzystek@gmail.com"))
        
        
    def invoke_type_player_id_window(self):
        self.player_id_top_window = tk.Toplevel(root)
        self.player_id_top_window.title("Add")
        _main_frame = tk.Frame(self.player_id_top_window)
        _main_frame.pack()
        tk.Label(_main_frame, text="Type player id").grid(row=0, column=0, padx=10, pady=10)
        self.entry_box = tk.Entry(_main_frame, width=7)
        self.entry_box.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(_main_frame, text="Scrap!", command=self.add_source_data, width=5).grid(row=1, column=1, padx=10, pady=10)
        
        
    def add_source_data(self):
        _player_id = str(self.entry_box.get().strip())
        if len(_player_id):
            self.scrap_games_data(_player_id)
        self.player_id_top_window.withdraw()
        self.select_games_top_window.withdraw()
        self.invoke_select_games_window()
        if self.scrap_status == "":
            messagebox.showinfo("Info", "Scraping successful. " + str(self.scraped_games_cnt) + " new games added.")
        else:
            messagebox.showerror("Warning", "Scraping failed. Maybe check your internet connection or test whether the LittleGolem site is OK. The error was: " + str(self.scrap_status) + ".")
        
    def update_source_data(self):
        _source = self.source_choice.get()
        print("UPDATING DATA FOR", _source)
        self.scrap_games_data(_source)
        self.select_games_top_window.withdraw()
        self.invoke_select_games_window()
        if self.scrap_status == "":
            messagebox.showinfo("Info", "Scraping successful. " + str(self.scraped_games_cnt) + " new games added.")
        else:
            messagebox.showerror("Warning", "Scraping failed. Maybe check your internet connection or test whether the LittleGolem site is OK. The error was: " + str(self.scrap_status) + ".")
        
    
    # unused now (changed to submenu)
    def invoke_change_size_window(self):
        self.change_size_window = tk.Toplevel(root)
        self.change_size_window.title("Change size")
        _main_frame = tk.Frame(self.change_size_window)
        _main_frame.pack(padx=5, pady=5)
        _labelframe = tk.LabelFrame(_main_frame, text="Select board size")
        _labelframe.grid(row=0, sticky="nwse", padx=5, pady=5)
        self.size_choice = tk.IntVar()
        tk.Radiobutton(_labelframe, text="11x11", variable=self.size_choice, value=11).pack(side="left", padx=10, pady=5)
        tk.Radiobutton(_labelframe, text="13x13", variable=self.size_choice, value=13).pack(side="left", padx=10, pady=5)
        tk.Radiobutton(_labelframe, text="19x19", variable=self.size_choice, value=19).pack(side="left", padx=10, pady=5)
        self.size_choice.set(0)
        tk.Button(_main_frame, text="OK", command=self.change_size, width=10).grid(sticky="e", padx=5, pady=5)
        
    def change_size(self):
        #self.change_size_window.withdraw()
        _size = self.size_choice.get()
        print("NEW SIZE:", _size)
        self.rows = _size
        self.columns = _size
        self.size = _size
        self.canvas.config(width = self.a * (3 ** 0.5) * (self.columns + 0.5 * (self.rows - 1)) + self.a * (3 ** 0.5),
                           height = 2 * self.a * (self.rows // 2 + 1) + self.a * (self.rows // 2) + 2 * self.a)
        self.canvas.delete("all")
        self.draw_board()
        if self.size == 11:
            self.moves_canvas.config(height=200)
        elif self.size == 13:
            self.moves_canvas.config(height=300)
        elif self.size == 19:
            self.moves_canvas.config(height=525)
        if self.size in (13, 19):
            self.mode = "championships"
        else:
            self.mode = "11x11_top"
        self.prepare_dicts()
    
    
    def onFrameConfigure(self, event):
        self.moves_canvas.configure(scrollregion=self.moves_canvas.bbox("all"))
        
    def set_canvas_width(self, event):
        self.moves_canvas.itemconfig(self.canvas_frame, width=event.width)
    
    
    # unused but looks pro
    def configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight())
        self.canv.config(scrollregion='0 0 %s %s' % size)
        if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canv.config(width = self.scrollwindow.winfo_reqwidth())
        if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canv.config(height = self.scrollwindow.winfo_reqheight())
       
       
    def bound_to_mousewheel(self, event):
        self.moves_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
    def unbound_to_mousewheel(self, event):
        self.moves_canvas.unbind_all("<MouseWheel>")
        
    def on_mousewheel(self, event):
        self.moves_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        
    def show_hand_cursor(self, event):
        event.widget.configure(cursor="hand2")
        
    def show_normal_cursor(self, event):
        event.widget.configure(cursor="")
        
        
    def show_coordinates(self, event, move):
        adder = self.a
        i = int(self.size * 1.5)
        mirrored_move = chr(abs(ord(move[0])-96 -(self.size + 1))+96) + str(abs(int(move[1:])-(self.size + 1)))
        _text = move + " (" + mirrored_move + ")"
        self.canvas.create_text(0.5 * 0.5 * self.a * 3 ** 0.5 + adder + i * self.a * 3 ** 0.5, 10, text = _text, anchor = "e", font = font.Font(weight="bold", size=8), tags="coordinates")
        
    def hide_coordinates(self, event):
        self.canvas.delete("coordinates")
        
    
    def scrap_games_data(self, _source):
        self.load_games_data()
        try:
            self.scrap_status = ""
            self.scraped_games_cnt = 0
            if _source == "championships":
                tournament_number = 1
                break_flg = False
                while (break_flg == False):
                    for league in [1, 2]:
                        for group in [1, 2]:
                            if (league == 1 and group == 2) or (self.size == 13 and tournament_number == 1 and league == 2 and group == 2) or break_flg == True:
                                break
                            _pre = "hex." if self.size == 13 else "hex19."
                            tournament_name = _pre + "ch.{}.{}.{}".format(tournament_number, league, group)
                            if tournament_name in [v[3] for v in self.d3.values()]:
                                print("continue1 for", tournament_name)
                                continue
                            if self.size == 13:
                                tournament_url = "http://littlegolem.net/jsp/tournament/tournament.jsp?trnid=" + tournament_name
                            elif self.size == 19:
                                tournament_url = "http://littlegolem.net/jsp/tournament/tournament.jsp?trnid=" + tournament_name
                            tournament_html = urllib.request.urlopen(tournament_url).read().decode("utf-8")
                            if len(re.findall("<br>Finish date:(.*?)  </td>", str(tournament_html))) == 0:
                                break_flg = True
                                print("break for", tournament_name)
                                break           
                            finish_date = re.findall("<br>Finish date:(.*?)  </td>", str(tournament_html))[0]
                            if len(finish_date) == 0:
                                print("continue2 for", tournament_name)
                                continue
                            pgn_sgf_url = "http://littlegolem.net" + re.findall('href="(.*?)">PGN/SGF', str(tournament_html))[0]
                            html = urllib.request.urlopen(pgn_sgf_url).read()
                            print("TOURNAMENT NAME:", tournament_name)
                            self.scrap_from_html(html, "championships")                   
                            time.sleep(0.5)
                    tournament_number += 1
                games_cnt = len([k for k, v in self.d3.items() if "championships" in v[4]])
                self.d4["championships"] = [time.strftime("%Y-%m-%d"), games_cnt, "Championships"]
            elif _source == "11x11_top":
                how_many = 100
                n = 0
                page = 1
                top_players = []
                while (n < how_many):
                    players_list_url = "http://littlegolem.net/jsp/info/player_list.jsp?gtvar=hex_DEFAULT&page=" + str(page)
                    players_list_html = urllib.request.urlopen(players_list_url).read().decode("utf-8")
                    players_ids = re.findall('a href="player.jsp\?plid=(.*?)"', players_list_html)
                    for player_id in players_ids:
                        print("SCRAPING GAME DATA FOR:", player_id, "(as part of 11x11_top scraping)")
                        # getting the player's name
                        html = urllib.request.urlopen('http://littlegolem.net/jsp/info/player.jsp?plid=%s' % (player_id)).read()
                        soup = BeautifulSoup(html, 'lxml')
                        player_name = re.findall('<b>Name:</b></td>\n<td>(.*?)</td>', str(soup.find_all('div', class_ = "table")))[0]
                        if player_name.startswith('['):
                            player_name = player_name[1:]
                        if player_name.endswith(']'):
                            player_name = player_name[:-1]
                        # getting the player's games
                        html = urllib.request.urlopen('http://littlegolem.net/jsp/info/player_game_list_txt.jsp?plid=%s&gtid=hex' % (player_id)).read()
                        self.scrap_from_html(html, "11x11_top")
                        top_players.append(player_name)
                        n += 1
                        if n == how_many:
                            break
                        time.sleep(0.25)
                    page += 1
                print("FINISHED SCRAPING TOP100")
                    
                # extracting only games between the top players
                games_between_top_players = []
                print("LEN OF D3:", len(self.d3))
                print("LEN OF top_player:", len(top_players))
                self.top_players = top_players
                for i in self.d3:
                    if self.d3[i][0] in top_players and self.d3[i][1] in top_players:
                        games_between_top_players.append(i)
                print("NUMBER OF GAMES BETWEEN TOP PLAYERS:", len(games_between_top_players)) #139
                new_d1 = {}
                new_d2 = {}
                new_d3 = {}
                for i in games_between_top_players:
                    new_d1[i] = self.d1[i]
                    new_d3[i] = self.d3[i]
                for k in self.d2.keys():
                    new_content = set(self.d2[k]) & set(games_between_top_players)
                    if len(new_content) > 0:
                        new_d2[k] = list(new_content)
                games_cnt = len([k for k, v in new_d3.items() if "11x11_top" in v[4]])
                self.d4["11x11_top"] = [time.strftime("%Y-%m-%d"), games_cnt, "Top ~100 players"]
                self.d1 = new_d1.copy()
                self.d2 = new_d2.copy()
                self.d3 = new_d3.copy()
            else:
                print("SCRAPING GAME DATA FOR:", _source)
                # getting the player's name
                html = urllib.request.urlopen('http://littlegolem.net/jsp/info/player.jsp?plid=%s' % (_source)).read()
                if len(html) == 0:
                    return
                print("SCRAPING...")
                soup = BeautifulSoup(html, 'lxml')
                player_name = re.findall('<b>Name:</b></td>\n<td>(.*?)</td>', str(soup.find_all('div', class_ = "table")))[0]
                if player_name.startswith('['):
                    player_name = player_name[1:]
                if player_name.endswith(']'):
                    player_name = player_name[:-1]
                # getting the player's games
                if self.size in (11, 13):
                    html = urllib.request.urlopen('http://littlegolem.net/jsp/info/player_game_list_txt.jsp?plid=%s&gtid=hex' % (_source)).read()
                elif self.size == 19:
                    html = urllib.request.urlopen('http://littlegolem.net/jsp/info/player_game_list_txt.jsp?plid=%s&gtid=hex19' % (_source)).read()
                self.scrap_from_html(html, _source)
                games_cnt = len([k for k, v in self.d3.items() if _source in v[4]])
                self.d4[_source] = [time.strftime("%Y-%m-%d"), games_cnt, player_name + " (" + _source + ")"]
            self.static_moves_history_list = []    # this way everything will be cleared (calling undo_all_moves is not enough)
            self.undo_all_moves()
            
            conn = sqlite3.connect('hex_fusekipedia_db.sqlite3')
            cur = conn.cursor()
            for i in self.d1:
                for j in self.d1[i]:
                    cur.execute('INSERT OR IGNORE INTO t1 (game_id, move) VALUES (?, ? )', (i, str(j) + ' ' + self.d1[i][j]))
            for i in self.d3:
                cur.execute('INSERT OR IGNORE INTO t2 (game_id, red_player, blue_player, red_won_flg, event, size) VALUES (?, ?, ?, ?, ?, ?)', (i, self.d3[i][0], self.d3[i][1], self.d3[i][2], self.d3[i][3], self.size))
                for j in range(len(self.d3[i][4])):
                    cur.execute('INSERT OR IGNORE INTO t3 (game_id, matching) VALUES (?, ?)', (i, self.d3[i][4][j]))
            for i in self.d4:
                cur.execute('INSERT OR REPLACE INTO t4 (matching, update_date, games_cnt, visible_name, size) VALUES (?, ?, ?, ?, ?)', (i, self.d4[i][0], self.d4[i][1], self.d4[i][2], self.size))          
            conn.commit()
            conn.close()
            
            self.d3_full = self.d3.copy()
        except Exception as e:
            self.scrap_status = e
            
    
    def scrap_from_html(self, html, _mode):
        games = re.findall("\(;(.*?)\)", str(html))
        self.scraped_games_cnt = 0
        for game in games:
            print("scrapinggg 1...", len(game))
            position_to_start_searching_for_moves = game.find('SO[http://www.littlegolem.com]')
            _moves = game[position_to_start_searching_for_moves:].partition(';')[2].split(';')
            if len(_moves) <= 5 or len(re.findall('RE\[(.*?)\]', game)) == 0:
                continue    # discard games shorter than 6 moves as well as ongoing games
            print("scrapinggg 2...", len(game))
            size = re.findall("SZ\[(.*?)\]", game)[0]
            if int(size) != self.size:
                continue
            game_id = re.findall("GC\[ game #(.*?)\]", game)[0]
            event = re.findall("EV\[(.*?)\]", game)[0]
            red_player = re.findall("PB\[(.*?)\]", game)[0]
            blue_player = re.findall("PW\[(.*?)\]", game)[0]
            red_won_flg = int(re.findall("RE\[(.*?)\]", game)[0] == "B")
            if game_id in self.d3.keys():
                if _mode not in self.d3[game_id][4]:
                    self.d3[game_id][4].append(_mode)
                continue    # skip the game if it already is in the base
            self.d3[game_id] = [red_player, blue_player, red_won_flg, event, [_mode]]
            _moves_list = []
            mirror_flg = 0
            for n, m in enumerate(_moves):
                move = re.findall('\[(.*?)\]', m)[0]
                if move not in ("resign", "swap"):
                    if n == 0 and ((ord(move[0])-96 + ord(move[1])-96 > (self.size + 1)) or (ord(move[0])-96 + ord(move[1])-96 == (self.size+1) and ord(move[0])-96 <= int(self.size/2))):
                    #if n == 0 and ord(move[0])-96 + ord(move[1])-96 > (self.size + 1):
                        mirror_flg = 1
                        print("MIRRORING", game_id)
                    if mirror_flg == 1:
                        move = chr(abs(ord(move[0])-96 -(self.size + 1))+96) + chr(abs(ord(move[1])-96 -(self.size + 1))+96)
                    move = move[0] + str(ord(move[1]) - 96)
                _moves_list.append(move)
            for n, v in enumerate(_moves_list):
                if n == 0:
                    self.d1[game_id] = {n+1: v}
                else:
                    self.d1[game_id][n+1] = v
                try:
                    self.d2[str(n+1) + " " + v].append(game_id)
                except:
                    self.d2[str(n+1) + " " + v] = [game_id]
            if v != "resign":
                self.d1[game_id][n+2] = "end"
                try:
                    self.d2[str(n+2) + " " + "end"].append(game_id)
                except:
                    self.d2[str(n+2) + " " + "end"] = [game_id]
            self.scraped_games_cnt += 1
            
    
    def load_games_data(self):
        self.d1 = {}
        self.d2 = {}
        self.d3 = {}
        self.d4 = {}
        self.d3_full = {}
        
        conn = sqlite3.connect('hex_fusekipedia_db.sqlite3')
        cur = conn.cursor()
        
        #cur.execute('CREATE TABLE t1 (game_id TEXT, move TEXT, UNIQUE(game_id, move))')
        #cur.execute('CREATE TABLE t2 (game_id TEXT UNIQUE, red_player TEXT, blue_player TEXT, red_won_flg INTEGER, event TEXT, size INTEGER)')
        #cur.execute('CREATE TABLE t3 (game_id TEXT, matching TEXT, UNIQUE(game_id, matching))')
        #cur.execute('CREATE TABLE t4 (matching TEXT, update_date TEXT, games_cnt INTEGER, visible_name TEXT, size INTEGER, UNIQUE(matching, size))')
        
        cur.execute('SELECT a.game_id, a.move FROM t1 a, t2 b WHERE a.game_id = b.game_id AND b.size = ?', (self.size, ))
        data = cur.fetchall()
        for i in data:
            number = int(i[1].split()[0])
            coords = i[1].split()[1]
            try:
                self.d1[i[0]][number] = coords
            except:
                self.d1[i[0]] = {number: coords}
                
        cur.execute('SELECT a.game_id, a.move FROM t1 a, t2 b WHERE a.game_id = b.game_id AND b.size = ?', (self.size, ))
        data = cur.fetchall()
        for i in data:
            try:
                self.d2[i[1]].append(i[0])
            except:
                self.d2[i[1]] = [i[0]]
                
        cur.execute('SELECT a.game_id, a.red_player, a.blue_player, a.red_won_flg, a.event, b.matching FROM t2 a, t3 b WHERE a.game_id = b.game_id AND a.size = ?', (self.size, ))
        data = cur.fetchall()
        for i in data:
            try:
                self.d3[i[0]][4].append(i[5])
                self.d3_full[i[0]][4].append(i[5])
            except:
                self.d3[i[0]] = [i[1], i[2], i[3], i[4], [i[5]]]
                self.d3_full[i[0]] = [i[1], i[2], i[3], i[4], [i[5]]]
                
        cur.execute('SELECT matching, update_date, games_cnt, visible_name FROM t4 WHERE size = ?', (self.size, ))
        data = cur.fetchall()
        for i in data:
            self.d4[i[0]] = [i[1], i[2], i[3]] 
            
        conn.close()
            
    
    def prepare_dicts(self, conditional=False):
        self.load_games_data()
        #self.d1 --> KEY - game id, VALUE - dict of moves (key - move number, value - move coordinates)
        #self.d2 --> KEY - move number || move coordinates, VALUE - list of game ids
        #self.d3 --> KEY - game id, VALUE - [red player, blue player, red won flag, event, [matching], swap_flg (added in v2.4)]
        #self.d4 --> KEY - mode (ie., "championships" or player id), VALUE - [last update date, games cnt, visible name]
        print("PREPARING DICTS FOR", self.mode)
        if conditional and self.tournament_only_checkbutton.get(): # hasattr(self, "tournament_only_checkbutton")
            print("preparting option 1.1")
            list_of_game_ids = [k for k, v in self.d3.items() if self.mode in v[4] and v[3] != "null"]
        else:
            print("preparting option 1.2")
            list_of_game_ids = [k for k, v in self.d3.items() if self.mode in v[4]] #re.match(pattern, v[3])
        if conditional and self.recent_games_entry.get().strip(): # hasattr(self, "recent_games_entry")
            print("preparting option 2")
            list_of_game_ids.sort(key=lambda x: int(x), reverse=True)
            list_of_game_ids = list_of_game_ids[:int(self.recent_games_entry.get().strip())]
        print("LENGTH OF list_of_game_ids:", len(list_of_game_ids))
        set_of_game_ids = set(list_of_game_ids)
        d1 = {}
        d2 = {}
        d3 = {}
        for i in list_of_game_ids:
            d1[i] = self.d1[i]
            d3[i] = self.d3[i] + [0]    # add swap_flg and set it to 0 as for now
        for k, v in self.d2.items():
            if set_of_game_ids & set(v):
                d2[k] = list(set_of_game_ids & set(v))
                
        ### get-rid-of-swap modification (v 2.4)
        d1_new = {}
        d2_new = {}
        games_with_swap = []
        
        # updating d3 (and collecting games where swap occurred)
        for _game in d2["2 swap"]:
            games_with_swap.append(_game)
            # apart from setting swap flag we must do sth with players' names and colors since if we eliminate swap then the original blue player will be red in the application
            d3[_game] = [d3[_game][1], d3[_game][0], int(d3[_game][2]==0), d3[_game][3], d3[_game][4], 1]
        
        # updating d1
        for _game in d1:
            if _game in games_with_swap:
                for _move in d1[_game]:
                    if _move == 1:
                        try:
                            d1_new[_game][_move] = d1[_game][_move]
                        except:
                            d1_new[_game] = {_move: d1[_game][_move]}
                    if _move > 2:
                        _move_after_swap_pre = d1[_game][_move]
                        if _move_after_swap_pre not in ("end", "resign"):
                            _move_after_swap_post = chr(int(_move_after_swap_pre[1:])+96) + str(ord(_move_after_swap_pre[0])-96)
                        else:
                            _move_after_swap_post = _move_after_swap_pre
                        try:
                            d1_new[_game][_move-1] = _move_after_swap_post
                        except:
                            d1_new[_game] = {_move-1: _move_after_swap_post}
            else:
                d1_new[_game] = d1[_game]
        
        # updating d2
        for _game in d1_new:
            for _move in d1_new[_game]:
                _move_full = str(_move) + " " + d1_new[_game][_move]
                try:
                    d2_new[_move_full].append(_game)
                except:
                    d2_new[_move_full] = [_game]
            
        self.d1 = d1_new
        self.d2 = d2_new
        self.d3 = d3
        self.static_moves_history_list = []    # this way everything will be cleared (calling undo_all_moves is not enough)
        self.undo_all_moves()
    
    
    def draw_board(self):
        self.hexes_dict = {}
        adder = self.a
        for i in range(self.rows):
            for j in range(self.columns):
                move_y = i * 1.5 * self.a + adder
                move_x = self.technical_size * j + i * 0.5 * self.a * 3 ** 0.5 + adder
                x0 = int(0.5 * self.a * 3 ** 0.5 + move_x)
                y0 = int(0 + move_y)
                x1 = int(self.a * 3 ** 0.5 + move_x)
                y1 = int(0.5 * self.a + move_y)
                x2 = int(self.a * 3 ** 0.5 + move_x)
                y2 = int(1.5 * self.a + move_y)
                x3 = int(0.5 * self.a * 3 ** 0.5 + move_x)
                y3 = int(2 * self.a + move_y)
                x4 = int(0 + move_x)
                y4 = int(1.5 * self.a + move_y)
                x5 = int(0 + move_x)
                y5 = int(0.5 * self.a + move_y)
                self.canvas.create_line(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x0, y0, tags="hex")
                self.hexes_dict[chr(j+1+96)+str(i+1)] = [x0, y1+0.5*self.a]    # we save the coordinates of hexes centers for later use
                
        # add board coordinates
        x_start_pos = 0.5 * 0.5 * self.a * 3 ** 0.5 + adder
        for i in range(self.columns):
            letter = chr(i + 65)
            x = x_start_pos + i * self.a * 3 ** 0.5
            self.canvas.create_text(x, 10, text = letter)    # 10 is arbitrary
        x_start_pos = 10    # arbitrary
        y_start_pos = self.a + adder
        for i in range(self.rows):
            x = x_start_pos + i * 0.5 * self.a * 3 ** 0.5
            y = y_start_pos + i * self.a * 1.5
            self.canvas.create_text(x, y, text = i+1, anchor = "e")    # from tkinter import font /// font = font.Font(weight="bold")
                
        # color top border red
        x_pre = 0 + adder
        y_pre = 0.5 * self.a + adder
        for i in range(self.columns*2-1):    # we substract 1 in order to make the last line red only in half its length
            x_post = x_pre + int(0.5 * self.a * (3 ** 0.5))
            if y_pre == 0.5 * self.a + adder:
                y_post = adder
            else:
                y_post = 0.5 * self.a + adder
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color1)
            x_pre = x_post
            y_pre = y_post
        # make the last line red only in half its length
        x_post = x_pre + int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = 0.5 * self.a * 0.5 + adder
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color1)
        
        # color bottom border red (we make use of previously created variables x2, y2 --> we draw from the end, i.e., from bottom right)
        x_pre = x2
        y_pre = y2
        for i in range(self.columns*2 - 1):    # we substract 1 in order to make the last line red only in half its length
            x_post = x_pre - int(0.5 * self.a * (3 ** 0.5))
            if y_pre == y2:
                y_post = y_pre + 0.5 * self.a
            else:
                y_post = y_pre - 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color1)
            x_pre = x_post
            y_pre = y_post
        # make the last line red only in half its length
        x_post = x_pre - int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre - 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color1)
        
        # color left border blue
        x_pre = 0 + adder
        y_pre = 0.5 * self.a + adder
        for i in range(self.rows*2 - 1):    # we substract 1 in order to make the last line blue only in half its length
            x_post = x_pre + (i % 2 != 0) * int(0.5 * self.a * (3 ** 0.5))
            y_post = y_pre + 0.5 * self.a + (i % 2 == 0) * 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color2)
            x_pre = x_post
            y_pre = y_post
        # make the last line blue only in half its length
        x_post = x_pre + int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre + 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color2)
            
        # color right border blue (we make use of previously created variables x2, y2 --> we draw from the end, i.e., from bottom right)
        x_pre = x2
        y_pre = y2
        for i in range(self.rows*2 - 1):    # we substract 1 in order to make the last line blue only in half its length
            x_post = x_pre - (i % 2 != 0) * int(0.5 * self.a * (3 ** 0.5))
            y_post = y_pre - 0.5 * self.a - (i % 2 == 0) * 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color2)
            x_pre = x_post
            y_pre = y_post
        # make the last line blue only in half its length
        x_post = x_pre - int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre - 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill=self.color2)
        
        # make technical (empty) ovals in order to show coordinates while mouse on them
        for i in self.hexes_dict:
            _x0 = self.hexes_dict[i][0] - 0.8*self.a
            _y0 = self.hexes_dict[i][1] - 0.8*self.a
            _x1 = self.hexes_dict[i][0] + 0.8*self.a - 1
            _y1 = self.hexes_dict[i][1] + 0.8*self.a - 1
            self.canvas.create_oval(_x0, _y0, _x1, _y1, width=0, tags="technical_"+i)
            self.canvas.tag_bind("technical_"+i, "<Enter>", lambda event, _arg=i: self.show_coordinates(event, _arg))    
            self.canvas.tag_bind("technical_"+i, "<Leave>", self.hide_coordinates)
            
    
    def arrange_next_moves(self, only_technical=False):
        player = self.color1 if self.move_number % 2 != 0 else self.color2
        
        # we unbind the tags associated with previous moves so that already placed stones cannot be clicked (does not apply to the first move)
        for n, move in enumerate(self.moves_list):
            self.canvas.tag_unbind(move[0], "<Button-1>")
        
        print("GAMES WITH THE MOVE 1:", self.games_in_question)
        self.dynamic_games_history_list.append(self.games_in_question)
        self.static_games_history_list.append(self.games_in_question)
        print("DYNAMIC GAMES HISTORY:", self.dynamic_games_history_list)
        moves_list = []
        
        # for the first move do this
        if self.move_number == 1:
            for _move in self.d2:
                if _move.partition(" ")[0] == "1":
                    wins_cnt = 0
                    games_cnt = 0
                    for _game in self.d2[_move]:
                        if self.d3[_game][2] == 1:
                            wins_cnt += 1
                        games_cnt += 1
                    
                    # addition (for the part "win ratio if swapped")
                    # can (should?) be integrated into the loop above
                    # as for now, left here for clarity
                    #swapped_wins_cnt = 0
                    #swapped_games_cnt = 0
                    #for _game in self.d2[_move]:
                        #if self.d1[_game][2] == 'swap':
                            #if self.d3[_game][2] == 1:
                                #swapped_wins_cnt += 1
                            #swapped_games_cnt += 1
                    #moves_list.append([_move.partition(" ")[2], wins_cnt, games_cnt, swapped_wins_cnt, swapped_games_cnt])
                    moves_list.append([_move.partition(" ")[2], wins_cnt, games_cnt])
                    
        # for further moves do this
        else:
            if len(self.games_in_question) == 0:    # for (only?) second move we do this
                self.games_in_question = self.d2[self.played_move]
            else:
                #self.games_in_question = [i for i in self.d2[self.played_move] if i in self.games_in_question]
            
            
                red_moves = []
                blue_moves = []
                for i in self.dynamic_moves_history_list:
                    if int(i.partition(" ")[0]) % 2:
                        red_moves.append(i.partition(" ")[2])
                    else:
                        blue_moves.append(i.partition(" ")[2])
                        
                matching_games = []
                for _game in self.d1:
                    is_ok = True
                    for i in range(1, self.move_number):
                        if i % 2:
                            if self.d1[_game][i] not in red_moves:
                                is_ok = False
                                break
                        else:
                            if self.d1[_game][i] not in blue_moves:
                                is_ok = False
                                break
                    if is_ok:
                        matching_games.append(_game)
                        
                self.games_in_question = matching_games
                        
                
            next_moves_set = set()
            for i in self.games_in_question:
                next_moves_set.add(str(self.move_number) + " " + self.d1[i][self.move_number])
            print("NEXT MOVE SET:", next_moves_set)
            for _move in next_moves_set:
                wins_cnt = 0
                games_cnt = 0
                for _game in self.d2[_move]:
                    if _game in self.games_in_question:
                        if player == self.color1 and self.d3[_game][2] == 1 or player == self.color2 and self.d3[_game][2] == 0:
                            wins_cnt += 1
                        games_cnt += 1
                moves_list.append([_move.partition(" ")[2], wins_cnt, games_cnt])
          
        if only_technical == True:    # this is the case when button ">>" is pressed (--> we dont need buttons, labels etc. for every intermediary move)
            return
            
        for child in self.moves_frame.winfo_children():
            child.destroy()
        for child in self.info_frame.winfo_children():
            child.destroy()
        for child in self.position_info.winfo_children():
            child.destroy()
        
        print("GAMES WITH THE MOVE 2:", self.games_in_question)     
        print(moves_list)
        moves_list.sort(key=lambda x: x[0], reverse=True)
        moves_list.sort(key=lambda x: x[1], reverse=True)
        moves_list.sort(key=lambda x: x[2], reverse=True)
        self.moves_list = moves_list    # will be handy for unbinding tags for oval canvas objects
        
        # info labels
        tk.Label(self.info_frame, text="Move number: "+str(self.move_number)).pack(side="left", anchor="w", padx=2, pady=2)
        tk.Label(self.info_frame, text=player.capitalize(), fg=player).pack(side="right", anchor="e", pady=2)
        tk.Label(self.info_frame, text="Player:").pack(side="right", anchor="e", pady=2)
        
        # headers
        tk.Label(self.moves_frame, text="Move").grid(row=0, column=0, padx=2, pady=2)
        tk.Label(self.moves_frame, text="Games").grid(row=0, column=1, padx=2, pady=2) #Number of games / Games / #
        tk.Label(self.moves_frame, text="Win ratio").grid(row=0, column=2, padx=2, pady=2) #Winnings percentage / Result / Red(Blue) Win
        #if self.move_number == 1:
            #tk.Label(self.moves_frame, text="Win ratio\nif swapped").grid(row=0, column=3, padx=1, pady=1)
            
        # content
        self.canvas.delete("phantom")
        self.canvas.delete("highlight")
        self.canvas.delete("coordinates")
        for n, move in enumerate(moves_list):
            if move[0] == "swap":
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", command=self.swap_a_move)
            elif move[0] in ("resign", "end"):
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", state=tk.DISABLED)
            else:
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", command = lambda _arg=move[0]: self.make_a_move(_arg))
                if len(moves_list) > 1:    # highlighting only makes sense with more than one move to highlight
                    self.move_button.bind("<Enter>", lambda event, _arg=move[0]: self.highlight_next_move(_arg))
                    self.move_button.bind("<Leave>", self.unhighlight_next_move)
            self.move_button.grid(row=n+1, column=0, sticky='we', padx=2, pady=2)
            _label1 = tk.Label(self.moves_frame, text=str(move[2]))
            _label1.grid(row=n+1, column=1, padx=2, pady=2)
            _label2 = tk.Label(self.moves_frame, text=str(round(move[1]/move[2]*100)) + "%")
            _label2.grid(row=n+1, column=2, padx=2, pady=2)
            if move[0] not in ("swap", "resign", "end") and len(moves_list) > 1:    # highlighting only makes sense with more than one move to highlight
                _label1.bind("<Enter>", lambda event, _arg=move[0]: self.highlight_next_move(_arg))
                _label1.bind("<Leave>", self.unhighlight_next_move)
                _label2.bind("<Enter>", lambda event, _arg=move[0]: self.highlight_next_move(_arg))
                _label2.bind("<Leave>", self.unhighlight_next_move)
            #if self.move_number == 1:
                #_label3 = tk.Label(self.moves_frame, text="-" if move[4] == 0 else str(round(move[3]/move[4]*100))+"%")
                #_label3.grid(row=n+1, column=3, padx=1, pady=1)
                #_label3.bind("<Enter>", lambda event, _arg=move[0]: self.highlight_next_move(_arg))
                #_label3.bind("<Leave>", self.unhighlight_next_move)

            # highlight (phantom) next moves
            if move[0] not in ("swap", "resign", "end") and len(moves_list) > 1:    # highlighting (phantoms) only makes sense with more than one move to highlight (phantom)
                _x0 = self.hexes_dict[move[0]][0] - 0.6*self.a
                _y0 = self.hexes_dict[move[0]][1] - 0.6*self.a
                _x1 = self.hexes_dict[move[0]][0] + 0.6*self.a - 1
                _y1 = self.hexes_dict[move[0]][1] + 0.6*self.a - 1
                if player == self.color1:
                    color = "RosyBrown1"
                else:
                    color = "light blue"
                self.canvas.create_oval(_x0, _y0, _x1, _y1, fill=color, width=0, tags=("phantom", move[0]))
                self.canvas.tag_bind(move[0], "<Button-1>", lambda event, _arg=move[0]: self.make_a_move(_arg))    # makes ovals (with phantoms) clickable
                self.canvas.tag_bind(move[0], "<Enter>", lambda event, _arg=move[0]: self.show_coordinates(event, _arg))    # makes ovals (with phantoms) show coordinates and hand cursor while mouse on
                self.canvas.tag_bind(move[0], "<Leave>", self.hide_coordinates)
        self.canvas.tag_bind("phantom", "<Enter>", self.show_hand_cursor)
        self.canvas.tag_bind("phantom", "<Leave>", self.show_normal_cursor)
        self.canvas.tag_bind("phantom", "<Button-1>", self.show_normal_cursor)
            
        if len(self.static_moves_history_list) < self.move_number:
            self.next_button.config(state="disabled")
            self.next_next_button.config(state="disabled")
        
        # scrollbar stuff
        print("SCROLLBAR POSITION", self.scrollbar.get())
        self.moves_canvas.yview_moveto(0.0)
        self.scrollbar.set(0.0, 0.0)
        if len(moves_list) < 9:
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side="right", fill="y", expand=False)        
        
        # position info labelframe
        if self.move_number == 1:
            _text = str(len(self.d1)) + " games in this branch."
        elif len(self.games_in_question) == 1:
            _game = self.games_in_question[0]
            _text = "Game " + _game + " between " + self.d3[_game][0] + " (red) and " + self.d3[_game][1] + " (blue) (tournament " + self.d3[_game][3] + "), won by " + (self.d3[_game][0] if self.d3[_game][2] == 1 else self.d3[_game][1]) + "."
        else:
            _text = str(len(self.games_in_question)) + " games in this branch."
        text_position_info = tk.Text(self.position_info, height=6, width=25, wrap=tk.WORD)
        text_position_info.insert(tk.INSERT, _text)
        text_position_info.pack()
        if len(self.games_in_question) == 1:
            text_position_info.tag_add("game_id_tag", "1.5", "1.{}".format(5+len(self.games_in_question[0])))
            text_position_info.tag_config("game_id_tag", foreground="blue", underline=1)
            text_position_info.tag_bind("game_id_tag", "<Enter>", self.show_hand_cursor)
            text_position_info.tag_bind("game_id_tag", "<Leave>", self.show_normal_cursor)
            text_position_info.tag_bind("game_id_tag", "<Button-1>", lambda event, url=r"http://littlegolem.net/jsp/game/game.jsp?gid="+_game: webbrowser.open_new(url))
        
        # mark the last move
        self.canvas.delete("last_move_mark")
        if self.move_number > 1:
            if self.played_move != "2 swap":
                last_move = self.played_move.partition(" ")[2]
            else:
                pre_swap_move = self.dynamic_moves_history_list[-2].partition(" ")[2]
                last_move = chr(int(pre_swap_move[1:])+96) + str(ord(pre_swap_move[0])-96)
            self.canvas.create_text(self.hexes_dict[last_move][0], self.hexes_dict[last_move][1], text="+", font = font.Font(weight="bold", size=16), tags="last_move_mark")
        
        print("MOVE NUMBER:", self.move_number)
        print("")
        
        
    def highlight_next_move(self, move):
        _x0 = self.hexes_dict[move][0] - 0.6*self.a
        _y0 = self.hexes_dict[move][1] - 0.6*self.a
        _x1 = self.hexes_dict[move][0] + 0.6*self.a - 1
        _y1 = self.hexes_dict[move][1] + 0.6*self.a - 1
        self.canvas.create_oval(_x0, _y0, _x1, _y1, width=2, tags=("highlight"))
        
        
    def unhighlight_next_move(self, event):
        self.canvas.delete("highlight")
    
    
    def make_a_move(self, move, swap=False, next_next=False):
        player = self.color1 if self.move_number % 2 != 0 else self.color2
        self.prev_button.config(state="normal") #self.prev_button["state"] = "normal"
        self.prev_prev_button.config(state="normal")
        oval_x0 = self.hexes_dict[move][0] - 0.6*self.a
        oval_y0 = self.hexes_dict[move][1] - 0.6*self.a
        oval_x1 = self.hexes_dict[move][0] + 0.6*self.a - 1
        oval_y1 = self.hexes_dict[move][1] + 0.6*self.a - 1
        self.canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1, fill=player, width=0, tags=("played_moves", move))
        if not swap:
            self.played_move = str(self.move_number) + " " + move
        else:
            self.played_move = "2 swap"
        print("PLAYED MOVE:", self.played_move)
        if self.played_move not in self.static_moves_history_list:
            if int(self.played_move.partition(" ")[0]) <= len(self.static_moves_history_list):
                print("CONDITION FULFILLED")
                self.static_moves_history_list = self.static_moves_history_list[:self.move_number-1]
            self.static_moves_history_list.append(self.played_move)
        self.dynamic_moves_history_list.append(self.played_move)
        self.move_number += 1
        self.arrange_next_moves(only_technical=next_next)
        
        
    def swap_a_move(self):
        last_move_played = self.played_move.partition(" ")[2]
        self.canvas.delete(last_move_played)    # we make use of the tag "move" (a few lines above)
        new_move = chr(int(last_move_played[1:])+96) + str(ord(last_move_played[0])-96)
        self.make_a_move(new_move, swap=True)
        
        
    def undo_a_move(self):
        if self.move_number > 1:    # although PREV buttons are disabled, the user can undo by clicking RMB or "p" key
            print("\nPREV\n")
            self.canvas.delete("highlight")
            print("DYNAMIC MOVES HISTORY: ", self.dynamic_moves_history_list)
            self.next_button.config(state="normal")
            self.next_next_button.config(state="normal")
            print("PLAYED MOVE 0:", self.played_move)
            if self.played_move != "2 swap":
                self.canvas.delete(self.dynamic_moves_history_list.pop().partition(" ")[2])
            else:
                self.dynamic_moves_history_list.pop()
                _post_swap_move = self.dynamic_moves_history_list[-1].partition(" ")[2]
                _pre_swap_move = chr(int(_post_swap_move[1:])+96) + str(ord(_post_swap_move[0])-96)
                self.canvas.delete(_pre_swap_move)
                oval_x0 = self.hexes_dict[_post_swap_move][0] - 0.6*self.a
                oval_y0 = self.hexes_dict[_post_swap_move][1] - 0.6*self.a
                oval_x1 = self.hexes_dict[_post_swap_move][0] + 0.6*self.a - 1
                oval_y1 = self.hexes_dict[_post_swap_move][1] + 0.6*self.a - 1
                self.canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1, fill=self.color1, width=0, tags=("played_moves", _post_swap_move))
            print("GAMES IN QUESTION 1:", self.games_in_question)
            self.games_in_question = self.dynamic_games_history_list.pop()
            self.games_in_question = self.dynamic_games_history_list.pop()
            print("GAMES IN QUESTION 2:", self.games_in_question)
            print("PLAYED MOVE 1:", self.played_move)
            try:
                self.played_move = self.dynamic_moves_history_list[-1]
            except:
                pass #self.played_move = None
            print("PLAYED MOVE 2:", self.played_move)
            self.move_number -= 1
            if self.move_number == 1:
                self.prev_button.config(state="disabled")
                self.prev_prev_button.config(state="disabled")
            self.arrange_next_moves()
        
        
    def undo_all_moves(self):
        #if self.prev_prev_button["state"] == "normal":    # although the << button is normally disabled, the user invoke it by clicking the "f" key
        print("\nPREV PREV\n")
        self.canvas.delete("highlight")
        self.next_button.config(state="normal")
        self.next_next_button.config(state="normal")
        self.prev_button.config(state="disabled")
        self.prev_prev_button.config(state="disabled")
        self.canvas.delete("played_moves")
        self.move_number = 1
        self.games_in_question = []
        self.dynamic_games_history_list = []
        self.dynamic_moves_history_list = []
        self.arrange_next_moves()
        

    def play_the_next_move(self):
        if self.next_button["state"] == "normal":    # although the > button is normally disabled, the user invoke it by clicking the "n" key
            print("\nNEXT\n")
            print("STATIC MOVES HISTORY:", self.static_moves_history_list)
            next_move = self.static_moves_history_list[self.move_number-1].partition(" ")[2]
            print("NEXT MOVE:", next_move)
            if next_move != "swap":
                self.make_a_move(next_move)
            else:
                self.swap_a_move()
    
    
    def play_all_next_moves(self):
        if self.next_next_button["state"] == "normal":    # although the >> button is normally disabled, the user invoke it by clicking the "l" key
            print("\nNEXT NEXT\n")
            print("STATIC MOVES HISTORY:", self.static_moves_history_list)
            print("MOVES TO BE PLAYED:", self.static_moves_history_list[self.move_number-1:])
            for _move_pre in self.static_moves_history_list[self.move_number-1:-1]:
                _move = _move_pre.partition(" ")[2]
                if _move != "swap":
                    self.make_a_move(_move, next_next=True)
                else:
                    self.swap_a_move()
            next_move = self.static_moves_history_list[-1].partition(" ")[2]
            if next_move != "swap":
                self.make_a_move(next_move)
            else:
                self.swap_a_move()
        
        
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title('Hex Fusekipedia')
    app = Hex_Fusekipedia(root)
    root.mainloop()
