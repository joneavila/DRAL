# A GUI application for viewing best and worst linear regression predictions.

import tkinter as tk
import tkinter.ttk as ttk

import data
import pandas as pd
from metrics import euclidean_distance_2D
from sox.core import play


# https://stackoverflow.com/a/65692405
class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        self.outer = tk.Frame(parent)
        self.canvas = tk.Canvas(self.outer)
        self.scroll = tk.Scrollbar(self.outer, command=self.canvas.yview)
        tk.Frame.__init__(self, self.canvas)
        self.contentWindow = self.canvas.create_window((0, 0), window=self, anchor="nw")

        self.canvas.pack(fill="both", expand=True, side="left")
        self.scroll.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.scroll.set)
        self.bind("<Configure>", self.resizeCanvas)

        self.pack = self.outer.pack
        self.place = self.outer.place
        self.grid = self.outer.grid

    def resizeCanvas(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.contentWindow, width=self.canvas.winfo_width())


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        master.geometry("1100x1000")
        master.title("Linear regression predictions")

        self.master = master

        frame_main = ScrollableFrame(self.master)

        # notebook_test_type = ttk.Notebook(self.master)
        notebook_test_type = ttk.Notebook(frame_main)

        frame_en_to_es = self.get_frame(notebook_test_type, "EN to ES")
        notebook_test_type.add(frame_en_to_es, text="EN → ES")

        frame_es_to_en = self.get_frame(notebook_test_type, "ES to EN")
        notebook_test_type.add(frame_es_to_en, text="ES → EN")

        notebook_test_type.pack(fill=tk.BOTH, expand=True)

        frame_main.pack(fill=tk.BOTH, expand=True)

    def get_frame(self, parent, test_type):

        # Load the data.
        if test_type == "EN to ES":
            df_Y_test = pd.read_csv(data.PATH_LIN_REG_FEATS_TEST_EN_ES, index_col="Row")
            df_Y_pred = pd.read_csv(data.PATH_LIN_REG_FEATS_PRED_EN_ES, index_col="Row")
        elif test_type == "ES to EN":
            df_Y_test = pd.read_csv(data.PATH_LIN_REG_FEATS_TEST_ES_EN, index_col="Row")
            df_Y_pred = pd.read_csv(data.PATH_LIN_REG_FEATS_PRED_ES_EN, index_col="Row")
        else:
            raise ValueError("Invalid test type.")

        # Compute the error (similarity) between the test and predicted values.
        arr_diff = euclidean_distance_2D(df_Y_test, df_Y_pred)
        df_diff = pd.DataFrame(arr_diff, columns=["similarity"], index=df_Y_test.index)

        df_diff_best = df_diff.sort_values("similarity", ascending=True)
        df_diff_worst = df_diff.sort_values("similarity", ascending=False)

        notebook_pred_type = ttk.Notebook(parent)

        frame_best = self.create_list_of_frags(notebook_pred_type, df_diff_best)
        notebook_pred_type.add(frame_best, text="Best")

        frame_worst = self.create_list_of_frags(notebook_pred_type, df_diff_worst)
        notebook_pred_type.add(frame_worst, text="Worst")

        notebook_pred_type.pack(fill=tk.BOTH, expand=True)

        return notebook_pred_type

    def create_list_of_frags(self, parent, df_diff):
        MAX = 32
        frame_main = ttk.Frame(parent)
        for i in range(MAX):

            frame_pair = ttk.Frame(frame_main)

            frag_id_output = df_diff.index[i]
            score = df_diff.iloc[i]["similarity"]
            if "EN" in frag_id_output:
                frag_id_input = frag_id_output.replace("EN", "ES")
            elif "ES" in frag_id_output:
                frag_id_input = frag_id_output.replace("ES", "EN")

            frame_frag_input = self.create_fragment_frame(
                frame_pair, frag_id_input, None
            )
            frame_frag_input.pack(side=tk.LEFT)

            frame_frag_output = self.create_fragment_frame(
                frame_pair, frag_id_output, score
            )
            frame_frag_output.pack(side=tk.RIGHT)

            frame_pair.pack()

            ttk.Separator(frame_main, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )
        frame_main.pack()
        return frame_main

    # TODO Some duplicate code from main_gui.py.
    def create_fragment_frame(self, master, frag_id: str, error: str):

        frame_main = ttk.Frame(master)

        frame_info = ttk.Frame(frame_main, width=350, height=350)

        # Fragment ID and error.
        frame_title = ttk.Frame(frame_info)
        ttk.Label(frame_title, text=frag_id, style="bold.TLabel").pack(side=tk.LEFT)
        if error is not None:
            ttk.Label(frame_title, text=f"(error = {error:.2f})").pack(side=tk.LEFT)
        frame_title.pack(anchor=tk.W)

        frame_info.pack(fill=tk.X, expand=True, side=tk.LEFT)

        frame_buttons = ttk.Frame(frame_main)
        # Button to play audio.
        ttk.Button(
            frame_buttons,
            text="Play",
            command=lambda f_id=frag_id: self.play_fragment_audio(f_id),
        ).pack(anchor=tk.W)
        # Button to copy fragment ID.
        ttk.Button(
            frame_buttons,
            text="Copy ID",
            command=lambda: self.copy_to_clipboard(frag_id),
        ).pack(anchor=tk.W)
        frame_buttons.pack(side=tk.RIGHT)

        return frame_main

    # TODO Some duplicate code from main_gui.py.
    def play_fragment_audio(self, frag_id: str) -> None:
        # TODO Read known fragment audio path from DRAL release `fragments-short-full.csv`.
        path_frag_audio_inferred = f"/Users/jon/Documents/dissertation/DRAL/release/fragments-short/{frag_id}.wav"
        sox_play_args = [path_frag_audio_inferred]
        play(sox_play_args)

    def copy_to_clipboard(self, text: str) -> None:
        self.master.clipboard_clear()
        self.master.clipboard_append(text)


root = tk.Tk()
app = Application(master=root)
app.mainloop()
