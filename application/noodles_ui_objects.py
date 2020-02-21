import tkinter as tk
from .vault import Vault

#LARGE_FONT = ("Verdana", 12)
TRUE_FONT = "Comic Sans MS"

# funciton to combine functions


def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func


class NoodlePassword(tk.Tk):

    def __init__(self, *args, **kwargs):
        self.vault = Vault()

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="black_noodles_white_Xbg_icon.ico")
        tk.Tk.wm_title(self, "Noodle Password Vault")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, InsidePage, ForgotPassword, SignUp):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def log_in(self, user, pw):
        if not self.vault.log_in():
            return False
        self.show_frame() #next frame
        return True

# functions for the buttons
def log_in():
    return


def clear_entry(*args):
    for e in args:
        e.delete(0, 'end')


# def sign_up():
#    return

# def forgot_pw():
#    return

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        #label.pack(pady=10, padx=10)

        name_shown = tk.Label(
            self, text="Noodle Password Vault", font=(TRUE_FONT, 50))

        username_text = tk.Label(self, text="Username: ", font=(TRUE_FONT, 16))
        username_entry = tk.Entry(self, width=35, borderwidth=5)

        pw_text = tk.Label(self, text="Password: ", font=(TRUE_FONT, 16))
        # show="*" changes input to *
        pw_entry = tk.Entry(self, show="◕", width=35, borderwidth=5)

        log_in_button = tk.Button(self, text="Log in", padx=20, pady=10,
                                  command=log_in)

        sign_up_button = tk.Button(self, text="Sign Up", padx=10, pady=10,
                                   command=lambda: controller.show_frame(SignUp))

        forgot_pw_button = tk.Button(self, text="Forgot Password?", padx=10, pady=10,
                                     command=lambda: controller.show_frame(ForgotPassword))

        # testing for multiple pages
        new_page_button = tk.Button(self, text="Load next page",
                                    command=lambda: controller.show_frame(InsidePage))

        # placing
        name_shown.grid(row=0, column=0, columnspan=3)

        username_text.grid(row=1, column=0)
        username_entry.grid(row=1, column=1, pady=10)

        pw_text.grid(row=2, column=0)
        pw_entry.grid(row=2, column=1, pady=10)

        log_in_button.grid(row=3, column=1)

        sign_up_button.grid(row=4, column=1)

        forgot_pw_button.grid(row=5, column=1)

        new_page_button.grid(row=6, column=1)


class InsidePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        web_column_title = tk.Label(self, text="Website", background="blue")
        buttons = []
        for i in range(6):
            buttons.append(tk.Button(self, text="Button %s" %
                                     (i+1,), background="green"))
        other1 = tk.Label(self, text="Password Info")
        main = tk.Frame(self, background="blue")

        web_column_title.grid(row=0, column=0, rowspan=2, sticky="nsew")
        other1.grid(row=0, column=1, columnspan=2, sticky="nsew")
        buttons[0].grid(row=2, column=0, sticky="nsew")
        buttons[1].grid(row=3, column=0, sticky="nsew")
        buttons[2].grid(row=4, column=0, sticky="nsew")
        buttons[3].grid(row=5, column=0, sticky="nsew")
        buttons[4].grid(row=6, column=0, sticky="nsew")
        buttons[5].grid(row=7, column=0, sticky="nsew")
        main.grid(row=2, column=2, columnspan=2, rowspan=6)

        for row in range(8):
            self.grid_rowconfigure(row, weight=1)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

        back_page_button = tk.Button(self, text="Go back to original",
                                     command=lambda: controller.show_frame(StartPage))

        back_page_button.grid(row=8, column=2)


class ForgotPassword(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        forgot_pw_title = tk.Label(
            self, text="Forgot Password?", font=(TRUE_FONT, 50))

        username_text = tk.Label(self, text="Username: ", font=(TRUE_FONT, 16))
        username_entry = tk.Entry(self, width=35, borderwidth=5)

        username_confirm = tk.Label(
            self, text="Confirm Username: ", font=(TRUE_FONT, 16))
        username_confirm_entry = tk.Entry(self, width=35, borderwidth=5)

        submit_button = tk.Button(self, text="Submit", padx=40, pady=20,
                                  command=log_in)

        back_button = tk.Button(self, text="Nvm", padx=10, pady=10,
                                command=lambda: controller.show_frame(StartPage))

        # placing
        forgot_pw_title.grid(row=0, column=0, columnspan=3)

        username_text.grid(row=1, column=0)
        username_entry.grid(row=1, column=1, pady=10)

        username_confirm.grid(row=2, column=0)
        username_confirm_entry.grid(row=2, column=1, pady=10)

        submit_button.grid(row=3, column=1)

        back_button.grid(row=4, column=1)


class SignUp(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        signup_title = tk.Label(self, text="Sign Up", font=(TRUE_FONT, 50))

        username_text = tk.Label(
            self, text="Enter Username: ", font=(TRUE_FONT, 16))
        username_entry = tk.Entry(self, width=35, borderwidth=5)

        pw_text = tk.Label(self, text="Enter Password: ", font=(TRUE_FONT, 16))
        pw_entry = tk.Entry(self, show="◕", width=35, borderwidth=5)

        pw_text_confirm = tk.Label(
            self, text="Re-enter Password: ", font=(TRUE_FONT, 16))
        pw_confirm_entry = tk.Entry(self, show="◕", width=35, borderwidth=5)

        submit_button = tk.Button(self, text="Submit", padx=40, pady=20,
                                  command=log_in)

        back_button = tk.Button(self, text="Nvm", padx=10, pady=10,
                                command=lambda: combine_funcs(controller.show_frame(StartPage), clear_entry(username_entry, pw_entry, pw_confirm_entry)))

        # placing
        signup_title.grid(row=0, column=0, columnspan=2)

        username_text.grid(row=1, column=0)
        username_entry.grid(row=1, column=1, pady=10)

        pw_text.grid(row=2, column=0)
        pw_entry.grid(row=2, column=1, pady=10)

        pw_text_confirm.grid(row=3, column=0)
        pw_confirm_entry.grid(row=3, column=1, pady=10)

        submit_button.grid(row=4, column=1)

        back_button.grid(row=5, column=1)


app = NoodlePassword()
app.mainloop()
