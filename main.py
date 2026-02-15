import customtkinter
import requests

class TypingTester:
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.title("Typing Tester")
        self.root.geometry("800x400")
        self.root.config(background="#362F4F")
        self.exception = []
        self.text_widget = None
        self.paragraph = ''
        self.letters_done = 0
        self.words_done = 0
        self.time_left = 15
        self.wps = 0.0
        self.allWps = {}
        self.timer_running = False
        self.fontSettings = ("Arial", 24, "bold")

        self.current_index = 0

        self.url = "https://random-words-api.kushcreates.com/api"
        self.params = {
            "language": "en",
            "words": '150',
            'alphabetize': "false"
        }

    def handler(self):
        try:
            data = requests.get(self.url, params=self.params)
            data = data.json()
            paragraph = [words['word'] for words in data]
            self.paragraph = " ".join(paragraph)
        except Exception as e:
            self.paragraph = "Error fetching words. Please check internet."
            print(e)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.configure(text=f"Time: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        else:
            self.end_game()

    def end_game(self):
        total_seconds = 0
        self.timer_running = False
        self.root.unbind("<Key>")

        self.text_widget.configure(state="disabled")
        print(self.allWps)
        for seconds in self.allWps.values():
            total_seconds += seconds
        try:
            wpm = int((self.words_done * 60) / total_seconds)
        except:
            print("No words typed please try again")
        else:
            self.timer_label.configure(text=f"Wpm: {wpm}", text_color="#E6501B")

    def cursor(self):
        pass

    def wordPerSeconds(self):
        self.wps += .01
        self.root.after(10, self.wordPerSeconds)

    def nextWordStarted(self):
        finalTime = self.wps
        self.allWps[f"word{self.words_done}"] = finalTime
        self.wps = 0


    def show_words_on_screen(self):

        self.text_widget = customtkinter.CTkTextbox(
            self.root,
            width=760,
            height=200,
            fg_color="#564B7D",
            bg_color="#362F4F",
            corner_radius=20,
            font=("Arial", 40),
            wrap="word"
        )
        self.timer_label = customtkinter.CTkLabel(
            self.root, text=f"Time: {self.time_left}s", font=self.fontSettings, bg_color="#362F4F", fg_color="#362F4F", text_color="#E4FF30"
        )
        self.text_widget.grid(row=0, column=0, padx=20, pady=20)
        self.timer_label.grid(row=1, column=0, pady=120)

        self.text_widget.insert("0.0", self.paragraph)

        self.text_widget.tag_config("typed", foreground="#E4FF30")
        self.text_widget.tag_config("pending", foreground="#008BFF")
        self.text_widget.tag_config("wrong", foreground="red")
        self.text_widget.tag_config("cursor", background="#00F0FF", foreground="#362F4F")

        self.text_widget.tag_add("pending", "1.0", "end")
        self.text_widget.tag_add("cursor", "1.0")
        self.text_widget.configure(state="disabled")

    def check_key(self, event):
        if self.current_index >= len(self.paragraph):
            return

        if not self.timer_running and self.time_left > 0:
            self.timer_running = True
            self.update_timer()
            self.wordPerSeconds()

        target_char = self.paragraph[self.current_index]

        if event.char == target_char:
            self.text_widget.tag_remove("cursor", f"1.{self.current_index}")

            self.letters_done += 1
            if self.letters_done >= 5:
                self.words_done += 1
                self.nextWordStarted()
                self.letters_done = 0
            self.current_index += 1

            tk_index = f"1.{self.current_index}"

            self.text_widget.configure(state="normal")

            self.text_widget.tag_add("typed", "1.0", tk_index)
            self.text_widget.tag_remove("pending", "1.0", tk_index)
            for i in self.exception:
                self.text_widget.tag_add("wrong", i)
                self.text_widget.tag_remove("typed", i)

            self.text_widget.configure(state="disabled")

        elif event.keysym == "BackSpace":
            self.text_widget.tag_remove("cursor", f"1.{self.current_index}")
            if self.current_index != 0:
                self.current_index -= 1
            tk_index = f"1.{self.current_index}"
            self.text_widget.tag_add("pending", tk_index)
            if tk_index in self.exception:
                self.text_widget.tag_remove("wrong", tk_index)
                self.exception.remove(tk_index)

        elif event.char != target_char:
            self.text_widget.tag_remove("cursor", f"1.{self.current_index}")
            tk_index = f"1.{self.current_index}"
            self.exception.append(tk_index)
            self.text_widget.tag_add("wrong", tk_index)
            self.current_index += 1

        self.text_widget.tag_add("cursor", f"1.{self.current_index}")


        look_ahead_index = f"1.{self.current_index} + 1 displaylines"
        self.text_widget.see(look_ahead_index)


    def run(self):
        self.handler()
        self.show_words_on_screen()

        self.root.bind("<Key>", self.check_key)
        self.root.mainloop()


if "__main__" == __name__:
    app = TypingTester()
    app.run()