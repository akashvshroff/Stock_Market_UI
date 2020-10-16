import sqlite3
import tkinter as tk
from file_paths import *
from colours import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd


class DatabaseUI:
    def __init__(self, master):
        """
        Initialise all the data structures, set the tkinter variables and call upon fns to build the tkinter
        screen as well as the db set-up.
        """
        self.master = master
        self.stock_names = []
        self.n, self.k = None, None
        self.conn = sqlite3.connect(stocks_db)
        self.cur = self.conn.cursor()
        self.fetch_names()
        self.tkinter_setup()

    def tkinter_setup(self):
        """
        Create the tkinter window and add the various buttons. 
        """
        self.master.geometry("1100x600")
        self.master.title("Database Visualiser")
        self.master.resizable(False, False)

        # Frame
        main_frame = tk.Frame(self.master, width=1100,
                              height=600, bg=bg_primary)
        main_frame.pack()

        title = tk.Label(self.master, text='DAILY VALUE', width=50, font=(
            "Helvetica", 24, 'bold'), fg=text_colour, bg=bg_primary)
        title.place(relx=0.06, rely=0.02)

        # Left-Side

        self.canvas_plot = tk.Canvas(
            self.master, width=650, height=400, bg=bg_secondary, bd=0, highlightthickness=0)
        self.canvas_plot.place(relx=0.04, rely=0.12)

        self.from_var = tk.StringVar(self.master)
        self.from_var.set('FROM')
        self.from_option = tk.OptionMenu(
            self.master, self.from_var, '')
        self.from_option.config(bg=bg_secondary)
        self.from_option.config(fg=text_colour)
        self.from_option.config(width=14)
        self.from_option.config(activebackground=bg_secondary)
        self.from_option.config(highlightthickness=0)
        self.from_option.config(activeforeground=text_colour)
        self.from_option.config(font=("Helvetica", 18,))
        self.from_option.place(relx=0.04, rely=0.81)
        self.from_option.configure(state='disabled')

        to = tk.Label(self.master, text='TO', width=8, font=(
            "Helvetica", 18,), fg=text_colour, bg=bg_primary)
        to.place(relx=0.25, rely=0.82)

        self.to_var = tk.StringVar(self.master)
        self.to_var.set('TO')
        self.to_option = tk.OptionMenu(self.master, self.to_var, '')
        self.to_option.config(bg=bg_secondary)
        self.to_option.config(fg=text_colour)
        self.to_option.config(width=14)
        self.to_option.config(activebackground=bg_secondary)
        self.to_option.config(highlightthickness=0)
        self.to_option.config(activeforeground=text_colour)
        self.to_option.config(font=("Helvetica", 18,))
        self.to_option.place(relx=0.36, rely=0.81)
        self.to_option.configure(state='disabled')

        ok = tk.Button(self.master, text='OK', font=(
            "Helvetica", 18,), bg=green, fg=text_colour)
        ok.place(relx=0.58, rely=0.80)

        save_plot_btn = tk.Button(self.master, text='SAVE PLOT', font=(
            "Helvetica", 18,), bg=blue, fg=text_colour, width=22, command=self.save_plot)
        save_plot_btn.place(relx=0.04, rely=0.9)

        save_plot_btn = tk.Button(self.master, text='SAVE PLOT', font=(
            "Helvetica", 18,), bg=blue, fg=text_colour, width=22, command=self.save_plot)
        save_plot_btn.place(relx=0.04, rely=0.9)

        # Separator

        # Right Side

    def convert_name(self, name):
        """
        Converts a string to an acceptable field name for sqlite.
        """
        if name[0].isdigit():
            name = '_' + name
        name = ''.join([letter if letter.isalnum() or letter ==
                        '_' else '_' for letter in name])
        return name

    def fetch_names(self):
        """
        Read all the stock names from the csv file and then store it in the stock_names list.
        """
        df = pd.read_csv(share_list)
        self.stock_names = df['NAMES'].values.tolist()

    def save_plot(self):
        """
        Save the plot that is currently generated.
        """
        pass


def main():
    """
    Driver function for the program.
    """
    root = tk.Tk()
    obj = DatabaseUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
