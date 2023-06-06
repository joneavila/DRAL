import random
import tkinter as tk
import tkinter.ttk as ttk


class SingleTab(ttk.Frame):
    def __init__(self, parent, master):

        super().__init__(master)
        self.parent = parent  # Of type Application.

        frame_left = ttk.Frame(self)

        # Entry for search, button to select random fragment.
        self.string_var_entry = tk.StringVar()
        self.string_var_entry.trace("w", self.update_treeview_with_completions)
        frame_search = ttk.Frame(frame_left)
        ttk.Label(frame_search, text="Search:").pack(side=tk.LEFT)
        entry_search = ttk.Entry(frame_search, textvariable=self.string_var_entry)
        entry_search.pack(side=tk.LEFT)
        ttk.Button(
            frame_search, text="Select random", command=self.select_random_fragment
        ).pack(side=tk.LEFT)
        frame_search.pack()

        # Treeview for fragment IDs.
        self.treeview_frags = ttk.Treeview(
            frame_left,
            selectmode="browse",
            columns=("id", "notes"),
            show="headings",
            height=8,
        )
        self.treeview_frags.heading("id", text="Fragment ID")
        self.treeview_frags.heading("notes", text="Notes")
        self.treeview_frags.bind("<<TreeviewSelect>>", self.on_select_fragment)
        self.treeview_frags.pack()

        # Frame for selected fragment.
        self.frame_current_frag = ttk.Frame(frame_left)
        self.frame_current_frag.pack()

        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frame_right = ttk.Frame(self)

        # Frame for most/least similar fragments.
        notebook_sim_type = ttk.Notebook(frame_right)
        self.frame_most_similar = ttk.Frame(notebook_sim_type)
        self.frame_least_similar = ttk.Frame(notebook_sim_type)
        notebook_sim_type.add(self.frame_most_similar, text="Most similar")
        notebook_sim_type.add(self.frame_least_similar, text="Least similar")
        notebook_sim_type.pack()

        # Add the fragments to the Treeview.
        for frag_id in self.parent.frag_ids:
            note = self.parent.get_frag_notes(frag_id)
            self.treeview_frags.insert("", tk.END, iid=frag_id, values=(frag_id, note))
        self.frag_ids_all = list(self.treeview_frags.get_children())

        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Start with the first fragment selected.
        self.treeview_frags.focus(self.frag_ids_all[0])

    def on_select_fragment(self, _: tk.Event = None) -> None:

        # Get selected fragment ID.
        frag_id_selected = self.treeview_frags.focus()

        # Update selected fragment.
        self.clear_frame(self.frame_current_frag)
        self.parent.create_fragment_frame(
            self.frame_current_frag, frag_id_selected, 0
        ).pack(expand=True, fill=tk.X, ipady=10)

        df_frag_sorted = self.parent.get_similar_to_frag(frag_id_selected)

        n_frags_to_display = 8

        # Update most similar fragments.
        self.clear_frame(self.frame_most_similar)
        for i in range(n_frags_to_display):
            frag_id = df_frag_sorted.index[i]
            similarity_score = df_frag_sorted[i]
            self.parent.create_fragment_frame(
                self.frame_most_similar, frag_id, similarity_score
            ).pack(fill=tk.X)
            ttk.Separator(self.frame_most_similar, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

        # Update least similar fragments.
        self.clear_frame(self.frame_least_similar)
        for i in range(n_frags_to_display):
            frag_id = df_frag_sorted.index[-i - 1]
            similarity_score = df_frag_sorted[-i - 1]
            self.parent.create_fragment_frame(
                self.frame_least_similar, frag_id, similarity_score
            ).pack(fill=tk.X)
            ttk.Separator(self.frame_least_similar, orient=tk.HORIZONTAL).pack(
                expand=True, fill=tk.X, ipady=10
            )

    def update_treeview_with_completions(self, *args) -> None:
        entry_value = self.string_var_entry.get()
        new_frag_ids = [
            frag_id for frag_id in self.frag_ids_all if entry_value in frag_id
        ]
        self.treeview_frags.detach(*self.treeview_frags.get_children())
        for frag_id in new_frag_ids:
            self.treeview_frags.move(frag_id, "", index=tk.END)

    def select_random_fragment(self) -> None:
        frag_id_random = random.choice(self.treeview_frags.get_children())
        self.treeview_frags.selection_set(frag_id_random)
        self.treeview_frags.focus(frag_id_random)
        self.on_select_fragment()

    def clear_frame(self, frame: ttk.Frame) -> None:
        for widgets in frame.winfo_children():
            widgets.destroy()
