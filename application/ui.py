import tkinter as tk
from tkinter import TkVersion, PhotoImage, Tk, messagebox, Canvas
from PIL import ImageTk, Image  
import sys, os, platform
import time


TRUE_FONT = "Arial"

# Global variables
_assetdir = os.path.join(os.path.dirname(__file__), 'assets')
_security_questions_1 = ['  Are you single? If so, why?',
                         '  Why did you forget your password?',
                         '  What is your favorite color?',
                         '  What is your mother\'s maiden name?',
                         '  Who is your favorite CS professor?']
_security_questions_2 = ['  What is your favorite TV program?',
                         '  What team do you love to see lose?',
                         '  Where did you meet your spouse?',
                         '  Who is your least favorite person?',
                         '  Where did you have your first kiss?']

_sample_user_info = [("google.com", "DevenGay", "IHateKneegrows", "today"), ("urmom.com", "devenxtian", "gay", "yesterday")]

# Placeholder functions
def __query_login(username, password):
    return True
    
def __fetch_website_list(username, password):
    return ["google.com", "yahoo.com"]
    
def __get_user_information(input):
    return False

# Utility functions
def _log_in(username, password):
    if __query_login(username, password):
        return True
    else:
        return False
    raise NotImplementedError
    
def _clear_entry(username_entry, pw_entry, pw_confirm_entry):
    username_entry.delete(0, 'end')
    pw_entry.delete(0, 'end')
    pw_confirm_entry.delete(0, 'end')
    
def _clear_main_page(username_entry, pw_entry):
    username_entry.delete(0, 'end')
    pw_entry.delete(0, 'end')
    
def _reset_password(answer_1, answer_2, new_password):
    return True
    raise NotImplementedError
    
def _delete_login(website):
    raise NotImplementedError 
    
def _log_out(controller):
    if messagebox.askokcancel("Confirmation", "Do you want to log out?"):    
        controller.show_frame(StartPage)
        raise NotImplementedError  

def _combine_funcs(*funcs):
    def _combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return _combined_func
    
def _fetch_login_information(website):
    return ("google.com", "DevenGay", "IHateKneegrows", "today")
    raise NotImplementedError
    #return (website, username, password, update_time)
    
def _fetch_username_information(username):
    if __get_user_information(username):
        return True
    else:
        return False
    raise NotImplementedError
    
def _quit():  
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    application_process.destroy()

'''
def _update_website_list(lst):
    global _website_list
    _website_list = lst
    return _website_list
'''
    

