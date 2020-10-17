import sqlite3
import tkinter as tk
from tkinter import messagebox
from file_paths import *
import retrieve_data
from colours import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
import sys
import os
import random


class DatabaseUI:
    def __init__(self, master):
        """
        Initialise all the data structures, set the tkinter variables and call upon fns to build the tkinter
        screen as well as the db set-up.
        """
        self.master = master
        self.stock_names = []
        self.dates = []
        self.ratios = []
        self.dates_iso = []
        self.n, self.k = None, None
        self.fig = None
        self.conn = sqlite3.connect(stocks_db)
        self.cur = self.conn.cursor()
        self.fetch_names()
        self.get_basic_info()
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

        title = tk.Label(self.master, text='PLOT', width=25, font=(
            "Helvetica", 24, 'bold'), fg=text_colour, bg=bg_primary)
        title.place(relx=0.1, rely=0.02)

        # Left-Side

        self.canvas_plot = tk.Canvas(
            self.master, width=650, height=400, bg=bg_secondary, bd=0, highlightthickness=0)
        self.canvas_plot.place(relx=0.04, rely=0.12)

        self.from_var = tk.StringVar(self.master)
        self.from_var.set('START')
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
        self.to_var.set('END')
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

        self.ok = tk.Button(self.master, text='OK', font=(
            "Helvetica", 18,), bg=green, fg=text_colour, state=tk.DISABLED, command=self.show_plot)
        self.ok.place(relx=0.58, rely=0.80)

        save_plot_btn = tk.Button(self.master, text='SAVE PLOT', font=(
            "Helvetica", 18,), bg=blue, fg=text_colour, width=21, command=self.save_plot)
        save_plot_btn.place(relx=0.04, rely=0.9)

        refresh_btn = tk.Button(self.master, text='REFRESH DATA', font=(
            "Helvetica", 18,), bg=red, fg=text_colour, width=22, command=lambda: self.refresh_data("Refreshing data", self.n, self.k, False))
        refresh_btn.place(relx=0.34, rely=0.9)

        # Separator

        canvas_sep = tk.Canvas(
            self.master, width=10, height=550, bg=bg_secondary, bd=0, highlightthickness=0)
        canvas_sep.place(relx=0.65, rely=0.04)

        # Right Side

        daily = tk.Label(self.master, text='DAILY VALUE', font=(
            "Helvetica", 24, 'bold'), fg=text_colour, bg=bg_primary)
        daily.place(relx=0.73, rely=0.02)

        info = "View a line graph of the average of the daily values of the previous K days over the previous N days for each day for K < N.\nChoose a stock to view its graph and choose a start and end date!\nP.S - hit refresh to get data for the last 10 days."
        info_label = tk.Message(self.master, text=info, bg=bg_primary,
                                fg=text_colour, highlightthickness=0, font=("Helvetica", 16), width=325)
        info_label.place(relx=0.67, rely=0.12)

        stocks = tk.Label(self.master, text='STOCKS:',
                          bg=bg_primary, fg=text_colour, font=("Helvetica", 18))
        stocks.place(relx=0.68, rely=0.49)

        self.stock_choice_var = tk.StringVar()
        self.stock_choice_var.set("CHOOSE")
        self.stock_choice = tk.OptionMenu(
            self.master, self.stock_choice_var, *self.stock_names)
        self.stock_choice.config(bg=bg_secondary)
        self.stock_choice.config(fg=text_colour)
        self.stock_choice.config(width=16)
        self.stock_choice.config(activebackground=bg_secondary)
        self.stock_choice.config(highlightthickness=0)
        self.stock_choice.config(activeforeground=text_colour)
        self.stock_choice.config(font=("Helvetica", 16,))
        self.stock_choice.place(relx=0.68, rely=0.57)

        stock_btn = tk.Button(self.master, text='OK',  font=(
            "Helvetica", 16), bg=green, fg=text_colour, command=self.get_data)
        stock_btn.place(relx=0.92, rely=0.56)

        stocks = tk.Label(self.master, text='CHANGE K,N:',
                          bg=bg_primary, fg=text_colour, font=("Helvetica", 18))
        stocks.place(relx=0.68, rely=0.69)

        change_btn = tk.Button(self.master, text='EDIT', font=(
            "Helvetica", 16), bg=blue, fg=text_colour, command=self.enable_n_k)
        change_btn.place(relx=0.91, rely=0.68)

        self.k_var = tk.StringVar()
        self.k_var.set(self.k)

        self.n_var = tk.StringVar()
        self.n_var.set(self.n)

        k_label = tk.Label(self.master, text='K:', font=(
            "Helvetica", 18), bg=bg_primary, fg=text_colour)
        self.k_entry = tk.Entry(self.master, textvariable=self.k_var,
                                bg=bg_secondary, disabledbackground=bg_secondary, fg=text_colour, font=(
                                    "Helvetica", 18), width=3)
        k_label.place(relx=0.68, rely=0.80)
        self.k_entry.place(relx=0.72, rely=0.80)
        self.k_entry.configure(state='disabled')

        n_label = tk.Label(self.master, text='N:', font=(
            "Helvetica", 18), bg=bg_primary, fg=text_colour)
        self.n_entry = tk.Entry(self.master, textvariable=self.n_var,
                                bg=bg_secondary, disabledbackground=bg_secondary, fg=text_colour, font=(
                                    "Helvetica", 18), width=3)
        n_label.place(relx=0.78, rely=0.80)
        self.n_entry.place(relx=0.82, rely=0.80)
        self.n_entry.configure(state='disabled')

        self.n_k_btn = tk.Button(self.master, text='OK', font=(
            "Helvetica", 16), bg=green, fg=text_colour, state=tk.DISABLED, command=self.change_n_k)
        self.n_k_btn.place(relx=0.92, rely=0.79)

        quit_btn = tk.Button(self.master, text='QUIT PROGRAM', font=(
            "Helvetica", 18), bg=red, fg=text_colour, width=22, command=self.quit_prg)
        quit_btn.place(relx=0.68, rely=0.9)

    def get_basic_info(self):
        """
        Get the k,n from the database.
        """
        info = self.cur.execute('SELECT k,n FROM info where id = 1')
        row = info.fetchone()
        self.k, self.n = row

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

    def get_data(self):
        """
        Gets the dates and ratios for a stock.
        """
        self.ratios = []
        self.dates = []
        self.dates_iso = []
        if self.stock_choice_var.get() == 'CHOOSE':
            messagebox.showerror(
                "ERROR", "Please choose a stock from the list first.")
            return
        name = self.convert_name(self.stock_choice_var.get())
        query = 'SELECT date,ratio from {}'.format(name)
        try:
            raw_data = self.cur.execute(query)
            data = raw_data.fetchall()
            if len(data) in [0, 1]:
                messagebox.showerror(
                    "ERROR", "No data exists for this stock. Please run refresh data and retry or choose another."
                )
                return
            for date, ratio in data:
                rev = list(date.split('-'))[::-1]
                formatted = '{}/{}/{}'.format(*rev)
                self.dates_iso.append(date)
                self.dates.append(formatted)
                self.ratios.append(ratio)
            self.show_dates()
            self.show_plot()
        except:
            messagebox.showerror(
                "ERROR", "An error occured. Please run refresh data and retry."
            )

    def show_dates(self):
        """
        Display the dates in the option menu.
        """
        self.ok.configure(state='normal')
        self.to_option.configure(state='normal')
        self.from_option.configure(state='normal')
        end = len(self.dates) - 1
        self.from_option['menu'].delete(0, 'end')
        self.to_option['menu'].delete(0, 'end')
        for id, date in enumerate(self.dates):
            if id != end:
                self.from_option['menu'].add_command(
                    label=date, command=tk._setit(self.from_var, date))
            if id:
                self.to_option['menu'].add_command(
                    label=date, command=tk._setit(self.to_var, date))
        self.from_var.set(self.dates[0])
        self.to_var.set(self.dates[-1])

    def show_plot(self):
        """
        Gets the dates and shows the plots.
        """
        from_date = self.from_var.get()
        to_date = self.to_var.get()
        if from_date == to_date:
            messagebox.showerror(
                'ERROR', 'Start and end date cannot be the same. Change either one.')
            return
        from_id = self.dates.index(from_date)
        to_id = self.dates.index(to_date)
        values = self.ratios[from_id:to_id + 1]
        labels = [
            f'{date} 00:00:00' for date in self.dates_iso[from_id:to_id+1]]
        dates = mdates.num2date(mdates.datestr2num(labels))
        self.fig = Figure(figsize=(6.5, 4), dpi=100)
        subplot = self.fig.add_subplot(111)
        subplot.plot(dates, values, '.-')
        title = f'Ratio Line Graph - {self.stock_choice_var.get()}'
        subplot.set_title(title, loc='left')
        subplot.xaxis_date()
        subplot.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
        self.fig.autofmt_xdate()
        line_plot = FigureCanvasTkAgg(self.fig, self.master)
        line_plot.get_tk_widget().place(relx=0.04, rely=0.12)
        line_plot.draw()
        toolbar = NavigationToolbar2Tk(line_plot, self.master)
        toolbar.place(relx=0.40, rely=0.13)

    def save_plot(self):
        """
        Save the plot that is currently generated.
        """
        if self.fig is None or self.stock_choice_var.get() == 'CHOOSE':
            messagebox.showerror(
                'ERROR', 'Generate a plot for a stock first.')
            return
        name = self.stock_choice_var.get()
        from_ = self.from_var.get()
        to = self.to_var.get()
        if from_ == to:
            messagebox.showerror(
                'ERROR', 'Start and end date cannot be the same. Change either one.')
            return
        from_ = ''.join([l if l != '/' else '-' for l in from_])
        to = ''.join([l if l != '/' else '-' for l in to])
        path_ = f'{name}_{from_}_{to}.png'
        file_path = os.path.join(images, path_)
        self.fig.savefig(file_path)
        messagebox.showinfo(
            "SUCCESS", f"Your file has been saved as {file_path} under the saved_plots folder.")

    def refresh_data(self, message, n, k, reset):
        """
        Fetch data for the previous 10 days and then refresh the plot.
        """
        if not reset:
            text = f"{message} means all the data must be regenerated, the program will inform you when it is done and will be unresponsive (for a few moments) till then."
        else:
            text = f'{message} means all the data must be regenerated and the previous data is all cleared. New data will be generated for a month.'
        if messagebox.askokcancel("ARE YOU SURE?", text):
            self.k, self.n = k, n
            num = 10 if not reset else 30
            retrieve_data.main(num, self.n, self.k, reset)
            self.disable_n_k()
            self.reset_options()
            messagebox.showinfo(
                "SUCCESS", "Data has been officially fetched, please select stock again.")
        else:
            self.disable_n_k()

    def reset_options(self):
        """
        Resets the stock choice and the dates.
        """
        self.stock_choice_var.set('CHOOSE')
        self.from_option['menu'].delete(0, 'end')
        self.to_option['menu'].delete(0, 'end')
        self.to_var.set("END")
        self.from_var.set("START")

    def enable_n_k(self):
        """
        Enable the n and k entry fields.
        """
        self.k_entry.configure(state='normal')
        self.n_entry.configure(state='normal')
        self.n_k_btn.configure(state='normal')

    def disable_n_k(self):
        """
        Resets the entries and disables everything.
        """
        self.k_var.set(self.k)
        self.n_var.set(self.n)
        self.k_entry.configure(state='disabled')
        self.n_entry.configure(state='disabled')
        self.n_k_btn.configure(state='disabled')

    def change_n_k(self):
        """
        Change n and k and then fetch the data with the new format.
        """
        k, n = int(self.k_var.get()), int(self.n_var.get())
        if k == self.k and n == self.n:
            messagebox.showinfo(
                "INFO", "You haven't changed K or N!"
            )
            self.disable_n_k()
            return
        if k >= n:
            messagebox.showerror(
                "ERROR", "K must be less than N."
            )
            self.disable_n_k()
            return
        self.refresh_data("Changing N or K", n, k, True)

    def quit_prg(self):
        """
        Quits the program and closes the connection.
        """
        self.conn.close()
        sys.exit()


def main_ui():
    """
    Driver function for the program.
    """
    root = tk.Tk()
    obj = DatabaseUI(root)
    root.mainloop()


if __name__ == '__main__':
    main_ui()
