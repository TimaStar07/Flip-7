import tkinter as tk
from tkinter import ttk, messagebox
import random

# ---------------------------
# Deck mapping
# ---------------------------
deck_of_cards = {
    1: 0,
    2: 1,
    3: 2, 4: 2,
    5: 3, 6: 3, 7: 3,
    8: 4, 9: 4, 10: 4, 11: 4,
    12: 5, 13: 5, 14: 5, 15: 5, 16: 5,
    17: 6, 18: 6, 19: 6, 20: 6, 21: 6, 22: 6,
    23: 7, 24: 7, 25: 7, 26: 7, 27: 7, 28: 7, 29: 7,
    30: 8, 31: 8, 32: 8, 33: 8, 34: 8, 35: 8, 36: 8, 37: 8,
    38: 9, 39: 9, 40: 9, 41: 9, 42: 9, 43: 9, 44: 9, 45: 9, 46: 9,
    47: 10, 48: 10, 49: 10, 50: 10, 51: 10, 52: 10, 53: 10, 54: 10, 55: 10, 56: 10,
    57: 11, 58: 11, 59: 11, 60: 11, 61: 11, 62: 11, 63: 11, 64: 11, 65: 11, 66: 11, 67: 11,
    68: 12, 69: 12, 70: 12, 71: 12, 72: 12, 73: 12, 74: 12, 75: 12, 76: 12, 77: 12, 78: 12, 79: 12,
    80: "+2", 81: "+4", 82: "+6", 83: "+8", 84: "+10", 85: "x2",
    86: "Freeze", 87: "Freeze", 88: "Freeze",
    89: "Flip Three", 90: "Flip Three", 91: "Flip Three",
    92: "Second Chance", 93: "Second Chance", 94: "Second Chance"
}
discard_pile = [0]

# ---------------------------
# User manual text
# ---------------------------
instructions_list = [
    "Flip 7 - Instructions (How to Play)\n",
    "1. Setup: Decide the number of players (minimum 3, max 18). Each player starts with an empty hand.\n",
    "2. Take Turns: On your turn, choose to either Hit (draw a card) or Stay (end your turn and bank points).\n",
    "3. Play Cards:\n",
    "   - Number cards add points to your hand.\n",
    "   - Modifier cards adjust points (add or multiply).\n",
    "   - Action cards create special effects:\n",
    "        * Freeze: When drawn, you can target any active player, including yourself, to immediately end their turn,\n",
    "         keeping any cards collected so far as if they chose to Stay.\n",
    "        * Second Chance: When drawn, keep it for later. It lets you stay in the round in the event you flip a duplicate Number card. Then you can discard the Second Chance card and the duplicate Number card at the same time.\n",
    "        * Flip Three: When drawn, you must accept 3 cards from the dealer and flip them over one at a time.\n",
    "           - If you get a duplicate card, you're busted.\n",
    "           - If you draw another Flip Three or a Freeze card, finish drawing the first 3 cards before starting the new action.\n",
    "           - If you draw a Second Chance card, save it and finish drawing however many cards remain in your Flip Three.\n",
    "           - If, while drawing for Flip 3, you draw enough cards to make a Flip 7, gameplay stops because you just won the round. Don't finish the Flip 3 action.\n",
    "4. Avoid Busts: Do not draw a duplicate Number card, or your round ends with 0 points.\n",
    "5. 7 Unique Bonus: If you collect 7 different Number cards in one round, get +15 points and your round ends.\n",
    "6. Round End: The round ends when all players stayed, busted, or someone hits the 7 Unique Bonus.\n",
    "7. Winning: Continue rounds until a player reaches 200+ points. Highest score wins if multiple players pass 200 in the same round.\n\n"
]

rules_list = [
    "Flip 7 - Rules\n"
    "1. Objective: Be the first to reach 200 or more points.\n"
    "2. Number Cards (0-12): Add to your total score. Drawing a duplicate busts your round.\n"
    "3. Modifier Cards (+2, +4, x2, etc.): Alter your score for that round.\n"
    "4. Action Cards (Freeze!, Flip Three!, Second Chance): Trigger special effects. Check instructions to understand how they work.\n"
    "5. Bust: Drawing a duplicate Number card ends your turn and scores 0 points unless Second Chance is used.\n"
    "6. 7 Unique Bonus: Collecting 7 different Number cards in a round gives +15 points and ends the round immediately."
]

