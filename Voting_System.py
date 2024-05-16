import tkinter as tk
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from tkinter import messagebox

class VotingSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Voting System")
        self.master.configure(bg="#F0F0F0")

        # Create the posts and candidates
        self.posts = ["Post 1", "Post 2", "Post 3"]
        self.candidates = {
            "Post 1": ["Candidate 1", "Candidate 2", "Candidate 3"],
            "Post 2": ["Candidate 4", "Candidate 5"],
            "Post 3": ["Candidate 6", "Candidate 7", "Candidate 8"]
        }

        # Initialize Firebase
        self.initialize_firebase()

        # Create the widgets
        self.post_label = tk.Label(self.master, text="Select a Post:", font=("Garamond", 14, "bold"), bg="#F0F0F0",fg="#FF0000")
        self.post_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.post_var = tk.StringVar()
        self.post_var.set(self.posts[0])

        # Create the drop-down menu
        self.post_dropdown = tk.OptionMenu(self.master, self.post_var, *self.posts, command=self.update_candidates)
        self.post_dropdown.config(width=20, font=("Garamond", 15), bg="#F0F0F0", relief="solid")
        self.post_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        self.candidate_labels = []
        self.vote_buttons = []
        self.result_button = None
        self.reset_button = None

        self.update_candidates()

    def initialize_firebase(self):
        # Initialize Firebase using the downloaded credentials file
        cred = credentials.Certificate("")
        firebase_admin.initialize_app(cred, {
            'databaseURL': ''
        })

    def update_candidates(self, *args):
        # Clear the previous candidate labels and buttons
        for label in self.candidate_labels:
            label.grid_forget()
        for button in self.vote_buttons:
            button.grid_forget()
        if self.result_button:
            self.result_button.grid_forget()
        if self.reset_button:
            self.reset_button.grid_forget()

        # Get the selected post and candidates
        selected_post = self.post_var.get()
        selected_candidates = self.candidates[selected_post]

        # Display the candidates and vote buttons
        self.candidate_labels = []
        self.vote_buttons = []
        for index, candidate in enumerate(selected_candidates, start=1):
            candidate_label = tk.Label(self.master, text=candidate, font=("Franklin Gothic", 15), bg="#F0F0F0")
            candidate_label.grid(row=index, column=0, sticky="w", pady=15, padx=10)
            self.candidate_labels.append(candidate_label)

            vote_button = tk.Button(self.master, text="Vote", command=lambda c=candidate: self.confirm_vote(c))
            vote_button.config(width=10, font=("Franklin Gothic", 11), bg="#4CAF50", fg="#FFFFFF", activebackground="#45a049",
                               activeforeground="#FFFFFF")
            vote_button.grid(row=index, column=1 , sticky="w", padx=10)
            self.vote_buttons.append(vote_button)

        # Display the result button
        self.result_button = tk.Button(self.master, text="Show Result", command=self.show_result)
        self.result_button.config(width=20, font=("Franklin Gothic", 12), bg="#2196F3", fg="#FFFFFF", activebackground="#1976D2",
                                  activeforeground="#FFFFFF")
        self.result_button.grid(row=len(selected_candidates) + 1, column=0, columnspan=2, pady=10, padx=10)

        # Display the reset button
        self.reset_button = tk.Button(self.master, text="Reset Votes", command=self.reset_votes)
        self.reset_button.config(width=20, font=("Franklin Gothic", 12), bg="#F44336", fg="#FFFFFF", activebackground="#D32F2F",
                                 activeforeground="#FFFFFF")
        self.reset_button.grid(row=len(selected_candidates) + 2, column=0, columnspan=2, pady=5, padx=10)

    def confirm_vote(self, candidate):
        answer = messagebox.askyesno("Confirmation", f"Are you sure you want to vote for {candidate}?")
        if answer:
            self.vote(candidate)

    def vote(self, candidate):
        post = self.post_var.get()
        ref = db.reference(f'/votes/{post}/{candidate}')
        votes = ref.get()

        if votes is None:
            ref.set(1)
        else:
            ref.set(votes + 1)

        messagebox.showinfo("Success", f"Vote for {candidate} registered!")


    def show_result(self):
        post = self.post_var.get()
        ref = db.reference(f'/votes/{post}')
        results = ref.order_by_value().get()

        # Create a new window for displaying the results
        result_window = tk.Toplevel(self.master)
        result_window.title("Voting Results")
        result_window.configure(bg="#F0F0F0")

        # Create a Treeview widget to display the results
        votes_table = ttk.Treeview(result_window, columns=("Candidate", "Votes"), show="headings")
        votes_table.heading("Candidate", text="Candidate", anchor="center")
        votes_table.heading("Votes", text="Votes", anchor="center")
        votes_table.column("Candidate", width=200, anchor="center")
        votes_table.column("Votes", width=100, anchor="center")
        votes_table.pack()

        for candidate, votes in results:
            votes_table.insert("", "end", values=(candidate, votes))

    def reset_votes(self):
        answer = messagebox.askyesno("Confirmation", "Are you sure you want to reset all votes?")
        if answer:
            ref = db.reference('/votes')
            ref.delete()
            messagebox.showinfo("Success", "All votes have been reset!")



if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#F0F0F0")
    voting_system = VotingSystem(root)
    root.mainloop()
