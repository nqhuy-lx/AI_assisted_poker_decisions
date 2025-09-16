import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import pyautogui

from NhanDienBoBai import update_folds
from NhanDienLaBai import capture_screen, recognize_hand, recognize_board
from LoadTemplate import load_templates
from XacDinhTiLeScale import estimate_scale
import Van_Bai
from MonteCarloSimulator import simulate
from ClickActionEvent import ButtonClicker, wait_result_and_restart


class PokerCMD_GUI:
    def __init__(self, root, initial_bots=4, sim_runs=1000):
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')

        self.root = root
        self.root.title("Poker AI CMD GUI")
        self.root.attributes("-topmost", True)

        screenTemplate = capture_screen()
        icons = load_templates("FindScale")
        if not icons:
            raise RuntimeError("Không tìm thấy folder FindScale")
        icon_img = list(icons.values())[0]
        self.scale = estimate_scale(screenTemplate, icon_img)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = int(screen_width - (400 * self.scale))
        y = int((screen_height // 2) - ((760 * self.scale) // 2))
        self.root.geometry(f"{int(400 * self.scale)}x{int(760 * self.scale)}+{x}+{y}")

        self.output = ScrolledText(root, width=50, height=30,
                                   state='disabled', bg='black', fg='white')
        self.output.pack(padx=6, pady=6, fill='both', expand=True)

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(root, textvariable=self.input_var)
        self.input_entry.pack(fill='x', padx=6, pady=(0, 6))
        self.input_entry.bind("<Return>", self.on_enter)

        self.input_callback = None
        self.sim_runs = sim_runs
        self.initial_bots = initial_bots
        self.used_regions = []
        self.fold_seen = 0
        self.my_hand = []
        self.van = None

        self.clicker = ButtonClicker()
        self.decision = ""
        self.auto_decision = ""
        self.auto_mode = False
        self.auto_games = 0
        self.games_played = 0

        self.already_raised = False

        self.waiting_user = False
        self.running = True
        self.hand_running = False

        self._observing = False

        self._log("=== Poker AI (web mode) ===")
        self.ask("Bạn muốn chơi thủ công hay AI tự chơi? (tay/auto):", self.choose_mode)

    def _log(self, text):
        if not self.running:
            return
        self.output.config(state='normal')
        self.output.insert(tk.END, str(text) + "\n")
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def clear_output(self):
        self.output.config(state='normal')
        self.output.delete("1.0", tk.END)
        self.output.config(state='disabled')

    def ask(self, prompt, callback):
        if not self.running:
            return
        self._log(prompt)
        self.input_callback = callback
        self.input_entry.focus()
        self.waiting_user = True

    def on_enter(self, event):
        if self.input_callback and self.running:
            val = self.input_var.get().strip()
            self.input_var.set("")
            cb = self.input_callback
            self.input_callback = None
            self.waiting_user = False
            cb(val)

    def choose_mode(self, val):
        if val.lower() == "auto":
            self.ask("Nhập tên folder để lưu kết quả:", self.set_folder_name)
        else:
            self.auto_mode = False
            self._log("👉 Chế độ thủ công được chọn")
            self.ask("Nhấn Enter để 10s sau sẽ bắt đầu nhận diện bài cầm tay...", self.preflop_step)

    def set_folder_name(self, val):
        self.folder_name = val.strip() if val.strip() else "DefaultRun"
        self.ask("AI sẽ chơi bao nhiêu ván?", self.set_auto_games)        

    def set_auto_games(self, val):
        try:
            self.auto_games = int(val)
            self.auto_mode = True
            self.games_played = 0
            self._log(f"👉 Chế độ auto: AI sẽ chơi {self.auto_games} ván")
            self.ask("Nhấn Enter để nhận diện bài cầm tay và bắt đầu tự động chơi trong 10s sau...", self.preflop_step)
        except:
            self._log("⚠️ Vui lòng nhập số hợp lệ")
            self.ask("AI sẽ chơi bao nhiêu ván?", self.set_auto_games)

    def preflop_step(self, val):
        self.hand_running = True
        self.clear_output()
        self.used_regions = []
        self.fold_seen = 0
        self.already_raised = False
        self._observing = False
        self.my_hand = []
        self.flop = []
        self.flop_plus = []
        self.full_board = []

        if self.auto_mode:
            self.games_played += 1
            self._log(f"=== Ván {self.games_played} bắt đầu sau 10s... ===")
        else:
            self._log("👉 Bắt đầu nhận diện sau 10s...")

        self.root.after(10000, self._start_preflop)

    def _start_preflop(self):
        screen = capture_screen()
        hand_left, hand_right = recognize_hand(screen, self.scale)
        if not hand_left or not hand_right:
            self._log("Không nhận diện được bài cầm tay.")
            self.ask("Không nhận được bài cầm tay. Thử lại? (c/k):", self.ask_retry_preflop)
            return
        self.my_hand = [hand_left, hand_right]
        self._log(f"Bài cầm tay: {self.my_hand[0]}, {self.my_hand[1]}")

        self.van = Van_Bai.VanBai(so_doi_thu=self.initial_bots,
                                 so_lan_mo_phong=self.sim_runs, web_mode=True)
        self.van.cap_nhat_bai_nguoi_choi(self.my_hand)

        self.already_raised = False
        self._log("⏳ Đang tính toán mô phỏng Preflop...")
        threading.Thread(target=self.preflop_simulation, daemon=True).start()

    def ask_retry_preflop(self, val):
        if val.lower() == 'c':
            self.ask("Nhấn Enter để bắt đầu nhận diện bài cầm tay...", self.preflop_step)
        else:
            self._log("Hoàn tất/thoát.")
            self.root.quit()

    def preflop_simulation(self):
        so_active = self.van.so_doi_thu + 1
        sim = simulate(self.my_hand, [], so_active, runs=self.sim_runs)
        self.root.after(0, lambda: self.show_preflop(sim, so_active))

    def show_preflop(self, sim, so_active):
        self._log(f"[Preflop] p_raw={sim['p_raw']*100:.2f}% | p_final={sim['p_final']*100:.2f}%")
        self.auto_decision, self.decision = self.van.ai.ra_quyet_dinh(self.my_hand, [], so_active, vong="preflop")
        self._log(f"{self.decision}")

        if self.auto_mode:
            self.root.after(200, lambda: self._auto_click(self.auto_decision))
            self.observe_until_next(3, self.auto_decision, self.flop_step_auto)
        else:
            self.ask("Hành động (theo/to/bo):", self.preflop_action)

    def preflop_action(self, act):
        if act == "bo":
            self._log("Bạn đã bỏ bài.")
            self.hand_running = False
            self._log("=== Ván kết thúc ===")
            self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)
            return
        self.ask("Nhấn Enter để nhận diện Flop...", self.flop_step_manual)

    def observe_until_next(self, expected_total_cards, decision, next_step_callback):
        if self._observing:
            return
        self._observing = True

        def loop():
            if not self.hand_running or not self.running:
                self._observing = False
                return
            
            if (self.clicker.wait(self.scale)==True):
                self._observing = False
                self._log(f"=== Ván {self.games_played} kết thúc ===")
                self.hand_running = False
                log_text = self.output.get("1.0", tk.END)
                self.root.after(800, wait_result_and_restart(self.scale, self.folder_name, self.games_played, log_text))
                if self.auto_mode:
                    if self.games_played < self.auto_games:
                        self.root.after(5000, self.preflop_step, "")
                    else:
                        self._log("🎉 AI đã hoàn thành số ván yêu cầu.")
                        self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)

            screen = capture_screen()
            board = recognize_board(screen, expected_total_cards, self.scale,
                                    exclude=self.my_hand, used_regions=self.used_regions)
            if len(board) == expected_total_cards:
                self._observing = False
                self.already_raised = False
                next_step_callback(board)
                return

            if decision == "theo":
                if not self.clicker.click_button("Check", self.scale, wait_until_found=False):
                    self.clicker.click_button("Call", self.scale, wait_until_found=False)
            elif decision == "to":
                if not self.already_raised:
                    if self.clicker.click_button("Raise", self.scale, wait_until_found=False):
                        self.clicker.click_button("OK", self.scale, wait_until_found=False)
                        self.already_raised = True
                else:
                    if not self.clicker.click_button("Check", self.scale, wait_until_found=False):
                        self.clicker.click_button("Call", self.scale, wait_until_found=False)
            elif decision == "bo":
                if self.clicker.click_button("Fold", self.scale, wait_until_found=False):
                    self._log(f"=== Ván {self.games_played} kết thúc ===")
                    self.hand_running = False
                    self._observing = False
                    log_text = self.output.get("1.0", tk.END)
                    self.root.after(800, wait_result_and_restart(self.scale, self.folder_name, self.games_played, log_text))
                    return

            self.root.after(8000, loop)

        self.root.after(8000, loop)

    def observe_until_end(self, decision):
        if self._observing:
            return
        self._observing = True

        def loop():
            if not self.hand_running or not self.running:
                self._observing = False
                return
            
            if (self.clicker.wait(self.scale)==False):
                if not self.clicker.click_button("Check", self.scale, wait_until_found=False):
                    self.clicker.click_button("Call", self.scale, wait_until_found=False)
                self.root.after(8000, loop)
            else:
                self._observing = False
                self._log(f"=== Ván {self.games_played} kết thúc ===")
                self.hand_running = False
                log_text = self.output.get("1.0", tk.END)
                self.root.after(800, wait_result_and_restart(self.scale, self.folder_name, self.games_played, log_text))
                if self.auto_mode:
                    if self.games_played < self.auto_games:
                        self.root.after(5000, self.preflop_step, "")
                    else:
                        self._log("🎉 AI đã hoàn thành số ván yêu cầu.")
                        self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)

        self.root.after(8000, loop)

    def flop_step_auto(self, flop):
        self.flop = flop
        self.van.bai_chung = self.flop
        self._log(f"✅ Đã thấy Flop: {', '.join(flop)}")
        self._log("⏳ Đang tính toán mô phỏng Flop...")
        threading.Thread(target=self.flop_simulation, daemon=True).start()

    def flop_step_manual(self, val):
        screen = capture_screen()
        flop = recognize_board(screen, 3, self.scale, exclude=self.my_hand, used_regions=self.used_regions)
        if len(flop) != 3:
            self._log("Chưa nhận diện đủ Flop.")
            self.ask("Nhấn Enter khi Flop xuất hiện...", self.flop_step_manual)
            return
        self.van.bai_chung = flop
        self.flop = flop
        self.already_raised = False
        self._log("⏳ Đang tính toán mô phỏng Flop...")
        threading.Thread(target=self.flop_simulation, daemon=True).start()

    def flop_simulation(self):
        screen = capture_screen()
        self.fold_seen = update_folds(screen, self.scale, self.fold_seen, log_func=self._log, VanBai=self.van)
        so_active = self.van.so_active_players()
        sim = simulate(self.my_hand, self.flop, so_active, runs=self.sim_runs)
        self.root.after(0, lambda: self.show_flop(sim, so_active))

    def show_flop(self, sim, so_active):
        self._log(f"[Flop] Board: {', '.join(self.flop)}")
        self._log(f"p_raw={sim['p_raw']*100:.2f}% | p_final={sim['p_final']*100:.2f}%")
        self.auto_decision, self.decision = self.van.ai.ra_quyet_dinh(self.my_hand, self.flop, so_active, vong='flop')
        self._log(f"{self.decision}")

        if self.auto_mode:
            self.root.after(200, lambda: self._auto_click(self.auto_decision))
            self.observe_until_next(1, self.auto_decision, self.turn_step_auto)
        else:
            self.ask("Hành động (theo/to/bo):", self.flop_action)

    def flop_action(self, act):
        if act == "bo":
            self._log("Bạn đã bỏ bài.")
            self.hand_running = False
            self._log("=== Ván kết thúc ===")
            self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)
            return
        self.ask("Nhấn Enter để nhận diện Turn...", self.turn_step_manual)

    def turn_step_auto(self, turn):
        self.flop_plus = self.flop + turn
        self.van.bai_chung = self.flop_plus
        self._log(f"✅ Đã thấy Turn: {', '.join(turn)}")
        self._log("⏳ Đang tính toán mô phỏng Turn...")
        threading.Thread(target=self.turn_simulation, daemon=True).start()

    def turn_step_manual(self, val):
        screen = capture_screen()
        turn = recognize_board(screen, 1, self.scale, exclude=self.my_hand, used_regions=self.used_regions)
        if len(turn) != 1:
            self._log("Chưa nhận diện đủ Turn.")
            self.ask("Nhấn Enter khi Turn xuất hiện...", self.turn_step_manual)
            return
        self.flop_plus = self.flop + turn
        self.van.bai_chung = self.flop_plus
        self.already_raised = False
        self._log("⏳ Đang tính toán mô phỏng Turn...")
        threading.Thread(target=self.turn_simulation, daemon=True).start()

    def turn_simulation(self):
        screen = capture_screen()
        update_folds(screen, self.scale, self.fold_seen, log_func=self._log, VanBai=self.van)
        so_active = self.van.so_active_players()
        sim = simulate(self.my_hand, self.flop_plus, so_active, runs=self.sim_runs)
        self.root.after(0, lambda: self.show_turn(sim, so_active))

    def show_turn(self, sim, so_active):
        self._log(f"[Turn] Board: {', '.join(self.flop_plus)}")
        self._log(f"p_raw={sim['p_raw']*100:.2f}% | p_final={sim['p_final']*100:.2f}%")
        self.auto_decision, self.decision = self.van.ai.ra_quyet_dinh(self.my_hand, self.flop_plus, so_active, vong='turn')
        self._log(f"{self.decision}")

        if self.auto_mode:
            self.root.after(200, lambda: self._auto_click(self.auto_decision))
            self.observe_until_next(1, self.auto_decision, self.river_step_auto)
        else:
            self.ask("Hành động (theo/to/bo):", self.turn_action)

    def turn_action(self, act):
        if act == "bo":
            self._log("Bạn đã bỏ bài.")
            self.hand_running = False
            self._log("=== Ván kết thúc ===")
            self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)
            return
        self.ask("Nhấn Enter để nhận diện River...", self.river_step_manual)

    def river_step_auto(self, river):
        self.full_board = self.flop_plus + river
        self.van.bai_chung = self.full_board
        self._log(f"✅ Đã thấy River: {', '.join(river)}")
        self._log("⏳ Đang tính toán mô phỏng River...")
        threading.Thread(target=self.river_simulation, daemon=True).start()

    def river_step_manual(self, val):
        screen = capture_screen()
        river = recognize_board(screen, 1, self.scale, exclude=self.my_hand, used_regions=self.used_regions)
        if len(river) != 1:
            self._log("Chưa nhận diện đủ River.")
            self.ask("Nhấn Enter khi River xuất hiện...", self.river_step_manual)
            return
        self.full_board = self.flop_plus + river
        self.van.bai_chung = self.full_board
        self.already_raised = False
        self._log("⏳ Đang tính toán mô phỏng River...")
        threading.Thread(target=self.river_simulation, daemon=True).start()

    def river_simulation(self):
        screen = capture_screen()
        update_folds(screen, self.scale, self.fold_seen, log_func=self._log, VanBai=self.van)
        so_active = self.van.so_active_players()
        sim = simulate(self.my_hand, self.full_board, so_active, runs=self.sim_runs)
        self.root.after(0, lambda: self.show_river(sim, so_active))

    def show_river(self, sim, so_active):
        self._log(f"[River] Board: {', '.join(self.full_board)}")
        self._log(f"p_raw={sim['p_raw']*100:.2f}% | p_final={sim['p_final']*100:.2f}%")
        self.auto_decision, self.decision = self.van.ai.ra_quyet_dinh(
            self.my_hand, self.full_board, so_active, vong='river'
        )
        self._log(f"{self.decision}")

        if self.auto_mode:
            self.root.after(200, lambda: self._auto_click(self.auto_decision))
            self.root.after(5000,self.observe_until_end(self.decision))
        else:
            self.river_action_manual()

    def river_action_manual(self):
        self.hand_running = False
        self._log("=== Ván kết thúc ===")
        self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)
        return

    def ask_continue(self, val):
        if val.lower() == "c":
            self.clear_output()
            self._log("=== Poker AI (web mode) ===")
            self.root.after(2000, lambda: self.ask("Bạn muốn chơi thủ công hay AI tự chơi? (tay/auto):", self.choose_mode))
        else:
            self._log("👋 Kết thúc chương trình.")
            self.hand_running = False
            self.root.quit()

    def _auto_click(self, decision):
        decision = decision.lower()
        if "bo" in decision:
            self._log("Auto action: Fold")
            self.clicker.click_button("Fold", self.scale, wait_until_found=False)
            self._log(f"=== Ván {self.games_played} kết thúc ===")
            self.hand_running = False
            log_text = self.output.get("1.0", tk.END)
            self.root.after(800, wait_result_and_restart(self.scale, self.folder_name, self.games_played, log_text))
            if self.auto_mode and self.games_played < self.auto_games:
                self.clear_output()
                self.root.after(5000, self.preflop_step, "")
            else:
                self.ask("Bạn có muốn tiếp tục chơi không? (c/k):", self.ask_continue)
        elif "theo" in decision:
            if self.clicker.click_button("Check", self.scale, wait_until_found=False):
                self._log("Auto action: Check")
            else:
                if self.clicker.click_button("Call", self.scale, wait_until_found=False):
                    self._log("Auto action: Call")
        elif "to" in decision:
            if not self.already_raised:
                if self.clicker.click_button("Raise", self.scale, wait_until_found=False):
                    self._log("Auto action: Raise")
                    self.clicker.click_button("OK", self.scale, wait_until_found=False)
                    self.already_raised = True
            else:
                if not self.clicker.click_button("Check", self.scale, wait_until_found=False):
                    self.clicker.click_button("Call", self.scale, wait_until_found=False)
                self._log("Auto action: Already raised -> Call/Check")

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerCMD_GUI(root, initial_bots=4, sim_runs=1000)
    root.mainloop()