with open("instructions.txt", "w") as ins:
    ins.writelines(instructions_list)
    ins.writelines(rules_list)


# ---------------------------
# Game logic helpers
# ---------------------------
def calculate_round_score(hand):
    """Calculate numeric score of a hand (numbers + additive modifiers + x2 multiplier)."""
    number_cards = [card for card in hand if isinstance(card, int)]
    modifier_cards = [card for card in hand if isinstance(card, str) and (card.startswith('+') or card == 'x2')]

    number_value = sum(number_cards)
    multiplier = 1

    for mod in modifier_cards:
        if mod.startswith('+'):
            try:
                number_value += int(mod[1:])
            except ValueError:
                pass
        elif mod == 'x2':
            multiplier *= 2

    final = number_value * multiplier

    # 7 unique bonus
    if len(set(number_cards)) == 7:
        final += 15

    return final


def check_round_end(player_id, current_hand):
    """
    Returns (is_busted, is_7_unique, current_score).
    Handles Second Chance logic.
    """
    number_cards = [card for card in current_hand if isinstance(card, int)]

    # duplicate → possible bust
    if len(number_cards) != len(set(number_cards)):
        last_number = None
        for c in reversed(current_hand):
            if isinstance(c, int):
                last_number = c
                break

        if last_number is None:
            return (False, False, calculate_round_score(current_hand))

        if "Second Chance" in current_hand:
            # use Second Chance: remove one Second Chance + the duplicate just drawn
            current_hand.remove("Second Chance")
            for i in range(len(current_hand) - 1, -1, -1):
                if current_hand[i] == last_number:
                    current_hand.pop(i)
                    break
            return (False, False, calculate_round_score(current_hand))

        # no Second Chance → busted
        return (True, False, 0)

    # 7 unique check
    if len(set(number_cards)) == 7 and len(number_cards) >= 7:
        return (False, True, calculate_round_score(current_hand))

    return (False, False, calculate_round_score(current_hand))


