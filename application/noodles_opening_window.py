# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 23:56:06 2020

@author: John
"""

from tkinter import *
from PIL import ImageTk, Image


window = Tk()
window.title("Noodles Password Vault")

#creating widgets
name_shown = Label(window, text="Noodle Password Vault", font=("Helvetica", 50))

username_text = Label(window, text="Username: ", font=("Helvetica", 16))
username_entry = Entry(window, width=35, borderwidth=5)

pw_text = Label(window, text="Password: ", font=("Helvetica", 16))
pw_entry = Entry(window, width=35, borderwidth=5)

log_in_button = Button(window, text="Log in", padx=40, pady=20)

#placing
name_shown.grid(row=0, column=0, columnspan = 3)

username_text.grid(row=1, column=0)
username_entry.grid(row=1, column=1, pady=10)

pw_text.grid(row=2, column=0)
pw_entry.grid(row=2, column=1, pady=10)

log_in_button.grid(row=3, column=1)

window.mainloop()