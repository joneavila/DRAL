import tkinter as tk
import tkinter.ttk as ttk


class MeanTab(ttk.Frame):
    def __init__(self, parent, master):

        super().__init__(master)
        self.parent = parent  # Of type Application.

        frame_main = ttk.Frame(self)

        tab_type = ttk.Notebook(frame_main)
        tab_most = ttk.Frame(tab_type)
        tab_least = ttk.Frame(tab_type)
        tab_type.add(tab_most, text="Most similar")
        tab_type.add(tab_least, text="Least similar")
        tab_type.pack()

        n_to_display = 8

        # Most similar to mean
        for i in range(n_to_display):
            frag_id = self.parent.series_similarity_to_mean.index[i]
            score = self.parent.series_similarity_to_mean.iat[i]
            self.parent.create_fragment_frame(tab_most, frag_id, score).pack()
            ttk.Separator(tab_most, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

        # Least similar to mean
        for i in range(n_to_display):
            frag_id = self.parent.series_similarity_to_mean.index[-i - 1]
            score = self.parent.series_similarity_to_mean.iat[-i - 1]
            self.parent.create_fragment_frame(tab_least, frag_id, score).pack()
            ttk.Separator(tab_least, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

        frame_main.pack()
