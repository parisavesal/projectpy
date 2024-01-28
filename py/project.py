import sqlite3 as sq
import tkinter as tk
import json


def login():
    global cnt, isLogin, userID, userScore, setFile
    user = text_user.get()
    pas = text_pass.get()
    sql = f'''
        SELECT * FROM users WHERE username="{user}" AND password="{pas}"
    '''
    result = cnt.execute(sql)
    row = result.fetchall()

    if len(row) < 1:
        lbl_msg.configure(text="Wrong username or password", fg='red')
    else:
        lbl_msg.configure(text="Welcome to your account", fg='green')
        isLogin = user
        userID = row[0][0]
        userScore = row[0][4]
        text_user.delete(0, "end")
        text_pass.delete(0, "end")
        btn_login.configure(state='disabled')
        btn_logout.configure(state="active")
        print(setFile['scores']['shop'])
        if isLogin == 'admin':
            btn_shop.configure(state='active')
            btn_setting.configure(state='active')
        if userScore >= int(setFile['scores']['shop']):
            btn_shop.configure(state='active')


def submit():

    def clear_all():
        text_user2.delete(0, "end")
        text_pass2.delete(0, "end")
        text_pass_con.delete(0, 'end')
        text_addr.delete(0, "end")

    def register():
        user = text_user2.get()
        pas = text_pass2.get()
        cpas = text_pass_con.get()
        addr = text_addr.get()

        result, msg = validate(user, pas, cpas, addr)
        if not result:
            lbl_msg2.configure(text=msg, fg='red')
            return

        sql = f'''
            INSERT INTO 
            users(username,password,address,score)
             VALUES("{user}","{pas}","{addr}",1)
        '''
        cnt.execute(sql)
        cnt.commit()
        clear_all()
        lbl_msg2.configure(text="Your Register Successfully! :)", fg='green')

    win_sub = tk.Toplevel(win)

    win_sub.title("Submit")
    win_sub.geometry("300x270")
    win_sub.configure(bg=setFile['color'])

    lbl_user2 = tk.Label(win_sub, text="Username: ", bg=setFile['color'])
    lbl_user2.pack()
    text_user2 = tk.Entry(win_sub)
    text_user2.pack()

    lbl_pass2 = tk.Label(win_sub, text="Password: ", bg=setFile['color'])
    lbl_pass2.pack()
    text_pass2 = tk.Entry(win_sub)
    text_pass2.pack()

    lbl_pass_con = tk.Label(win_sub, text="Password Confirmation: ", bg=setFile['color'])
    lbl_pass_con.pack()
    text_pass_con = tk.Entry(win_sub)
    text_pass_con.pack()

    lbl_addr = tk.Label(win_sub, text="Address: ", bg=setFile['color'])
    lbl_addr.pack()
    text_addr = tk.Entry(win_sub)
    text_addr.pack()

    lbl_msg2 = tk.Label(win_sub, text="", bg=setFile['color'])
    lbl_msg2.pack()

    btn_submit2 = tk.Button(win_sub, text="Register", command=register)
    btn_submit2.pack()

    win_sub.mainloop()


def validate(user, pas, cpas, addr):
    global cnt
    sql = f'''SELECT * From users WHERE username="{user}"'''
    result = cnt.execute(sql)

    row = result.fetchone()
    print(type(row))
    if not row is None:
        return False, "Username Already exist!"
    if user == '' or pas == '' or cpas == '' or addr == '':
        return False, "Please fill the blanks!"
    if len(pas) < 5:
        return False, "Password length should be at least 5!"
    if pas != cpas:
        return False, "Password and Confirmation Mismatch!"
    if len(addr) < 2:
        return False, "Address len is too short!"

    return True, ""


def logout():
    global isLogin
    btn_login.configure(state="active")
    btn_logout.configure(state="disabled")
    btn_shop.configure(state="disabled")
    btn_setting.configure(state="disabled")
    isLogin = False
    lbl_msg.configure(text="you are logout now!", fg="green")


def shop_panel():
    global userID

    def clear_all():
        text_id4.delete(0, "end")
        text_qnt4.delete(0, "end")
        product_list.delete(0, "end")

    def shop():
        p_id = text_id4.get()
        p_qnt = text_qnt4.get()

        result, msg = validate_shop(p_id, p_qnt)
        if not result:
            lbl_msg4.configure(text=msg, fg='red')
            return

        result = update_qnt(p_id, p_qnt)
        if not result:
            lbl_msg4.configure(text="Something went wrong while connecting DB!", fg='red')
            return

        print(userID, p_qnt, p_id)

        try:
            sql = f'''
                INSERT INTO 
                cart(p_id,p_qnt,u_id)
                 VALUES({p_id},{p_qnt},{userID})
                '''
            cnt.execute(sql)
            cnt.commit()
            print("shop success")
        except:
            print('shop failed')

        lbl_msg4.configure(text="Shop Successfully", fg='green')

       
        clear_all()

        
        fetch_data(product_list)

    win_shop = tk.Toplevel(win)
    win_shop.title("Shop Panel")
    win_shop.geometry("400x450")
    win_shop.configure(bg=setFile['color'])

    product_list = tk.Listbox(win_shop, width=50, height=13)
    product_list.pack(pady=20)

    lbl_id4 = tk.Label(win_shop, text="ID:", bg=setFile['color'])
    lbl_id4.pack()
    text_id4 = tk.Entry(win_shop)
    text_id4.pack()

    lbl_qnt4 = tk.Label(win_shop, text="QNT:", bg=setFile['color'])
    lbl_qnt4.pack()
    text_qnt4 = tk.Entry(win_shop)
    text_qnt4.pack()

    lbl_msg4 = tk.Label(win_shop, text="", bg=setFile['color'])
    lbl_msg4.pack()

    btn_shop4 = tk.Button(win_shop, text="Shop Now", command=shop)
    btn_shop4.pack()

    fetch_data(product_list)

    win.mainloop()


