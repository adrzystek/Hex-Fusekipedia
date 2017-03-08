# -*- coding: utf-8 -*-
"""
@author: adrzystek
"""


import urllib.request
import re
import tkinter as tk
import pickle
import webbrowser
from tkinter import font


class Hex_Fusekipedia(tk.Frame):
    
    def __init__(self, parent, rows=13, columns=13, size=48, color1="red", color2="blue"):
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.a = self.size / (3**0.5)
        self.hexes_dict = {}
        self.games_in_question = []
        self.move_number = 1
        self.static_moves_history_list = []
        self.dynamic_moves_history_list = []
        self.static_games_history_list = []
        self.dynamic_games_history_list = []
        self.TEST = False
        self.scrap = False
        
        self.main_frame = tk.Frame(parent)
        self.main_frame.pack()
        self.canvas = tk.Canvas(self.main_frame, borderwidth=0, highlightthickness=0, background="white",
                                width = self.a * (3 ** 0.5) * (self.columns + 0.5 * (self.rows - 1)) + self.a * (3 ** 0.5),
                                height = 2 * self.a * (self.rows // 2 + 1) + self.a * (self.rows // 2) + 2 * self.a)
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        if self.TEST:
            self.right_side_frame = tk.Frame(self.main_frame, bg="yellow")
            self.right_side_frame_top = tk.Frame(self.right_side_frame, bg="grey")
            self.right_side_frame_bottom = tk.Frame(self.right_side_frame, bg="red")
            self.control_frame = tk.Frame(self.right_side_frame_top, bg="cyan")
            self.info_frame = tk.Frame(self.right_side_frame_top, bg="tan")
            self.frame_for_canvas = tk.Frame(self.right_side_frame_top, bg="blue")
            self.moves_canvas = tk.Canvas(self.frame_for_canvas, width=1, height=300, bg="gold")    # height=300 - just proper for 48 size
            self.scrollbar = tk.Scrollbar(self.frame_for_canvas, orient="vertical", command=self.moves_canvas.yview)    # parent=self.moves_canvas possibly?
            self.moves_frame = tk.Frame(self.moves_canvas, bg="white")
            self.curiosity_frame = tk.LabelFrame(self.right_side_frame_bottom, text="Position info", bg="green")
        else:
            self.right_side_frame = tk.Frame(self.main_frame)
            self.right_side_frame_top = tk.Frame(self.right_side_frame)
            self.right_side_frame_bottom = tk.Frame(self.right_side_frame)
            self.control_frame = tk.Frame(self.right_side_frame_top)
            self.info_frame = tk.Frame(self.right_side_frame_top)
            self.frame_for_canvas = tk.Frame(self.right_side_frame_top)
            self.moves_canvas = tk.Canvas(self.frame_for_canvas, width=1, height=300)    # height=300 - just proper for 48 size
            self.scrollbar = tk.Scrollbar(self.frame_for_canvas, orient="vertical", command=self.moves_canvas.yview)    # parent=self.moves_canvas possibly?
            self.moves_frame = tk.Frame(self.moves_canvas)
            self.curiosity_frame = tk.LabelFrame(self.right_side_frame_bottom, text="Position info")
            
        self.right_side_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        self.right_side_frame_top.pack(side="top", fill="both", padx=10, pady=10, anchor="n")
        self.right_side_frame_bottom.pack(side="bottom", expand=True, fill="both", padx=10, pady=10, anchor="s")        
        self.control_frame.pack(side="top", expand=True, fill="x", padx=10, pady=10, anchor="n")
        self.info_frame.pack(side="top", expand=True, fill="x", pady=10, anchor="n")
        self.frame_for_canvas.pack(side="top", expand=True, fill="x", pady=(10,0), anchor="n")
        self.moves_canvas.pack(side="left", expand=True, fill="both", anchor="n")
        self.curiosity_frame.pack(side="bottom", pady=10, anchor="s")
        
        self.canvas_frame = self.moves_canvas.create_window((0,0), window=self.moves_frame, anchor='nw') 
        
        self.moves_canvas.config(yscrollcommand=self.scrollbar.set)
        
        self.moves_frame.bind("<Configure>", self.onFrameConfigure)
        self.moves_canvas.bind('<Configure>', self.set_canvas_width)
        #self.frame_for_canvas.bind('<Configure>', self.configure_window)    # unused but possible (see below)
        self.frame_for_canvas.bind('<Enter>', self.bound_to_mousewheel)
        self.frame_for_canvas.bind('<Leave>', self.unbound_to_mousewheel)
                
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
        
        if self.scrap == True:
            self.scrap_games_data()
        else:
            self.load_games_data()
            
        self.arrange_next_moves()
        
    
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
        
    
    def scrap_games_data(self):
        import time
        
        self.d1 = {}    # KEY - game id, VALUE - dict of moves (key - move number, value - move coordinates)
        self.d2 = {}    # KEY - move number || move coordinates, VALUE - list of game ids
        self.d4 = {}    # KEY - game id, VALUE - [red player, blue player, red won flag, tournament, ligue]
        
        for tournament_number in range(1, 39):
            for ligue in [1, 2]:
                
                tournament_name = "ch.{}.{}.1".format(tournament_number, ligue)
                tournament_url = "http://littlegolem.net/jsp/tournament/tournament.jsp?trnid=hex." + tournament_name
                tournament_html = urllib.request.urlopen(tournament_url).read().decode('utf-8')
                pgn_sgf_url = "http://littlegolem.net" + re.findall('href="(.*?)">PGN/SGF', str(tournament_html))[0]
                html = urllib.request.urlopen(pgn_sgf_url).read()
                
                games = re.findall("\(;(.*?)\)", str(html))
                for game in games:
                    position_to_start_searching_for_moves = game.find('SO[http://www.littlegolem.com]')
                    _moves = game[position_to_start_searching_for_moves:].partition(';')[2].split(';')
                    if len(_moves) <= 5:
                        continue
                    game_id = re.findall("GC\[ game #(.*?)\]", game)[0]
                    red_player = re.findall("PB\[(.*?)\]", game)[0]
                    blue_player = re.findall("PW\[(.*?)\]", game)[0]
                    red_won_flg = int(re.findall("RE\[(.*?)\]", game)[0] == "B")
                    self.d4[game_id] = [red_player, blue_player, red_won_flg, tournament_name]
                    _moves_list = []
                    mirror_flg = 0
                    for n, m in enumerate(_moves):
                        move = re.findall('\[(.*?)\]', m)[0]
                        if move not in ("resign", "swap"):
                            if n == 0 and ord(move[0])-96 + ord(move[1])-96 > 14:
                                mirror_flg = 1
                                print("MIRRORING", game_id)
                            if mirror_flg == 1:
                                move = chr(abs(ord(move[0])-96 -14)+96) + chr(abs(ord(move[1])-96 -14)+96)
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
        
                print("TOURNAMENT NAME:", tournament_name)                    
                time.sleep(1)
            time.sleep(3)
            
    
    def load_games_data(self):
        with open("d1.txt", "rb") as f:
            self.d1 = pickle.load(f)
        with open("d2.txt", "rb") as f:
            self.d2 = pickle.load(f)
        with open("d4.txt", "rb") as f:
            self.d4 = pickle.load(f)    
    
    
    def draw_board(self):
        adder = self.a
        for i in range(self.rows):
            for j in range(self.columns):
                move_y = i * 1.5 * self.a + adder
                move_x = self.size * j + i * 0.5 * self.a * 3 ** 0.5 + adder
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
            self.canvas.create_text(x, y, text = i+1, anchor = 'e')    # from tkinter import font /// font = font.Font(weight="bold")
                
        # color top border red
        x_pre = 0 + adder
        y_pre = 0.5 * self.a + adder
        for i in range(self.columns*2-1):    # we substract 1 in order to make the last line red only in half its length
            x_post = x_pre + int(0.5 * self.a * (3 ** 0.5))
            if y_pre == 0.5 * self.a + adder:
                y_post = adder
            else:
                y_post = 0.5 * self.a + adder
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="red")
            x_pre = x_post
            y_pre = y_post
        # make the last line red only in half its length
        x_post = x_pre + int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = 0.5 * self.a * 0.5 + adder
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="red")
        
        # color bottom border red (we make use of previously created variables x2, y2 --> we draw from the end, i.e., from bottom right)
        x_pre = x2
        y_pre = y2
        for i in range(self.columns*2 - 1):    # we substract 1 in order to make the last line red only in half its length
            x_post = x_pre - int(0.5 * self.a * (3 ** 0.5))
            if y_pre == y2:
                y_post = y_pre + 0.5 * self.a
            else:
                y_post = y_pre - 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="red")
            x_pre = x_post
            y_pre = y_post
        # make the last line red only in half its length
        x_post = x_pre - int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre - 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="red")
        
        # color left border blue
        x_pre = 0 + adder
        y_pre = 0.5 * self.a + adder
        for i in range(self.rows*2 - 1):    # we substract 1 in order to make the last line blue only in half its length
            x_post = x_pre + (i % 2 != 0) * int(0.5 * self.a * (3 ** 0.5))
            y_post = y_pre + 0.5 * self.a + (i % 2 == 0) * 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="blue")
            x_pre = x_post
            y_pre = y_post
        # make the last line blue only in half its length
        x_post = x_pre + int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre + 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="blue")
            
        # color right border blue (we make use of previously created variables x2, y2 --> we draw from the end, i.e., from bottom right)
        x_pre = x2
        y_pre = y2
        for i in range(self.rows*2 - 1):    # we substract 1 in order to make the last line blue only in half its length
            x_post = x_pre - (i % 2 != 0) * int(0.5 * self.a * (3 ** 0.5))
            y_post = y_pre - 0.5 * self.a - (i % 2 == 0) * 0.5 * self.a
            self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="blue")
            x_pre = x_post
            y_pre = y_post
        # make the last line blue only in half its length
        x_post = x_pre - int(0.5 * self.a * (3 ** 0.5)) * 0.5
        y_post = y_pre - 0.5 * self.a * 0.5
        self.canvas.create_line(x_pre, y_pre, x_post, y_post, width=3, fill="blue")
        
    
    def arrange_next_moves(self, only_technical=False):
        player = "red" if self.move_number % 2 != 0 else "blue"
        
        self.dynamic_games_history_list.append(self.games_in_question)
        self.static_games_history_list.append(self.games_in_question)
        moves_list = []
        
        # for the first move do this
        if self.move_number == 1:
            for _move in self.d2:
                if _move.partition(" ")[0] == "1":
                    wins_cnt = 0
                    games_cnt = 0
                    for _game in self.d2[_move]:
                        if self.d4[_game][2] == 1:
                            wins_cnt += 1
                        games_cnt += 1
                    
                    # addition (for the part "win ratio if swapped")
                    # can (should?) be integrated into the loop above
                    # as for now, left here for clarity
                    swapped_wins_cnt = 0
                    swapped_games_cnt = 0
                    for _game in self.d2[_move]:
                        if self.d1[_game][2] == 'swap':
                            if self.d4[_game][2] == 1:
                                swapped_wins_cnt += 1
                            swapped_games_cnt += 1
                    moves_list.append([_move.partition(" ")[2], wins_cnt, games_cnt, swapped_wins_cnt, swapped_games_cnt])
                        
                    
        # for further moves do this
        else:
            if len(self.games_in_question) == 0:    # for (only?) second move we do this
                self.games_in_question = self.d2[self.played_move]
            else:
                self.games_in_question = [i for i in self.d2[self.played_move] if i in self.games_in_question]
            next_moves_set = set()
            for i in self.games_in_question:
                next_moves_set.add(str(self.move_number) + " " + self.d1[i][self.move_number])
            for _move in next_moves_set:
                wins_cnt = 0
                games_cnt = 0
                for _game in self.d2[_move]:
                    if _game in self.games_in_question:
                        if player =="red" and self.d4[_game][2] == 1 or player == "blue" and self.d4[_game][2] == 0:
                            wins_cnt += 1
                        games_cnt += 1
                moves_list.append([_move.partition(' ')[2], wins_cnt, games_cnt])
          
        if only_technical == True:    # this is the case when button ">>" is pressed (--> we dont need buttons, labels etc. for every intermediary move)
            return
            
        for child in self.moves_frame.winfo_children():
            child.destroy()
        for child in self.info_frame.winfo_children():
            child.destroy()
        for child in self.curiosity_frame.winfo_children():
            child.destroy()
        
        moves_list.sort(key=lambda x: x[0], reverse=True)
        moves_list.sort(key=lambda x: x[1], reverse=True)
        moves_list.sort(key=lambda x: x[2], reverse=True)
        
        # info labels
        tk.Label(self.info_frame, text="Move number: "+str(self.move_number)).pack(side="left", anchor="w", padx=2, pady=2)
        tk.Label(self.info_frame, text=player.capitalize(), fg=player).pack(side="right", anchor="e", pady=2)
        tk.Label(self.info_frame, text="Player:").pack(side="right", anchor="e", pady=2)
        
        # headers
        tk.Label(self.moves_frame, text="Move").grid(row=0, column=0, padx=2, pady=2)
        tk.Label(self.moves_frame, text="Games").grid(row=0, column=1, padx=2, pady=2) #Number of games / Games / #
        tk.Label(self.moves_frame, text="Win ratio").grid(row=0, column=2, padx=2, pady=2) #Winnings percentage / Result / Red(Blue) Win
        if self.move_number == 1:
            tk.Label(self.moves_frame, text="Win ratio\nif swapped").grid(row=0, column=3, padx=1, pady=1)
            
        # content
        for n, move in enumerate(moves_list):
            if move[0] == "swap":
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", command=self.swap_a_move)
            elif move[0] in ("resign", "end"):
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", state=tk.DISABLED)
            else:
                self.move_button = tk.Button(self.moves_frame, text=move[0], relief="groove", command = lambda arg1=move[0] : self.make_a_move(arg1))
            self.move_button.grid(row=n+1, column=0, sticky='we', padx=2, pady=2)
            tk.Label(self.moves_frame, text=str(move[2])).grid(row=n+1, column=1, padx=2, pady=2) #.pack(side="top", fill="both", padx=2, pady=2)
            tk.Label(self.moves_frame, text=str(round(move[1]/move[2]*100)) + "%").grid(row=n+1, column=2, padx=2, pady=2)
            if self.move_number == 1:
                tk.Label(self.moves_frame, text="-" if move[4] == 0 else str(round(move[3]/move[4]*100))+"%").grid(row=n+1, column=3, padx=1, pady=1)
        
        if len(self.static_moves_history_list) < self.move_number:
            self.next_button.config(state="disabled")
            self.next_next_button.config(state="disabled")
        
        # scrollbar stuff
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
            _text = "Game " + _game + " between " + self.d4[_game][0] + " (red) and " + self.d4[_game][1] + " (blue) (tournament " + self.d4[_game][3] + "), won by " + (self.d4[_game][0] if self.d4[_game][2] == 1 else self.d4[_game][1]) + "."
        else:
            _text = str(len(self.games_in_question)) + " games in this branch."
        text_position_info = tk.Text(self.curiosity_frame, height=5, width=25, wrap=tk.WORD)
        text_position_info.insert(tk.INSERT, _text)
        text_position_info.pack()
        if len(self.games_in_question) == 1:
            text_position_info.tag_add("game_id_tag", "1.5", "1.{}".format(5+len(self.games_in_question[0])))
            text_position_info.tag_config("game_id_tag", foreground="blue", underline=1)
            text_position_info.tag_bind("game_id_tag", "<Enter>", self.show_hand_cursor)
            text_position_info.tag_bind("game_id_tag", "<Leave>", self.show_normal_cursor)
            text_position_info.tag_bind("game_id_tag", "<Button-1>", lambda e, url=r"http://littlegolem.net/jsp/game/game.jsp?gid="+_game: webbrowser.open_new(url))
        
        # mark the last move
        self.canvas.delete("last_move_mark")
        if self.move_number > 1:
            if self.played_move != "2 swap":
                last_move = self.played_move.partition(" ")[2]
            else:
                pre_swap_move = self.dynamic_moves_history_list[-2].partition(" ")[2]
                last_move = chr(int(pre_swap_move[1:])+96) + str(ord(pre_swap_move[0])-96)
            self.canvas.create_text(self.hexes_dict[last_move][0], self.hexes_dict[last_move][1], text="+", font = font.Font(weight="bold", size=16), tags="last_move_mark")
        
    
    def make_a_move(self, move, swap=False, next_next=False):
        player = "red" if self.move_number % 2 != 0 else "blue"
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
        if self.played_move not in self.static_moves_history_list:
            if int(self.played_move.partition(" ")[0]) <= len(self.static_moves_history_list):
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
        self.next_button.config(state="normal")
        self.next_next_button.config(state="normal")
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
            self.canvas.create_oval(oval_x0, oval_y0, oval_x1, oval_y1, fill="red", width=0, tags=("played_moves", _post_swap_move))
        self.games_in_question = self.dynamic_games_history_list.pop()
        self.games_in_question = self.dynamic_games_history_list.pop()
        try:
            self.played_move = self.dynamic_moves_history_list[-1]
        except:
            pass
        self.move_number -= 1
        if self.move_number == 1:
            self.prev_button.config(state="disabled")
            self.prev_prev_button.config(state="disabled")
        self.arrange_next_moves()
        
        
    def undo_all_moves(self):
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
        next_move = self.static_moves_history_list[self.move_number-1].partition(" ")[2]
        if next_move != "swap":
            self.make_a_move(next_move)
        else:
            self.swap_a_move()
    
    
    def play_all_next_moves(self):
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