# ---------------------------
# Tkinter GUI and state
# ---------------------------
class Flip7GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flip 7")
        self.root.geometry("980x620")
        self.root.configure(bg="#00BFFF")

        """ game state """
        self.num_players = 0
        self.player_scores = {}
        self.cards_in_hand = {}
        self.active_players = set()
        self.stayed_players = set()
        self.busted_players = set()
        self.finished_players = set()
        self.skip_turn = set()
        self.current_player = 0
        self.round_number = 1
        self.round_active = False
        self.temp_targets = []
        self.last_drawn = None
        self.card_label_bg = "#931B1B"

        self.build_start_frame()
        self.build_game_frame()

    # ---------------------------
    # Start / Setup UI
    # ---------------------------
    def build_start_frame(self):
        """ Framing UI """
        self.start_frame = tk.Frame(self.root, bg="#00BFFF")

        title = tk.Label(self.start_frame, text="Flip 7",
                         font=("Helvetica", 34, "bold"),
                         fg="white", bg="#00BFFF")
        title.pack()

        subtitle = tk.Label(self.start_frame,
                            text="Select number of players (3-18):",
                            fg="white", bg="#00BFFF",
                            font=("Helvetica", 14))
        subtitle.pack(pady=20)

        self.player_count_var = tk.IntVar(value=3)
        spin = tk.Spinbox(self.start_frame, from_=3, to=18,
                          textvariable=self.player_count_var,
                          width=5, font=("Helvetica", 14))
        spin.pack(pady=20)

        start_btn = tk.Button(self.start_frame, text="Start Game",
                              font=("Helvetica", 14),
                              bg="green", fg="white",
                              command=self.start_game)
        start_btn.pack(pady=20)

        rules_btn = tk.Button(self.start_frame,
                              text="Show User Manual\n(for beginner's, please read)",
                              font=("Helvetica", 12),
                              bg="gray", fg="white",
                              command=self.show_rules)
        rules_btn.pack(pady=20)

        self.start_frame.pack(expand=True, anchor="center")

    def show_rules(self):
        """ File I/O """
        with open("instructions.txt", "r") as ins:
            manual_text = ins.read()
        messagebox.showinfo("User Manual", manual_text)

    # ---------------------------
    # Main Game UI
    # ---------------------------
    def build_game_frame(self):
        """ Framing UI """
        self.game_frame = tk.Frame(self.root, bg="#151515")

        # top bar
        top_frame = tk.Frame(self.game_frame, bg="#151515")
        top_frame.pack(fill="x", pady=6)

        self.round_label = tk.Label(top_frame, text="Round: 0",
                                    font=("Helvetica", 16),
                                    bg="#151515", fg="cyan")
        self.round_label.pack(side="left", padx=10)

        self.turn_label = tk.Label(top_frame, text="Turn: Player 1",
                                   font=("Helvetica", 16),
                                   bg="#151515", fg="white")
        self.turn_label.pack(side="left", padx=20)

        self.next_round_btn = tk.Button(top_frame, text="Next Round",
                                        font=("Helvetica", 12),
                                        bg="#4caf50", fg="white",
                                        command=self.start_new_round,
                                        state="disabled")
        self.next_round_btn.pack(side="right", padx=10)

        self.restart_btn = tk.Button(top_frame, text="Restart Game",
                                     font=("Helvetica", 12),
                                     bg="#ff6666", fg="white",
                                     command=self.restart_game)
        self.restart_btn.pack(side="right", padx=10)

        self.end_btn = tk.Button(top_frame, text="End Game",
                                 font=("Helvetica", 12),
                                 bg="#ff6666", fg="white",
                                 command=self.end_game)
        self.end_btn.pack(side="right", padx=10)

        # little cyan bar
        below_top = tk.Frame(self.game_frame, bg="cyan", width=1000)
        below_top.pack()

        # scrollable players row
        player_scroll_frame = tk.Frame(self.game_frame, bg="#151515")
        player_scroll_frame.pack(fill="x", pady=5)

        player_canvas = tk.Canvas(player_scroll_frame, bg="#151515",
                                  highlightthickness=0, height=130)
        player_canvas.pack(side="left", fill="x", expand=True)

        x_scrollbar = tk.Scrollbar(player_scroll_frame, orient="horizontal",
                                   command=player_canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        player_canvas.configure(xscrollcommand=x_scrollbar.set)

        self.players_container = tk.Frame(player_canvas, bg="#151515")
        player_canvas.create_window((0, 0),
                                    window=self.players_container,
                                    anchor="nw")

        def update_scroll_region(event):
            """ scroll bar functions when there's more than 10 players """
            player_canvas.configure(scrollregion=player_canvas.bbox("all"))

        self.players_container.bind("<Configure>", update_scroll_region)

        # center stuff
        center_frame = tk.Frame(self.game_frame, bg="#151515")
        center_frame.pack(fill="both", expand=True)

        self.card_display = tk.Label(center_frame,
                                     text="Press 'Start Game' to begin",
                                     font=("Helvetica", 25),
                                     bg=self.card_label_bg, fg="white")
        self.card_display.pack(fill="x", pady=30)

        self.target_frame = tk.Frame(center_frame, bg="#151515")
        self.target_frame.pack(pady=6)

        controls = tk.Frame(center_frame, bg="#151515")
        controls.pack(pady=30)

        self.hit_btn = tk.Button(controls, text="Hit",
                                 font=("Helvetica", 18),
                                 bg="#33aa33", fg="white",
                                 width=30,
                                 command=self.hit_action,
                                 state="disabled")
        self.hit_btn.grid(row=0, column=0, padx=6)

        self.stay_btn = tk.Button(controls, text="Stay",
                                  font=("Helvetica", 18),
                                  bg="#ff9f1c", fg="white",
                                  width=30,
                                  command=self.stay_action,
                                  state="disabled")
        self.stay_btn.grid(row=0, column=1, padx=6)

        self.info_label = tk.Label(center_frame, text="",
                                   font=("Helvetica", 12),
                                   bg="#151515", fg="lightgray",
                                   wraplength=380, justify="left")
        self.info_label.pack(pady=6)

        log_frame = tk.Frame(self.game_frame, bg="#111111")
        log_frame.pack(side="bottom", fill="x")
        self.log_text = tk.Text(log_frame, height=30,
                                bg="#0f0f0f", fg="#dcdcdc")
        self.log_text.pack(fill="x")

    # ---------------------------
    # Game flow
    # ---------------------------
    def start_game(self):
        """ begins a new game """
        n = self.player_count_var.get()
        if not (3 <= n <= 18):
            messagebox.showwarning("Players", "Choose between 3 and 18 players.")
            return

        self.num_players = int(n)
        self.player_scores = {i: 0 for i in range(self.num_players)}
        self.cards_in_hand = {i: [] for i in range(self.num_players)}

        self.start_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.setup_player_panels()
        self.start_new_round()

    def setup_player_panels(self):
        """ setup for player panel """
        for widget in self.players_container.winfo_children():
            widget.destroy()

        self.player_frames = []
        for i in range(self.num_players):
            f = tk.Frame(self.players_container, bg="#1b1b1b",
                         bd=1, relief="solid", padx=6, pady=6)
            f.pack(side="left", padx=8, pady=4)

            lbl = tk.Label(f, text=f"Player {i+1}",
                           font=("Helvetica", 14, "bold"),
                           bg="#1b1b1b", fg="white")
            lbl.pack(anchor="w")

            score_lbl = tk.Label(f, text=f"Total: {self.player_scores[i]}",
                                 font=("Helvetica", 12),
                                 bg="#1b1b1b", fg="lightgreen")
            score_lbl.pack(anchor="w")

            hand_lbl = tk.Label(f, text="Hand: []",
                                font=("Helvetica", 11),
                                bg="#1b1b1b", fg="lightgray",
                                wraplength=300, justify="left")
            hand_lbl.pack(anchor="w")

            status_lbl = tk.Label(f, text="Status: Ready",
                                  font=("Helvetica", 10),
                                  bg="#1b1b1b", fg="cyan")
            status_lbl.pack(anchor="w")

            self.player_frames.append({
                "frame": f,
                "score": score_lbl,
                "hand": hand_lbl,
                "status": status_lbl
            })

    def log(self, text):
        """ shows end of game """
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def start_new_round(self):
        """ starts new round """
        self.round_active = True
        self.cards_in_hand = {i: [] for i in range(self.num_players)}
        self.active_players = set(range(self.num_players))
        self.stayed_players = set()
        self.busted_players = set()
        self.finished_players = set()
        self.skip_turn = set()
        self.current_player = 0

        self.round_label.config(text=f"Round: {self.round_number}")
        self.turn_label.config(text=f"Turn: Player {self.current_player + 1}")
        self.update_all_player_panels()

        self.card_display.config(
            text="Round started. Player 1's turn – Hit or Stay.",
            bg=self.card_label_bg
        )
        self.info_label.config(text="")
        self.hit_btn.config(state="normal")
        self.stay_btn.config(state="normal")
        self.next_round_btn.config(state="disabled")
        self.log(f"--- Round {self.round_number} started ---")

    def end_round_and_bank(self):
        """Bank all round scores, busted players get 0."""
        for p in range(self.num_players):
            if p in self.busted_players:
                round_score = 0
            else:
                round_score = calculate_round_score(self.cards_in_hand.get(p, []))
            self.player_scores[p] += round_score

        self.round_active = False
        self.hit_btn.config(state="disabled")
        self.stay_btn.config(state="disabled")
        self.next_round_btn.config(state="normal")
        self.log("Round ended. Scores banked.")
        self.update_all_player_panels()

        winner = self.checking_winner()
        if winner is not None:
            messagebox.showinfo("Winner!",
                                f"Player {winner+1} wins with {self.player_scores[winner]} points!")
            self.log(f"Player {winner+1} wins the game with {self.player_scores[winner]} points!")
            self.hit_btn.config(state="disabled")
            self.stay_btn.config(state="disabled")
            self.next_round_btn.config(state="disabled")

        self.round_number += 1

    def checking_winner(self):
        """ checks for winner """
        if not self.player_scores:
            return None
        max_score = max(self.player_scores.values())
        if max_score < 200:
            return None
        for player, score in self.player_scores.items():
            if score == max_score:
                return player

    def restart_game(self):
        """ function to restart game """
        if messagebox.askyesno("Restart", "Restart the entire game?"):

            self.game_frame.pack_forget()

            self.num_players = 0
            self.player_scores = {}
            self.cards_in_hand = {}
            self.active_players = set()
            self.stayed_players = set()
            self.busted_players = set()
            self.finished_players = set()
            self.skip_turn = set()
            self.current_player = 0
            self.round_active = False
            self.last_drawn = None
            self.round_number = 1

            self.log_text.delete("1.0", "end")

            self.start_frame.destroy()
            self.build_start_frame()
            self.player_count_var.set(3)
            self.start_frame.pack(expand=True, anchor="center")

    def end_game(self):
        """ function to end game """
        if messagebox.askyesno("End", "End the entire game?"):

            self.game_frame.pack_forget()
            endscreen = tk.Label(self.root, text='Thanks for playing!',
                                 font=("Helvetica", 80),
                                 bg="#00BFFF")
            endscreen.pack(fill="both", expand=True)
            self.root.update()
            self.root.after(1000, self.root.destroy)

    # ---------------------------
    # Player actions (Hit / Stay)
    # ---------------------------
    def hit_action(self):
        card_key = 0
        """One hit per turn, then move on (unless choosing target)."""
        if not self.round_active:
            return

        p = self.current_player

        if p in self.skip_turn:
            self.log(f"Player {p+1} loses this turn due to Freeze.")
            self.card_display.config(
                text=f"Player {p+1} was frozen and misses this turn.",
                bg="#555555"
            )
            self.skip_turn.remove(p)
            self.next_turn()
            return

        while card_key in discard_pile:
            card_key = random.randint(1, 94)
        discard_pile.append(card_key)
        value = deck_of_cards[card_key]
        self.last_drawn = value
        self.cards_in_hand[p].append(value)

        self.update_player_hand_display(p)
        bg = self.card_color(value)
        self.card_display.config(text=f"Player {p+1} drew: {value}", bg=bg)
        self.log(f"Player {p+1} drew {value}")

        is_busted, is_7_unique, current_val = check_round_end(
            p, self.cards_in_hand[p]
        )

        if is_busted:
            self.busted_players.add(p)
            self.finished_players.add(p)
            self.card_display.config(
                text=f"Player {p+1} busted with a duplicate. Round score: 0",
                bg="#660000"
            )
            self.log(f"Player {p+1} busted.")
            self.update_player_status(p, "Busted")
            self.next_turn()
            return

        if is_7_unique:
            self.finished_players.add(p)
            self.update_player_status(p, "7-Unique! Finished")
            self.log(f"Player {p+1} hit 7 unique numbers. Banking {current_val} points.")
            self.next_turn()
            return

        if isinstance(value, str):
            if value == "Freeze":
                self.show_target_buttons(action="Freeze", source_player=p)
                return
            elif value == "Flip Three":
                self.show_target_buttons(action="Flip Three", source_player=p)
                return
            elif value == "Second Chance":
                self.log(f"Player {p+1} holds a Second Chance card.")
                self.update_player_status(p, "Has Second Chance")
                self.next_turn()
                return
            else:
                self.update_player_status(p, "Modifier in hand")
                self.next_turn()
                return

        self.update_player_status(p, f"Score: {current_val}")
        self.next_turn()

    def stay_action(self):
        """ function for stay """
        if not self.round_active:
            return

        p = self.current_player
        self.stayed_players.add(p)
        self.finished_players.add(p)
        current_val = calculate_round_score(self.cards_in_hand[p])
        self.update_player_status(p, f"Stayed (round {current_val})")
        self.log(f"Player {p+1} stays and banks (at round end) {current_val} points.")
        self.next_turn()

    # ---------------------------
    # NEXT TURN (for...else)
    # ---------------------------
    def next_turn(self):
        """Move to next non-finished player, or end round."""
        search_order = list(range(self.current_player + 1, self.num_players)) + \
                       list(range(0, self.current_player + 1))

        # for...else required by rubric – logic stays the same
        for idx in search_order:
            if idx not in self.finished_players:
                self.current_player = idx
                break
        else:
            # this runs only if we never broke the loop → all players finished
            self.log("All players finished for this round.")
            self.end_round_and_bank()
            return

        self.turn_label.config(text=f"Turn: Player {self.current_player + 1}")
        self.card_display.config(
            text=f"Player {self.current_player + 1}'s turn – Hit or Stay",
            bg=self.card_label_bg
        )

        self.root.update_idletasks()
        self.update_all_player_panels()

    # ---------------------------
    # Action card target UI
    # ---------------------------
    def show_target_buttons(self, action, source_player):
        self.hit_btn.config(state="disabled")  # disable hit button until user chooses
        self.stay_btn.config(state="disabled")  # disable stay button until user picks

        """ targets """
        for btn in self.temp_targets:
            btn.destroy()
        self.temp_targets = []

        prompt = tk.Label(self.target_frame,
                          text=f"Action: {action}. Choose a target:",
                          bg="#151515", fg="white")
        prompt.pack(side="left", padx=6)
        self.temp_targets.append(prompt)

        for t in range(self.num_players):
            state = "normal"
            if t in self.finished_players:
                state = "disabled"
            btn = tk.Button(
                self.target_frame,
                text=f"P{t+1}",
                width=4,
                command=lambda target=t, act=action, src=source_player:
                    (self.resolve_action_target(act, src, target),
                     self.hit_btn.config(state="normal"),
                     self.stay_btn.config(state="normal")),
                state=state
            )
            btn.pack(side="left", padx=4)
            self.temp_targets.append(btn)

    def clear_temp_targets(self):
        """ targets """
        for w in self.temp_targets:
            w.destroy()
        self.temp_targets = []

    def resolve_action_target(self, action, source_player, target_player):
        """ Action card functions """
        self.clear_temp_targets()
        self.log(f"Player {source_player+1} used {action} on Player {target_player+1}.")

        if action == "Freeze":
            self.skip_turn.add(target_player)
            self.update_player_status(target_player, "Frozen (loses next turn)")
            self.card_display.config(
                text=f"Player {target_player+1} will lose their next turn (Freeze).",
                bg="#ffdd88"
            )
            self.next_turn()

        elif action == "Flip Three":
            self.card_display.config(
                text=f"Player {target_player+1} must Flip Three cards.",
                bg="#ffcc77"
            )
            self.root.update()
            for i in range(3):
                card_key = 0
                while card_key in discard_pile:
                    card_key = random.randint(1, 94)
                discard_pile.append(card_key)
                v = deck_of_cards[card_key]
                self.cards_in_hand[target_player].append(v)

                # 👉 show each flipped card in the big center bar
                self.card_display.config(
                    text=f"Player {target_player+1} flipped: {v}",
                    bg=self.card_color(v)
                )
                self.root.update()

                self.update_player_hand_display(target_player)
                self.log(f"Player {target_player+1} flipped {v}")

                is_busted, is_7_unique, cur_val = check_round_end(
                    target_player, self.cards_in_hand[target_player]
                )
                if is_busted:
                    self.busted_players.add(target_player)
                    self.finished_players.add(target_player)
                    self.update_player_status(target_player, "Busted from Flip Three")
                    self.log(f"Player {target_player+1} busted during Flip Three.")
                    break
                if is_7_unique:
                    self.finished_players.add(target_player)
                    self.update_player_status(target_player, f"7-Unique! ({cur_val})")
                    self.log(f"Player {target_player+1} got 7-Unique during Flip Three.")
                    break

            self.next_turn()

        else:
            self.next_turn()

    # ---------------------------
    # UI helpers
    # ---------------------------
    def update_player_hand_display(self, p):
        """ player activity """
        hand = self.cards_in_hand.get(p, [])
        hand_text = "[" + ", ".join(map(str, hand)) + "]"
        self.player_frames[p]["hand"].config(text=f"Hand: {hand_text}")
        round_val = calculate_round_score(hand)
        self.player_frames[p]["score"].config(
            text=f"Total: {self.player_scores[p]}"
        )
        status = self.player_frames[p]["status"].cget("text")
        if ("Busted" in status or "Stayed" in status or
                "7-Unique" in status or "Frozen" in status):
            return
        self.player_frames[p]["status"].config(text=f"Round: {round_val}")

    def update_player_status(self, p, text):
        """ player activity """
        self.player_frames[p]["status"].config(text=f"Status: {text}")

    def update_all_player_panels(self):
        """ player activity """
        for p in range(self.num_players):
            self.player_frames[p]["score"].config(
                text=f"Total: {self.player_scores[p]}"
            )
            hand = self.cards_in_hand.get(p, [])
            hand_text = "[" + ", ".join(map(str, hand)) + "]"
            self.player_frames[p]["hand"].config(text=f"Hand: {hand_text}")
            if p in self.finished_players:
                st = "Finished"
            elif p in self.skip_turn:
                st = "Frozen"
            else:
                st = "Active"
            self.player_frames[p]["status"].config(text=f"Status: {st}")

    def card_color(self, value):
        """ changes color for action cards """
        if isinstance(value, int):
            return "#3da5d9"
        if value == "Freeze":
            return "#ff9f1c"
        if value == "Flip Three":
            return "#ffcc66"
        if value == "Second Chance":
            return "#a0e7a0"
        if isinstance(value, str) and (value.startswith("+") or value == "x2"):
            return "#9fe2bf"
        return "#444444"


# ---------------------------
# Run it
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = Flip7GUI(root)
    root.mainloop()
