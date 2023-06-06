# TODO Fix layout.
import tkinter as tk
import tkinter.ttk as ttk


class OverallTab(ttk.Frame):
    def __init__(self, parent, master):

        super().__init__(master)
        self.parent = parent  # Of type Application.

        frame_main = ttk.Frame(self)

        notebook_sim_type = ttk.Notebook(frame_main)
        tab_most = ttk.Frame(notebook_sim_type)
        tab_least = ttk.Frame(notebook_sim_type)
        notebook_sim_type.add(tab_most, text="Most similar")
        notebook_sim_type.add(tab_least, text="Least similar")
        notebook_sim_type.pack()

        n_to_display = 8

        # Most similar.
        for i in range(n_to_display):
            frag1_id = self.parent.df_similarity_pairs.loc[i, "frag_id1"]
            frag2_id = self.parent.df_similarity_pairs.loc[i, "frag_id2"]
            score = self.parent.df_similarity_pairs.loc[i, "similarity_score"]
            frame_pair = ttk.Frame(tab_most)
            self.parent.create_fragment_frame(frame_pair, frag1_id, score).pack(
                fill=tk.BOTH, side=tk.LEFT,
            )
            self.parent.create_fragment_frame(frame_pair, frag2_id, score).pack(
                fill=tk.BOTH, side=tk.LEFT
            )
            frame_pair.pack(fill=tk.X)
            ttk.Separator(tab_most, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

        # Least similar.
        for i in range(
            self.parent.df_similarity_pairs.shape[0] - n_to_display,
            self.parent.df_similarity_pairs.shape[0],
        ):
            frag1_id = self.parent.df_similarity_pairs.loc[i, "frag_id1"]
            frag2_id = self.parent.df_similarity_pairs.loc[i, "frag_id2"]
            score = self.parent.df_similarity_pairs.loc[i, "similarity_score"]
            frame_pair = ttk.Frame(tab_least)
            self.parent.create_fragment_frame(frame_pair, frag1_id, score).pack(
                fill=tk.BOTH, side=tk.LEFT
            )
            self.parent.create_fragment_frame(frame_pair, frag2_id, score).pack(
                fill=tk.BOTH, side=tk.LEFT
            )
            frame_pair.pack(fill=tk.X)
            ttk.Separator(tab_least, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

        frame_main.config(width=800)
        frame_main.pack()
