# A GUI application for listening to similar DRAL fragments.
import tkinter as tk
import tkinter.ttk as ttk

import compute_similarity
import data
from gui_mean import MeanTab
from gui_overall import OverallTab
from gui_single import SingleTab
from sox.core import play


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        master.geometry("1100x1000")
        master.title("Similarity")

        self.master = master

        # Load the data.
        self.df_frags = data.read_metadata()
        df_features = data.read_features_en_es()
        self.df_similarity = compute_similarity.similarity(df_features)
        self.df_similarity_en = compute_similarity.similarity_by_language(
            df_features, "EN"
        )
        self.df_similarity_es = compute_similarity.similarity_by_language(
            df_features, "ES"
        )
        self.frag_ids = self.df_similarity.index.tolist()

        self.df_similarity_pairs = compute_similarity.similar_pairs(self.df_similarity)
        self.series_similarity_to_mean = compute_similarity.similarity_to_mean(
            df_features
        )

        self.configure_style()

        notebook_sim_type = ttk.Notebook(self.master)

        frame_single = SingleTab(self, notebook_sim_type)
        notebook_sim_type.add(frame_single, text="To fragment")

        frame_mean = MeanTab(self, notebook_sim_type)
        notebook_sim_type.add(frame_mean, text="To mean")

        frame_overall = OverallTab(self, notebook_sim_type)
        notebook_sim_type.add(frame_overall, text="Overall")

        notebook_sim_type.pack(fill=tk.BOTH, expand=True)

    def configure_style(self):
        s = ttk.Style()
        font_name = "TkDefaultFont"
        font_size = 12
        s.configure(".", font=(font_name, font_size))  # Default style.
        s.configure("bold.TLabel", font=("TkTextFont", font_size, "bold"))
        s.configure("Treeview.Heading", font=(font_name, font_size))

    def copy_to_clipboard(self, text: str) -> None:
        self.master.clipboard_clear()
        self.master.clipboard_append(text)

    def create_fragment_frame(self, master, frag_id: str, score: str):

        frame_main = ttk.Frame(master)

        frame_info = ttk.Frame(frame_main, width=350, height=350)

        # Info.
        WRAP_LEN = 350
        frag_text = self.get_frag_text(frag_id)
        frag_trans_text = self.get_frag_trans_text(frag_id)
        frag_notes = self.get_frag_notes(frag_id)

        # Fragment ID and similarity score.
        frame_title = ttk.Frame(frame_info)
        ttk.Label(frame_title, text=frag_id, style="bold.TLabel").pack(side=tk.LEFT)
        ttk.Label(frame_title, text=f"({score:.2f})").pack(side=tk.LEFT)
        frame_title.pack(anchor=tk.W)

        # Transcription text and translation transcription text.
        frame_long_texts = ttk.Frame(frame_info)
        ttk.Label(frame_long_texts, text="Text:", style="bold.TLabel").grid(
            row=0, column=0, sticky=tk.NE
        )
        ttk.Label(frame_long_texts, text=f'"{frag_text}"', wraplength=WRAP_LEN).grid(
            row=0, column=1, sticky=tk.W
        )
        ttk.Label(frame_long_texts, text="Text (trans.):", style="bold.TLabel").grid(
            row=1, column=0, sticky=tk.NE
        )
        ttk.Label(
            frame_long_texts, text=f'"{frag_trans_text}"', wraplength=WRAP_LEN
        ).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(frame_long_texts, text="Notes:", style="bold.TLabel").grid(
            row=2, column=0, sticky=tk.NE
        )
        text_notes = tk.Text(frame_long_texts, wrap=tk.WORD, width=40, height=4)
        text_notes.bind(
            "<Leave>",
            lambda e: self.save_notes(self, frag_id, text_notes.get("1.0", "end-1c")),
        )
        text_notes.grid(row=2, column=1, sticky=tk.W)
        if frag_notes != "":
            text_notes.insert(tk.INSERT, frag_notes)
        frame_long_texts.pack(anchor=tk.W)

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

    def play_fragment_audio(self, frag_id: str) -> None:
        # TODO Read known fragment audio path from DRAL release `fragments-short-full.csv`.
        path_frag_audio_inferred = f"/Users/jon/Documents/prosody_project/DRAL/release/fragments-short/{frag_id}.wav"
        sox_play_args = [path_frag_audio_inferred]
        play(sox_play_args)

    def save_notes(_: tk.Event, self, frag_id, frag_notes):
        self.df_frags.loc[frag_id, "note_function"] = frag_notes
        data.write_metadata(self.df_frags)

    def get_similar_to_frag(self, frag_id: str):
        # Sort similarity to a fragment in ascending order, excluding the same fragment
        # and fragments in a different language.
        if frag_id in self.df_similarity_en.index:
            df_frag = self.df_similarity_en.loc[frag_id]
        elif frag_id in self.df_similarity_es.index:
            df_frag = self.df_similarity_es.loc[frag_id]
        else:
            raise ValueError(f"Fragment {frag_id} not found.")
        df_frag_sorted = df_frag.sort_values(ascending=True).drop(frag_id)
        return df_frag_sorted

    def get_frag_notes(self, frag_id: str):
        note = self.df_frags.loc[frag_id, "note_function"]
        if isinstance(note, str):
            return note
        else:
            return ""

    def get_frag_text(self, frag_id: str) -> str:
        frag_text = self.df_frags.loc[frag_id, "text"]
        frag_text_no_quotes = frag_text.replace('"', "'")
        return frag_text_no_quotes

    def get_frag_trans_text(self, frag_id: str) -> str:
        frag_trans = self.df_frags.loc[frag_id, "trans_id"]
        return self.get_frag_text(frag_trans)


root = tk.Tk()
app = Application(master=root)
app.mainloop()