def fetch_data(lst):
    products = get_all_products()
    for product in products:
        info = f"ID:{product[0]}, Name:{product[1]}, Price:{product[2]}, QNT:{product[3]}"
        
        lst.insert('end', info)


def get_all_products():
    sql = '''
        SELECT * FROM products WHERE qnt>0
    '''

    result = cnt.execute(sql)
    rows = result.fetchall()
    return rows


def validate_shop(p_id, p_qnt):
    if p_id == '' or p_qnt == '':
        return False, 'Please Fill the Blanks!'

    p_qnt = int(p_qnt)

    if p_qnt <= 0:
        return False, 'QNT at least should be 1! :/'

    sql = f'''
    SELECT * FROM products WHERE id={p_id}
    '''
    result = cnt.execute(sql)
    row = result.fetchone()
    if row is None:
        return False, 'Wrong Product ID'

    sql = f'''SELECT * FROM products WHERE id={p_id} and qnt>={p_qnt}'''
    result = cnt.execute(sql)
    row = result.fetchone()
    if row is None:
        return False, 'there isnt enough products'

   
    return True, ''


def update_qnt(p_id, p_qnt):
    try:
        p_qnt = int(p_qnt)
        sql = f'''
        UPDATE products SET qnt=qnt-{p_qnt} WHERE id={p_id}
        '''
        cnt.execute(sql)
        cnt.commit()
        return True
    except:
        return False


def setting():
    global setFile

    def save():
        color = text_color.get()
        shop_score = text_shop_score.get()

        result, msg = validate_setting(color, shop_score)

        if not result:
            lbl_msg4.configure(text=msg, fg='red')
            return
        win.configure(bg=color)
        setFile['color'] = color
        setFile['scores']['shop'] = int(shop_score)
        print(setFile)
        try:
            read_write(setFile)
            lbl_msg4.configure(text="changes successfully! :)", fg='green')
        except:
            lbl_msg4.configure(text="changes failed, somthing went wrong", fg='red')

    win_set = tk.Toplevel(win)
    win_set.title("Setting")
    win_set.geometry("300x200")
    win_set.configure(bg=setFile['color'])


    lbl_color = tk.Label(win_set, text="Color: ", bg=setFile['color'])
    lbl_color.pack()
    text_color = tk.Entry(win_set)
    text_color.pack()

    lbl_shop_score = tk.Label(win_set, text="Shop Score:", bg=setFile['color'])
    lbl_shop_score.pack()
    text_shop_score = tk.Entry(win_set)
    text_shop_score.pack()

    lbl_msg4 = tk.Label(win_set, bg=setFile['color'])
    lbl_msg4.pack()

    btn_save = tk.Button(win_set, text="Save", command=save)
    btn_save.pack(pady=5)

    win_set.mainloop()


def read_write(inf=False):
    if not inf:
        try:
            with open('setting.json') as f:
                return json.load(f)
        except:
            with open('setting.json', 'w') as f:
                f.write('{"color" : "#ccc","scores":{"shop":5}}')
                return {"color" : "#ccc","scores":{"shop":5}}
    else:
        with open('setting.json', 'w') as f:
            json.dump(inf, f)


def validate_setting(color, shop_score):
    if color == '' or shop_score == '':
        return False, 'Please fill the blanks!'
    return True, ''

cnt = sq.connect('shop.db')
isLogin = False
userID = 0
userScore = 0
setFile = read_write()

print(setFile)
win = tk.Tk()

win.title("Login")
win.geometry("300x350")
win.configure(bg=setFile['color'])

lbl_user = tk.Label(win, text="Username: ", bg=setFile['color'])
lbl_user.pack()
text_user = tk.Entry(win)
text_user.pack()

lbl_pass = tk.Label(win, text="Password: ", bg=setFile['color'])
lbl_pass.pack()
text_pass = tk.Entry(win)
text_pass.pack()

lbl_msg = tk.Label(win, text="",bg=setFile['color'])
lbl_msg.pack()

btn_login = tk.Button(win, text="Login", command=login)
btn_login.pack()

btn_submit = tk.Button(win, text="Submit", command=submit)
btn_submit.pack(pady=10)

btn_logout = tk.Button(win, text="Logout", command=logout, state="disabled")
btn_logout.pack(pady=5)


btn_shop = tk.Button(win, text="Shop Panel", state="disabled", command=shop_panel)
btn_shop.pack(pady=5)

btn_setting = tk.Button(win, text="Setting", state="disabled", command=setting)
btn_setting.pack(pady=5)

win.mainloop()