# highlight on hover
class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.defaultForeground = self["foreground"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']
        self['foreground'] = self['activeforeground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
        self['foreground'] = self.defaultForeground


# scrollable button list
class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, width=200, height=470)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class NoodlePasswordVault(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        tk.Tk.wm_title(self, "Noodles Password Vault")
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        self.user_password_information = {}
        
        for F in (StartPage, 
                  #InsidePage, 
                  ForgotPassword, SignUp, AnswerSecurityQuestions, CreateSecurityQuestions, AddPassword):
        
            frame = F(self.container, self)
        
            self.frames[F] = frame
        
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]   
        frame.tkraise()
    
    def create_inside(self):
        if (InsidePage in self.frames.keys()):
            self.frames[InsidePage].destroy()
            
        self.user_password_information = _sample_user_info
        
        inside_frame = InsidePage(self.container, self, self.user_password_information)
        self.frames[InsidePage] = inside_frame
        inside_frame.grid(row=0, column=0, sticky="nsew")
        
    def restart_inside(self):
        self.create_inside()
        self.show_frame(InsidePage)
        
        
    def fetch_login_information(self, website):
        return self.user_password_information[website]
        #return (website, username, password, update_time)

class StartPage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # error message variable
        flag = 0
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # import logo 
        iconfile = os.path.join(_assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((200, 200), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        
        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        self.username_entry = tk.Entry(self, width=26, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575', highlightthickness=0)
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        self.pw_entry = tk.Entry(self, borderwidth=0, show="◕", width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575', highlightthickness=0) #show="*" changes input to *
        pw_text = tk.Label(self, text="Password", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # incorrect input
        self.error_text = tk.Label(self, text="The username or password you entered is incorrect or invalid.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # forgot password button
        forgot_pw_button = HoverButton(self, text="Forgot Password?", padx=-10, pady=-10, highlightthickness=0, command=lambda: _combine_funcs(controller.show_frame(ForgotPassword), _clear_main_page(self.username_entry, self.pw_entry)), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        
        # log in button
        log_in_button_path = os.path.join(_assetdir, 'log_in.png')
        log_in_button_image = Image.open(log_in_button_path)
        log_in_button_resized = log_in_button_image.resize((250, 47), Image.ANTIALIAS)
        log_in_button_final = ImageTk.PhotoImage(log_in_button_resized)
        log_in_button = tk.Button(self, image=log_in_button_final, padx=-10, pady=-5, borderwidth=0, background='#FFFFFF', command=lambda: self.query_login(controller, self.username_entry, self.pw_entry))
        log_in_button.image = log_in_button_final # prevent garbage collection

        # sign up button
        sign_up_button_path = os.path.join(_assetdir, 'sign_up_home_page.png')
        sign_up_button_image = Image.open(sign_up_button_path)
        sign_up_button_resized = sign_up_button_image.resize((250, 47), Image.ANTIALIAS)
        sign_up_button_final = ImageTk.PhotoImage(sign_up_button_resized)
        sign_up_button = tk.Button(self, image=sign_up_button_final, padx=-10, pady=-5, command=lambda: _combine_funcs(controller.show_frame(SignUp), _clear_main_page(self.username_entry, self.pw_entry)), background='#FFFFFF', borderwidth=0)
        sign_up_button.image = sign_up_button_final # prevent garbage collection

        # page transition testing
        #new_page_button = HoverButton(self, text="Load next page", command=lambda: controller.show_frame(InsidePage), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        
        # placement       
        logo.place(x=300, y=10)
        
        username_text.place(x=275, y=220)
        self.username_entry.place(x=279, y=240)
        username_entryline.place(x=272, y=230)
        
        pw_text.place(x=275, y=265)
        self.pw_entry.place(x=279, y=285)
        pw_entryline.place(x=272, y=275)
        
        log_in_button.place(x=273, y=335)
        
        sign_up_button.place(x=273, y=380)
        
        forgot_pw_button.place(x=343, y=430)
        
    def query_login(self, controller, username, password):
        if _log_in(username.get(), password.get()):
            username.delete(0, 'end')
            password.delete(0, 'end')
            self.error_text.config(foreground='#FFFFFF')
                                   
            controller.create_inside()
            controller.show_frame(InsidePage)
        else:
            self.error_text.place(x=300, y=310)
            self.error_text.config(foreground='#9B1C31')


# NEEDS WORK
class InsidePage(tk.Frame):
    def __init__(self, master, controller, info, startPage=None):
        tk.Frame.__init__(self, master)
        self.startPage = StartPage
        
        self.parent = controller
        
        
        # default displayed values
        self.website = ""
        self.password = tk.StringVar()
        self.username = ""
        self.update_time = ""
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # title
        self.title = tk.Label(self, text="Login Details", font=(TRUE_FONT, 18, "bold"), background='#FFFFFF', foreground='#757575')
        
                              
        #add password button                      
        self.add_new_password_button = tk.Button(self, text="Add New Password", font=TRUE_FONT, height=1, width=24, 
                                                 activebackground='#FFFFFF', activeforeground='#40c4ff', relief=tk.FLAT, 
                                                 bg='#42D3FC', fg='#757575', command=lambda: controller.show_frame(AddPassword))
                              
                              
        # side scrollbar
        self.website_list = VerticalScrolledFrame(self)
        
        self.user_info = info
        
        self.current_index = None
        
        # scrollbar contents
        self.lis = []
        
        
        for website in self.user_info:
            self.lis.append(website[0])
        
        for i in range(len(self.lis)):
            btn = tk.Button(self.website_list.interior, height=1, width=20, relief=tk.FLAT, 
                bg='#FFFFFF', fg='#757575',
                font=TRUE_FONT, text=self.lis[i],
                command=lambda i=i: self.getinfo(i),
                activebackground='#FFFFFF', activeforeground='#40c4ff')
            btn.pack(padx=10, pady=5, side=tk.TOP)
        
        # login information
        self.website_text = tk.Label(self, text="Website: " + self.website, font=(TRUE_FONT, 12), background='#FFFFFF', foreground='#757575')
        self.username_text = tk.Label(self, text="Username: " + self.username, font=(TRUE_FONT, 12), background='#FFFFFF', foreground='#757575')
        self.password_text = tk.Label(self, text="Password: " + self.password.get(), font=(TRUE_FONT, 12), background='#FFFFFF', foreground='#757575')
        self.update_time_text = tk.Label(self, text="Last Updated: " + self.update_time, font=(TRUE_FONT, 12), background='#FFFFFF', foreground='#757575')
        
        # delete button
        delete_button_path = os.path.join(_assetdir, 'delete_login.png')
        delete_button_image = Image.open(delete_button_path)
        delete_button_resized = delete_button_image.resize((143, 47), Image.ANTIALIAS)
        delete_button_final = ImageTk.PhotoImage(delete_button_resized)
        self.delete_button = tk.Button(self, image=delete_button_final, padx=20, pady=10, borderwidth=0, background='#FFFFFF', command=lambda:_combine_funcs(self.remove_password(), controller.restart_inside()))
        self.delete_button.image = delete_button_final # prevent garbage collection
        
        # show password button
        password_button_path = os.path.join(_assetdir, 'show_password.png')
        password_button_image = Image.open(password_button_path)
        password_button_resized = password_button_image.resize((143, 47), Image.ANTIALIAS)
        password_button_final = ImageTk.PhotoImage(password_button_resized)
        self.password_button = tk.Button(self, image=password_button_final, padx=20, pady=10, borderwidth=0, background='#FFFFFF', command=lambda: self.reveal_password())
        self.password_button.image = password_button_final # prevent garbage collection
        
        # log out button
        log_out_button_path = os.path.join(_assetdir, 'log_out.png')
        log_out_button_image = Image.open(log_out_button_path)
        log_out_button_resized = log_out_button_image.resize((143, 47), Image.ANTIALIAS)
        log_out_button_final = ImageTk.PhotoImage(log_out_button_resized)
        self.log_out_button = tk.Button(self, image=log_out_button_final, padx=20, pady=10, borderwidth=0, background='#FFFFFF', command=lambda: _log_out(controller))
        self.log_out_button.image = log_out_button_final # prevent garbage collection
        
        # placement
        self.add_new_password_button.place(x=0, y=0)
        
        self.website_list.place(x=0, y=30)
        
        self.title.place(x=450, y=20)
        
        self.website_text.place(x=280, y=100)
        self.username_text.place(x=280, y=150)
        self.password_text.place(x=280, y=200)
        self.update_time_text.place(x=280, y=250)
        
        self.log_out_button.place(x=647, y=350)
        self.password_button.place(x=647, y=400)
        self.delete_button.place(x=647, y=450)
    
    # fetches login information    
    def getinfo(self, index):
        self.current_index = index
        
        login_information = self.parent.fetch_login_information(index)
        #raise NotImplementedError
      
        self.website_text.config(text="Website: " + login_information[0])
        self.username_text.config(text="Username: " + login_information[1])
        display_password = "◕" * len(login_information[2])
        self.password.set(login_information[2])
        self.password_text.config(text="Password: " + display_password)
        self.update_time_text.config(text="Last Updated: " + login_information[3])       
        
        
    def remove_password(self):
        if self.current_index is None:
            return
        #self.parent.user_password_information.append((website, username, pw, "today"))
        _sample_user_info.remove(_sample_user_info[self.current_index])
        #quit_page(self)
    
    
    def reveal_password(self):
        self.password_text.config(text="Password: " + self.password.get())
        
    def update_list(self):
        self.lis = _website_list.split("`")


class ForgotPassword(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # title
        title = tk.Label(self, text="Did you forget your password?", font=(TRUE_FONT, 22), background='#FFFFFF', foreground='#40c4ff')
        subtitle = tk.Label(self, text="Don't worry, it happens to the best of us. Enter the username you are using\n\nbelow, relax, and we will get your account back in a jiffy.", font=(TRUE_FONT, 9), background='#FFFFFF', foreground='#757575')
        
        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        self.username_entry = tk.Entry(self, width=26, highlightthickness=0, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 11, "bold"), background='#FFFFFF', foreground='#757575')
        
        # request button
        request_path = os.path.join(_assetdir, 'request_password.png')
        request_image = Image.open(request_path)
        request_resized = request_image.resize((250, 47), Image.ANTIALIAS)
        request_final = ImageTk.PhotoImage(request_resized)
        request_button = tk.Button(self, image=request_final, padx=-10, pady=-5, borderwidth=0, background='#FFFFFF', command=lambda: self.validate_username(controller, self.username_entry))
        request_button.image = request_final # prevent garbage collection
        
        # incorrect input
        self.error_text = tk.Label(self, text="The username you entered is invalid or does not match our records.", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#9B1C31')
        
        # return to sign in button
        back_button = HoverButton(self, text="Back to Sign In", font=(TRUE_FONT, 10), borderwidth=0, background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', command=lambda: _combine_funcs(self.exit(self.username_entry), controller.show_frame(StartPage)))
        
        # sign up button
        sign_up_button = HoverButton(self, text="Sign up.", borderwidth=0, command=lambda: _combine_funcs(self.exit(self.username_entry), controller.show_frame(SignUp)), font=(TRUE_FONT, 8, "bold"), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff')
        sign_up_text = tk.Label(self, text="Don't have an account with us?", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        #placement
        title.place(x=260, y=120)
        subtitle.place(x=240, y=160)
        
        username_text.place(x=283, y=225)
        self.username_entry.place(x=287, y=250)
        username_entryline.place(x=280, y=240)
        
        request_button.place(x=280, y=300)
        back_button.place(x=365, y=370)
        
        sign_up_button.place(x=737, y=20)
        sign_up_text.place(x=580, y=20)
    
    def validate_username(self, controller, username_entry):
        input = username_entry.get()
        if input == "" or _fetch_login_information(input) == False:
            self.error_text.place(x=290, y=275)
            self.error_text.config(foreground='#9B1C31')
        else:
            self.exit(username_entry)
            controller.show_frame(AnswerSecurityQuestions)

    def exit(self, username_entry):
            self.error_text.config(foreground='#FFFFFF')
            username_entry.delete(0, 'end')


class AnswerSecurityQuestions(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)

        # response values
        resp1 = ""
        resp2 = ""
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # import logo 
        iconfile = os.path.join(_assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((250, 250), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        
        # title
        title = tk.Label(self, text="Reset Your Password", font=(TRUE_FONT, 20), background='#FFFFFF', foreground='#000000')
        subtitle = tk.Label(self, text="Please enter your new password below.", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        self.pw_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, show="◕", width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_text = tk.Label(self, text="Enter New Password", font=(TRUE_FONT, 8, "bold"), background='#FFFFFF', foreground='#757575')
        
        # confirmation entry
        pw_confirm_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_confirm_entryline.image = entryline_final
        self.pw_confirm_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, show="◕", width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_confirm_text = tk.Label(self, text="Confirm Password", font=(TRUE_FONT, 8, "bold"), background='#FFFFFF', foreground='#757575')
        
        # security question 1 dropdown
        dropdown_1_text = tk.Label(self, text="Security Question 1", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        var_1 = tk.StringVar()
        dropdown_1 = tk.OptionMenu(self, var_1, *_security_questions_1, command=self.get1)
        dropdown_1.config(width=24, background='#FFFFFF', activebackground='#FFFFFF', anchor=tk.W, borderwidth=1, relief="ridge")
        dropdown_1["menu"].config(background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#000000')
        
        # security question 1 response
        response_1_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        response_1_entryline.image = entryline_final
        self.response_1_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        response_1_text = tk.Label(self, text="Your Answer", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        # security question 2 dropdown
        dropdown_2_text = tk.Label(self, text="Security Question 2", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        var_2 = tk.StringVar()
        dropdown_2 = tk.OptionMenu(self, var_2, *_security_questions_2, command=self.get2)
        dropdown_2.config(width=24, background='#FFFFFF', activebackground='#FFFFFF', anchor=tk.W, borderwidth=1, relief="ridge")
        dropdown_2["menu"].config(background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#000000')
        
        # security question 2 response
        response_2_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        response_2_entryline.image = entryline_final
        self.response_2_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        response_2_text = tk.Label(self, text="Your Answer", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        # empty input
        self.error_text = tk.Label(self, text="Please fill out all fields.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # empty input
        self.mismatch_text = tk.Label(self, text="Your passwords do not match.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # invalid input
        self.invalid_text = tk.Label(self, text="Your answers do not match our records.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # confirm button
        confirm_button_path = os.path.join(_assetdir, 'confirm_small.png')
        confirm_button_image = Image.open(confirm_button_path)
        confirm_button_resized = confirm_button_image.resize((143, 47), Image.ANTIALIAS)
        confirm_button_final = ImageTk.PhotoImage(confirm_button_resized)
        confirm_button = tk.Button(self, image=confirm_button_final, padx=-100, pady=-100, command=lambda: self.on_confirm_press(controller), background='#FFFFFF', borderwidth=0)
        confirm_button.image = confirm_button_final # prevent garbage collection
        
        # cancel button
        cancel_button_path = os.path.join(_assetdir, 'cancel_small.png')
        cancel_button_image = Image.open(cancel_button_path)
        cancel_button_resized = cancel_button_image.resize((143, 47), Image.ANTIALIAS)
        cancel_button_final = ImageTk.PhotoImage(cancel_button_resized)
        cancel_button = tk.Button(self, image=cancel_button_final, padx=-100, pady=-100, command=lambda: self.clear_entries(controller), background='#FFFFFF', borderwidth=0)
        cancel_button.image = cancel_button_final # prevent garbage collection
        
        # placement
        title.place(x=73, y=30)
        subtitle.place(x=73, y=70)
        
        logo.place(x=445, y=70)
        
        confirm_button.place(x=500, y=360)
        cancel_button.place(x=500, y=410)
        
        pw_text.place(x=73, y=120)
        self.pw_entry.place(x=77, y=140)
        pw_entryline.place(x=70, y=130)
        
        pw_confirm_text.place(x=73, y=170)
        self.pw_confirm_entry.place(x=77, y=190)
        pw_confirm_entryline.place(x=70, y=180)
        
        dropdown_1_text.place(x=73, y=230)
        dropdown_1.place(x=74, y=250)
        
        response_1_text.place(x=73, y=290)
        self.response_1_entry.place(x=77, y=310)
        response_1_entryline.place(x=70, y=300)
        
        dropdown_2_text.place(x=73, y=350)
        dropdown_2.place(x=74, y=370)
        
        response_2_text.place(x=73, y=410)
        self.response_2_entry.place(x=77, y=430)
        response_2_entryline.place(x=70, y=420)

    def get1(self, value):
        resp1 = value
        print(resp1)

    def get2(self, value):
        resp2 = value
        print(resp2)

    # helper function to reset password
    def on_confirm_press(self, controller):
        if self.response_1_entry.get() == '' or self.response_2_entry.get() == '' or self.pw_entry.get() == '':
            self.mismatch_text.config(foreground='#FFFFFF')
            self.mismatch_text.lower()
            self.error_text.place(x=145, y=450)
            self.error_text.config(foreground='#9B1C31')
            self.invalid_text.config(foreground='#FFFFFF')
            self.invalid_text.lower()
        elif _reset_password(self.response_1_entry.get(), self.response_2_entry.get(), self.pw_entry.get()) == False:
            self.invalid_text.place(x=108, y=450)
            self.invalid_text.config(foreground='#9B1C31')
            self.error_text.config(foreground='#FFFFFF')
            self.error_text.lower()
            self.mismatch_text.config(foreground='#FFFFFF')
            self.mismatch_text.lower()
        elif self.pw_entry.get() != self. pw_confirm_entry.get():
            self.invalid_text.config(foreground='#FFFFFF')
            self.invalid_text.lower()
            self.error_text.config(foreground='#FFFFFF')
            self.error_text.lower()
            self.mismatch_text.place(x=128, y=450)
            self.mismatch_text.config(foreground='#9B1C31')
        else:
            # save inputs for future use
            messagebox.showinfo("Success", "Password Changed Successfully!")   
            self.clear_entries(controller)
            
    def clear_entries(self, controller):
            self.error_text.config(foreground='#FFFFFF')
            self.mismatch_text.config(foreground='#FFFFFF')
            self.invalid_text.config(foreground='#FFFFFF')
            controller.show_frame(StartPage)
            self.response_1_entry.delete(0, 'end')
            self.response_2_entry.delete(0, 'end')
            self.pw_entry.delete(0, 'end')
            self.pw_confirm_entry.delete(0, 'end')


class CreateSecurityQuestions(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)

        # response values
        resp1 = ""
        resp2 = ""

        # set background color
        self.config(bg='#FFFFFF')

        # title
        title = tk.Label(self, text="Set Your Security Questions", font=(TRUE_FONT, 20), background='#FFFFFF', foreground='#000000')
        subtitle = tk.Label(self, text="Please choose two security questions and answer them.\nWe will use them to help you recover your account\nin the event you ever lose it.", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')

        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)

        # banner
        banner_file = os.path.join(_assetdir, 'security_question_banner.png')
        banner_image = Image.open(banner_file)
        banner_resized = banner_image.resize((556, 500), Image.ANTIALIAS)
        banner_final = ImageTk.PhotoImage(banner_resized)
        banner = tk.Canvas(self, width=1024, height=540, background='#000000')
        banner.create_image(0, 0, image=banner_final, anchor=tk.NW)
        banner.image = banner_final
        banner.create_text(190, 150, fill='#FFFFFF', font=(TRUE_FONT, 22, "bold"), text="Your Security. \nOur Pride.")
        banner.create_text(205, 210, fill='#FFFFFF', font=(TRUE_FONT, 10),
                           text="If you reveal your secrets to the wind,   \nyou should not blame the wind for \nrevealing them to the trees....\n\n- Kahlil Gibran")

        # security question 1 dropdown
        dropdown_1_text = tk.Label(self, text="Security Question 1", font=(TRUE_FONT, 8), background='#FFFFFF',
                                   foreground='#757575')
        var_1 = tk.StringVar()
        dropdown_1 = tk.OptionMenu(self, var_1, *_security_questions_1, command=self.get1)
        dropdown_1.config(width=24, background='#FFFFFF', activebackground='#FFFFFF', anchor=tk.W, borderwidth=1,
                          relief="ridge")
        dropdown_1["menu"].config(background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF',
                                  activeforeground='#000000')

        # security question 1 response
        response_1_entryline = tk.Label(self, image=entryline_final, background='#FFFFFF')
        response_1_entryline.image = entryline_final
        self.response_1_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, width=26, background='#FFFFFF',
                                         foreground='#757575', insertbackground='#757575')
        response_1_text = tk.Label(self, text="Your Answer", font=(TRUE_FONT, 8), background='#FFFFFF',
                                   foreground='#757575')

        # security question 2 dropdown
        dropdown_2_text = tk.Label(self, text="Security Question 2", font=(TRUE_FONT, 8), background='#FFFFFF',
                                   foreground='#757575')
        var_2 = tk.StringVar()
        dropdown_2 = tk.OptionMenu(self, var_2, *_security_questions_2, command=self.get2)
        dropdown_2.config(width=24, background='#FFFFFF', activebackground='#FFFFFF', anchor=tk.W, borderwidth=1,
                          relief="ridge")
        dropdown_2["menu"].config(background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF',
                                  activeforeground='#000000')

        # security question 2 response
        response_2_entryline = tk.Label(self, image=entryline_final, background='#FFFFFF')
        response_2_entryline.image = entryline_final
        self.response_2_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, width=26, background='#FFFFFF',
                                         foreground='#757575', insertbackground='#757575')
        response_2_text = tk.Label(self, text="Your Answer", font=(TRUE_FONT, 8), background='#FFFFFF',
                                   foreground='#757575')

        # empty input
        self.error_text = tk.Label(self, text="Please fill out all fields.", font=(TRUE_FONT, 7), background='#FFFFFF',
                                   foreground='#9B1C31')

        # confirm button
        confirm_button_path = os.path.join(_assetdir, 'confirm_full.png')
        confirm_button_image = Image.open(confirm_button_path)
        confirm_button_resized = confirm_button_image.resize((250, 47), Image.ANTIALIAS)
        confirm_button_final = ImageTk.PhotoImage(confirm_button_resized)
        confirm_button = tk.Button(self, image=confirm_button_final, padx=-100, pady=-100,
                                   command=lambda: self.validate_inputs(controller, self.response_1_entry,
                                                                        self.response_2_entry), background='#FFFFFF',
                                   borderwidth=0)
        confirm_button.image = confirm_button_final  # prevent garbage collection

        # return to sign in button
        back_button = HoverButton(self, text="Cancel and Return to Sign In", font=(TRUE_FONT, 8),
                                  borderwidth=0, background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF',
                                  activeforeground='#40c4ff', command=lambda: self.quit(controller))

        # placement
        title.place(x=70, y=25)
        subtitle.place(x=100, y=65)

        banner.place(x=400)

        dropdown_1_text.place(x=74, y=130)
        dropdown_1.place(x=74, y=150)

        response_1_text.place(x=73, y=190)
        self.response_1_entry.place(x=77, y=210)
        response_1_entryline.place(x=70, y=200)

        dropdown_2_text.place(x=74, y=250)
        dropdown_2.place(x=74, y=270)

        response_2_text.place(x=73, y=310)
        self.response_2_entry.place(x=77, y=330)
        response_2_entryline.place(x=70, y=320)

        confirm_button.place(x=71, y=370)
        back_button.place(x=143, y=420)

    def get1(self, value):
        resp1 = value
        print(resp1)

    def get2(self, value):
        resp2 = value
        print(resp2)
    
    def validate_inputs(self, controller, response_1, response_2):
        string_1 = response_1.get()
        string_2 = response_2.get()
        if string_1 == "" or string_2 == "":
            self.error_text.place(x=145, y=353)
            self.error_text.config(foreground='#9B1C31')
        else:
            # save inputs for future use
            self.quit(controller)
    
    def quit(self, controller):
        self.error_text.config(foreground='#FFFFFF')
        controller.show_frame(StartPage)
        self.response_1_entry.delete(0, 'end')
        self.response_2_entry.delete(0, 'end')


class SignUp(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
        
        # import logo 
        iconfile = os.path.join(_assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((100, 100), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        
        # banner
        banner_file = os.path.join(_assetdir, 'sign_up_banner.png')
        banner_image = Image.open(banner_file)
        banner_resized = banner_image.resize((543, 540), Image.ANTIALIAS)
        banner_final = ImageTk.PhotoImage(banner_resized)
        banner = tk.Canvas(self, width=1024, height=540, background = '#000000')
        banner.create_image(0, 0, image=banner_final, anchor=tk.NW)
        banner.image = banner_final
        banner.create_text(200, 200, fill='#FFFFFF', font=(TRUE_FONT, 22, "bold"), text="Protect Yourself. \nSecure your future.")
        banner.create_text(203, 255, fill='#FFFFFF', font=(TRUE_FONT, 10), text="The journey of a thousand miles begins with\na single step. \n\n- Lao Tsu")

        # sign up button
        sign_up_button_path = os.path.join(_assetdir, 'get_started.png')
        sign_up_button_image = Image.open(sign_up_button_path)
        sign_up_button_resized = sign_up_button_image.resize((250, 47), Image.ANTIALIAS)
        sign_up_button_final = ImageTk.PhotoImage(sign_up_button_resized)
        sign_up_button = tk.Button(self, image=sign_up_button_final, padx=-10, pady=-5, command=lambda: self.check_inputs(controller, self.username_entry, self.pw_entry, self.pw_confirm_entry), background='#FFFFFF', borderwidth=0)
        sign_up_button.image = sign_up_button_final # prevent garbage collection
        
        # title and subtitle
        title = tk.Label(self, text="Noodles Password Vault", font=(TRUE_FONT, 20), foreground='#000000', background='#FFFFFF')
        subtitle = tk.Label(self, text="Create an account", font=(TRUE_FONT, 10), foreground='#757575', background='#FFFFFF')
        
        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        self.username_entry = tk.Entry(self, width=26, highlightthickness=0, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        self.pw_entry = tk.Entry(self, borderwidth=0, highlightthickness=0, show="◕", width=26, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_text = tk.Label(self, text="Password", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # confirmation entry
        pw_confirm_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_confirm_entryline.image = entryline_final
        self.pw_confirm_entry = tk.Entry(self, borderwidth=0, show="◕", width=26, highlightthickness=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_confirm_text = tk.Label(self, text="Confirm Password", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        
        # empty input
        self.error_text = tk.Label(self, text="Please fill out all fields.", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#9B1C31')
        
        # mismatch input
        self.mismatch_text = tk.Label(self, text="Your passwords do not match.", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#9B1C31')
        
        # existing username
        self.username_error_text = tk.Label(self, text="That username is already in use.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # log in text
        back_button = HoverButton(self, text="Log in.", font=(TRUE_FONT, 8, "bold"), command=lambda: _combine_funcs(controller.show_frame(StartPage), _clear_entry(self.username_entry, self.pw_entry, self.pw_confirm_entry)), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        log_in_text = tk.Label(self, text="Already have an account?", font=(TRUE_FONT, 10), background='#FFFFFF', foreground='#757575')
        back_button = HoverButton(self, text="Log in.", font=(TRUE_FONT, 8, "bold"), command=lambda: _combine_funcs(controller.show_frame(StartPage), self.quit_page()), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        log_in_text = tk.Label(self, text="Already have an account?", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        #placement
        logo.place(x=145, y=20)
        
        banner.place(x=400)
        
        title.place(x=85, y=130)
        subtitle.place(x=145, y=160)
        
        username_text.place(x=73, y=200)
        self.username_entry.place(x=77, y=220)
        username_entryline.place(x=70, y=210)
        
        pw_text.place(x=73, y=250)
        self.pw_entry.place(x=77, y=270)
        pw_entryline.place(x=70, y=260)
        
        pw_confirm_text.place(x=73, y=300)
        self.pw_confirm_entry.place(x=77, y=320)
        pw_confirm_entryline.place(x=70, y=310)
        
        sign_up_button.place(x=71, y=360)
        
        back_button.place(x=225, y=430)
        log_in_text.place(x=125, y=430)
        
    def check_inputs(self, controller, username_entry, pw_entry, pw_confirm_entry):
        string_1 = username_entry.get()
        string_2 = pw_entry.get()
        string_3 = pw_confirm_entry.get()
        if string_1 == "" or string_2 == "" or string_3 == "":
            self.mismatch_text.config(foreground='#FFFFFF')
            self.mismatch_text.lower()
            self.error_text.place(x=153, y=342)
            self.error_text.config(foreground='#9B1C31')
            self.username_error_text.lower()
            self.username_error_text.config(foreground='#FFFFFF')
        elif _fetch_username_information(string_1) == True:
            self.mismatch_text.config(foreground='#FFFFFF')
            self.mismatch_text.lower()
            self.error_text.config(foreground='#FFFFFF')
            self.error_text.lower()
            self.username_error_text.place(x=145, y=342)
            self.username_error_text.config(foreground='#9B1C31')
        elif string_2 != string_3:
            self.mismatch_text.place(x=140, y=342)
            self.mismatch_text.config(foreground='#9B1C31')
            self.error_text.config(foreground='#FFFFFF')
            self.error_text.lower()
            self.username_error_text.lower()
            self.username_error_text.config(foreground='#FFFFFF')
        else:
            # save inputs for future use
            self.quit_page()
            controller.show_frame(CreateSecurityQuestions)
    
    def quit_page(self):
        self.error_text.config(foreground='#FFFFFF')
        self.mismatch_text.config(foreground='#FFFFFF')
        self.username_error_text.config(foreground='#FFFFFF')
        self.username_entry.delete(0, 'end')
        self.pw_entry.delete(0, 'end')
        self.pw_confirm_entry.delete(0, 'end')


class DownloadPage(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
        
class AddPassword(tk.Frame):
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        
        # set background color
        self.config(bg='#FFFFFF')
                    
        self.parent = controller
        
        # import logo 
        iconfile = os.path.join(_assetdir, 'black_noodles_black.png')
        image = Image.open(iconfile)
        logo_resized = image.resize((100, 100), Image.ANTIALIAS)     
        img = ImageTk.PhotoImage(logo_resized)
        logo = tk.Label(self, image=img, background = '#FFFFFF')
        logo.image = img # prevent garbage collection
        
        # banner
        banner_file = os.path.join(_assetdir, 'sign_up_banner.png')
        banner_image = Image.open(banner_file)
        banner_resized = banner_image.resize((543, 540), Image.ANTIALIAS)
        banner_final = ImageTk.PhotoImage(banner_resized)
        banner = tk.Canvas(self, width=1024, height=540, background = '#000000')
        banner.create_image(0, 0, image=banner_final, anchor=tk.NW)
        banner.image = banner_final
        banner.create_text(200, 160, fill='#FFFFFF', font=(TRUE_FONT, 18, "bold"), text="Protect Yourself. \nSecure your future.")
        banner.create_text(205, 220, fill='#FFFFFF', font=(TRUE_FONT, 8), text="Insert here some inspirational text about \nwhy its a good idea to protect your passwords.")
        
        # sign up button
        add_confirm_button_path = os.path.join(_assetdir, 'confirm_small.png')
        add_confirm_button_image = Image.open(add_confirm_button_path)
        add_confirm_button_resized = add_confirm_button_image.resize((143, 47), Image.ANTIALIAS)
        add_confirm_button_final = ImageTk.PhotoImage(add_confirm_button_resized)
        add_confirm_button = tk.Button(self, image=add_confirm_button_final, padx=10, pady=10, command=lambda: _combine_funcs(create_new_password(self, self.website_entry.get(), self.username_entry.get(), self.pw_entry.get()), controller.show_frame(InsidePage)), background='#FFFFFF', borderwidth=0)
        add_confirm_button.image = add_confirm_button_final # prevent garbage collection
        
        # title and subtitle
        title = tk.Label(self, text="Add New Password", font=(TRUE_FONT, 16), foreground='#000000', background='#FFFFFF')
        
        # import entryline image
        entryline_file = os.path.join(_assetdir, 'entryline.png')
        entryline_image = Image.open(entryline_file)
        entryline_resized = entryline_image.resize((250, 26), Image.ANTIALIAS)
        entryline_final = ImageTk.PhotoImage(entryline_resized)
        
        # username entry
        username_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        username_entryline.image = entryline_final
        self.username_entry = tk.Entry(self, width=40, borderwidth=0, background='#FFFFFF', foreground='#757575', insertbackground='#757575')
        username_text = tk.Label(self, text="Username", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        # password entry
        pw_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        pw_entryline.image = entryline_final
        self.pw_entry = tk.Entry(self, borderwidth=0, show="◕", width=40, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        pw_text = tk.Label(self, text="Password", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        # website entry
        website_entryline = tk.Label(self, image=entryline_final, background = '#FFFFFF')
        website_entryline.image = entryline_final
        self.website_entry = tk.Entry(self, borderwidth=0, width=40, background='#FFFFFF', foreground='#757575', insertbackground='#757575') #show="*" changes input to *
        website_text = tk.Label(self, text="Website", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
                           
        # empty input
        self.error_text = tk.Label(self, text="Please fill out all fields.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # mismatch input
        #self.mismatch_text = tk.Label(self, text="Your passwords do not match.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # existing username
        #self.username_error_text = tk.Label(self, text="That username is already in use.", font=(TRUE_FONT, 7), background='#FFFFFF', foreground='#9B1C31')
        
        # log in text
        back_button = HoverButton(self, text="Go back", font=(TRUE_FONT, 8, "bold"), command=lambda: _combine_funcs(controller.show_frame(InsidePage), self.quit_page()), background='#FFFFFF', foreground='#757575', activebackground='#FFFFFF', activeforeground='#40c4ff', borderwidth=0)
        #log_in_text = tk.Label(self, text="Already have an account?", font=(TRUE_FONT, 8), background='#FFFFFF', foreground='#757575')
        
        #placement
        logo.place(x=145, y=20)
        
        banner.place(x=400)
        
        title.place(x=100, y=130)
        #subtitle.place(x=145, y=160)
        
        website_text.place(x=75, y=200)
        self.website_entry.place(x=77, y=220)
        website_entryline.place(x=70, y=210)
        
        username_text.place(x=75, y=250)
        self.username_entry.place(x=77, y=270)
        username_entryline.place(x=70, y=260)
        
        pw_text.place(x=75, y=300)
        self.pw_entry.place(x=77, y=320)
        pw_entryline.place(x=70, y=310)
        
        
        
        add_confirm_button.place(x=120, y=360)
        
        back_button.place(x=165, y=430)
        #log_in_text.place(x=105, y=430)
        
        def quit_page(self):
            self.error_text.config(foreground='#FFFFFF')
            #self.mismatch_text.config(foreground='#FFFFFF')
            #self.username_error_text.config(foreground='#FFFFFF')
            self.username_entry.delete(0, 'end')
            self.pw_entry.delete(0, 'end')
            self.website_entry.delete(0, 'end')
            
            
        def create_new_password(self, website, username, pw):
            #self.parent.user_password_information.append((website, username, pw, "today"))
            _sample_user_info.append((website, username, pw, "today"))
            quit_page(self)
            self.parent.create_inside()
    
    
    
if __name__ == "__main__":
    application_process = NoodlePasswordVault()
    
    # set icon
    if platform.system() == 'Windows':
        iconfile = os.path.join(_assetdir, 'black_noodles_white_Xbg_icon.ico')
        application_process.wm_iconbitmap(default=iconfile)
    else:
        ext = '.png' if tk.TkVersion >= 8.6 else '.gif'
        iconfiles = [os.path.join(_assetdir, 'black_noodles_white_Xbg_icon%s' % (ext))]
        icons = [tk.PhotoImage(master=application_process, file=iconfile) for iconfile in iconfiles]
        application_process.wm_iconphoto(True, *icons)

    # set window size
    application_process.geometry("800x500+0+0")
    application_process.resizable(False, False)
    
    application_process.protocol("WM_DELETE_WINDOW", _quit)
    application_process.mainloop()