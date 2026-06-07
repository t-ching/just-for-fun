# Name:         Terence Ching / 900026114
# Project:      Pizza kiosk
# Date:         2026-06-03
# Description:  The program is to create a kiosk that allows customers to order pizzas
#               in an efficient way. Functionalities include select pizzas, edit orders,
#               review cart, and make payment.

#------------------------------------ Imports -----------------------------------
import FreeSimpleGUI as sg
import datetime as dt

#------------------------------- Global Variables -------------------------------
dsn_menu = "images/.pizzas"                         # menu file
dsn_ordr = "images/order.txt"                       # order detail file
dsn_sid  = "images/id.txt"                          # file with latest system ID
dsn_revw = "images/cust_review.txt"                 # customer review file
screens  = ["scr_1", "scr_2", "scr_3", "scr_4"]     # list of all screen keys
fnt_fix  = "Menlo"                                  # default fixed-width font for MAC
fnt_ssf  = "Helvetica"                              # default sans-serif  font for MAC
fnt_xlg  = 30                                       # font size, extra large
fnt_lge  = 20                                       # font size, large
fnt_med  = 14                                       # font size, medium (default)
fnt_sml  = 10                                       # font size, small
menu     = []                                       # initiate pizza menu
menu_srt = 6                                        # 5: hard code from menu / 6: sum up from orders
shw_top  = 3                                        # show top N in "Most Popular"
ord_itm  = []                                       # initiate ordered items, only store name, price, quantity
ord_tot  = 0                                        # initiate total order amount
sys_id   = 0                                        # initiate system ID, also as order ref num
sts_tout = None
time_cnt = 10000                                    # 10 seconds
# sts_tout is the initial state of time out counter, use in confirmation page (screen 4)
# go back Home after the time_cnt threshold is met without any user interaction
ttip_logo= "Welcome to OnlyPizza"
ttip_back= "Go back to make changes to your order"
ttip_home= "Clear cart and Restart"
ttip_cart= "Review your order"
txt_vers = "© 2026 OnlyPizza Kiosk, Version 2.0"


#--------------------------------- Screen Setup ---------------------------------
sg.set_options(
    background_color='white',
    text_element_background_color='white',
    element_background_color='white',
    text_color='#555555',
    button_color=('white', 'teal'),
    font=(fnt_ssf, fnt_med)
)

#----------------------------------- Functions -----------------------------------
def show_screen(i):
    for idx, name in enumerate(screens, start=1):
        # Update visibility: True if it matches i, False otherwise
        window[name].update(visible=(idx == i))
        window.refresh()

# Read in pizza menu, return as
# Menu: [name, image, description, ingredient, price, quantity ever ordered]]
def read_menu(filename):
    with open(filename, "r") as file:
        for line in file:
            row = line.rstrip("\n").split("#")
            if len(row) >= 6:
                row[4] = float(row[4])  # Convert price to float
                row[5] = int(row[5])    # Convert hard-coded ever ordered to integer
                row.append(0)           # Adds a new column to store qty from order
                menu.append(row)

# Generate layout to display pizzas horizontally, use in menu - most popular
def gen_layt_topn(item,islast):
    row = sg.Column(
            [
                [sg.Image(filename=f"images/{item[1]}")],
                [sg.Text(f"${item[4]:.2f}")],
                [sg.Button("–", font=(fnt_ssf, fnt_lge), key=f"key_menu_dec_{item[0]}"),
                 sg.Text("0", key=f"txt_menu_qty_{item[0]}"),
                 sg.Button("+", font=(fnt_ssf, fnt_lge), key=f"key_menu_inc_{item[0]}")
                 ]
            ], element_justification='c')

    if not islast:
        return [row, sg.Push()]
    else:
        return [row]

# Generate layout to display pizzas vertically, use in menu - other items
def gen_layt_rest(item):
    return [   sg.vtop(sg.Image(filename=f"images/{item[1]}")),
                sg.Column([
                    [sg.Text(item[2], size=(32, None))],
                    [sg.Text(item[3], size=(32, None))],
                    [sg.Text(f"${item[4]:.2f}"),sg.Push(),
                     sg.Button("–", font=(fnt_ssf, fnt_lge), key=f"key_menu_dec_{item[0]}"),
                     sg.Text("0", key=f"txt_menu_qty_{item[0]}"),
                     sg.Button("+", font=(fnt_ssf, fnt_lge), key=f"key_menu_inc_{item[0]}")
                    ]
               ])
        ]

# Open ID file, read-in current number, add 1, save and close
# call upon once paid
def upd_id(filename):
    global sys_id
    try:
        with open(filename, "r+") as file:
            content = file.read().strip()
            sys_id = int(content) if content else 0

            sys_id += 1

            file.seek(0)  # Move file pointer back to the beginning
            file.write(str(sys_id))
            file.truncate()

    except FileNotFoundError:
        print("System ID file not found")

# Update order detail file
# ord_itm: [name, price, quantity]]
def upd_ord(ord_itm,cust_ref,ord_total):
    now = dt.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    numeric_ts = str(int(now.timestamp()))
    try:
        with open(dsn_ordr, "a") as f:
            for item in sorted(ord_itm):
                if item[2] > 0:                 # make sure quantity > 0
                    subtotal = item[1] * item[2] # price x quantity
                    #Construct row (all items in string) matching order file column sequence
                    row = [ str(cust_ref),      # cust order reference num
                            date_str,           # date
                            numeric_ts,         # timestamp
                            item[0],            # pizza name
                            str(item[2]),       # order quantity
                            f"{item[1]:.2f}",   # item price
                            f"{subtotal:.2f}",  # sub total
                            f"{ord_total:.2f}"  # total order price
                    ]
                    f.write(",".join(row) + "\n")
    except Exception as e:
        sg.popup_error("File Error", f"Could not save order data:\n{e}")

# Reset menu / cart
def homereset():
    # reset selected key values
    for key in list(window.key_dict.keys()):
        if isinstance(key, str) and key.startswith("txt_menu_qty_"):
            window[key].update("0")             # reset all quantities in menu
        if key == "txt_conf_thank":
            window[key].update("")              # reset review thank you text
        if isinstance(key, str) and key.startswith("key_conf_rev_"):
            window[key].update(disabled=False)  # enable review buttons
    # reset order related
    ord_itm.clear()
    ord_tot = 0

    # reset timeout counter
    sts_tout = None

    show_screen(1)

#-------------------------------- Create Screens --------------------------------
# Screen 1 - Home
def scr_home():
    scr1_layout = \
    [
        [sg.Push(),sg.Image(filename="images/OnlyPizza Logo.png", tooltip=ttip_logo),sg.Push()],
        [sg.Text("")],
        [sg.Push(),
         sg.Button("ORDER NOW!", size=(350, 1), key="go_menu",
                  font=(fnt_ssf, fnt_lge, "bold"),
                  button_color=('white', 'teal'),
                  border_width=1),
         sg.Push()],
        [sg.VPush()],
        [sg.Text(txt_vers, font=(fnt_ssf, fnt_sml))]
    ]
    return scr1_layout

# Screen 2 - Menu
read_menu(dsn_menu)                         # read-in pizza menu, output as "menu" list

# Sum quantities from the Order file and map it to Menu
# if found update order qty to index 6 in menu, this is the new field to get popular items
with open(dsn_ordr, 'r') as f:
    lines = f.readlines()
    for line in lines[1:]:
        row = line.strip().split(',')
        name = row[3].upper()
        qty_to_add = int(row[4])
        for item in menu:
            if item[0].upper() == name:
                item[6] += qty_to_add   # add ordered quantity
                break                   # stop searching if found

menu.sort(key=lambda x: x[0].lower())               # sort by name, case-insensitive
menu.sort(key=lambda x: x[menu_srt], reverse=True)  # sort by ever ordered /order total in desc order
menu_topN = menu[:shw_top]                          # create top N list
menu_rest = menu[shw_top:]                          # rest of pizza list
menu_rest.sort(key=lambda x: x[0].lower())          # sort by name for the rest

def scr_menu():
    scr2_layout = \
    [
        [sg.Push(), sg.Image(filename="images/OnlyPizza Logo sml.png", tooltip=ttip_logo), sg.Push()],
        [sg.Text("Back", font=(fnt_ssf, fnt_lge), text_color="white"),  #placeholder, not visible
         sg.Push(),
         sg.Text("MENU", font=(fnt_ssf, fnt_xlg, "bold")),
         sg.Push(),
         sg.Button("Home", font=(fnt_ssf, fnt_lge), tooltip=ttip_home, key="go_home2")],

        # Most popular (3), layout horizontally
        [sg.Text("Most Popular", font=(fnt_ssf, fnt_lge, "bold"))],
        sum([gen_layt_topn(item, islast=False) for item in menu_topN[:-1]], []) +
        sum([gen_layt_topn(item, islast=True) for item in menu_topN[-1:]], []),
        [sg.HorizontalSeparator()],

        # The rest, layout vertically and scrollable
        [sg.Text("All others", font=(fnt_ssf, fnt_lge, "bold"))],
        [sg.Column(
            [gen_layt_rest(item) for item in menu_rest],
            scrollable=True,
            vertical_scroll_only=True,
            size=(420,200),
            expand_x=False,
            sbar_width=8
        )],
        [sg.VPush()],
        [sg.Push(),
         sg.Button("Go to Cart", tooltip=ttip_cart, size=(350, 1), font=(fnt_ssf, fnt_lge), key="go_cart"),
         sg.Push()],
        [sg.VPush()],
        [sg.Text(txt_vers, font=(fnt_ssf, fnt_sml))]
    ]
    return scr2_layout

# Screen 3 - Cart
def scr_cart():
    scr3_layout = \
    [
        [sg.Push(), sg.Image(filename="images/OnlyPizza Logo sml.png", tooltip=ttip_logo), sg.Push()],
        [sg.Button("Back", font=(fnt_ssf, fnt_lge), tooltip=ttip_back, key="go_back"),
         sg.Push(),
         sg.Text("CART", font=(fnt_ssf, fnt_xlg, "bold")),
         sg.Push(),
         sg.Button("Home", font=(fnt_ssf, fnt_lge), tooltip=ttip_home, key="go_home3")],
        [sg.Text("")],
        [sg.Text("Show cart.", font=(fnt_fix, 19), key="txt_cart_list")],
        [sg.Text("Total: $0.00", font=(fnt_ssf, fnt_lge), key="txt_cart_tot")],
        [sg.Text("")],
        [sg.Push(),
         sg.Button("Go to Payment", size=(350, 1), font=(fnt_ssf, fnt_lge), key="go_pay"),
         sg.Push()],
        [sg.VPush()],
        [sg.Text(txt_vers, font=(fnt_ssf, fnt_sml))]
    ]
    return scr3_layout

# Screen 4 - Confirm
def scr_conf():
    scr4_layout = \
    [
        [sg.Push(), sg.Image(filename="images/OnlyPizza Logo sml.png", tooltip=ttip_logo), sg.Push()],
        [sg.Push(), sg.Text("ORDER CONFIRMED!", font=(fnt_ssf, fnt_xlg, "bold")), sg.Push()],
        [sg.Text("")],
        [sg.Text("Your order", font=(fnt_ssf, fnt_lge), pad=(None, 0)),
         sg.Text("", font=(fnt_ssf, fnt_xlg, "bold"), text_color="green", pad=(0, 0), key="txt_conf_num"),
         sg.Text("is being prepared:", font=(fnt_ssf, fnt_lge), pad=(0, None))],
        [sg.Text("Show orders.", font=(fnt_fix, 19), key="txt_conf_list")],
        [sg.Text("")],
        [sg.Text("Thank you for ordering with OnlyPizza.", font=(fnt_ssf, fnt_lge))],
        [sg.Text("")],
        [sg.Push(),
         sg.Button("Home", size=(350, 1), tooltip=ttip_home, font=(fnt_ssf, fnt_lge), key="go_home4"),
         sg.Push()],
        [sg.Text("")],
        [sg.HorizontalSeparator()],
        [sg.Text("How do you rate your ordering experience?")],
        [sg.Push(),
         sg.Button(image_filename="images/unhappy.png",
                   button_color=(sg.theme_background_color()), border_width=0, key="key_conf_rev_unhappy"),
         sg.Button(image_filename="images/neutral.png",
                   button_color=(sg.theme_background_color()), border_width=0, key="key_conf_rev_neutral"),
         sg.Button(image_filename="images/happy.png",
                   button_color=(sg.theme_background_color()), border_width=0, key="key_conf_rev_happy"),
         sg.Button(image_filename="images/ecstatic.png",
                   button_color=(sg.theme_background_color()), border_width=0, key="key_conf_rev_ecstatic"),
         sg.Push()],
        [sg.Text("", key="txt_conf_thank")],
        [sg.VPush()],
        [sg.Text(txt_vers, font=(fnt_ssf, fnt_sml))]
    ]
    return scr4_layout

#------------------------------------- Main -------------------------------------
layout = \
    [
        [sg.Column(scr_home(), key="scr_1", expand_x=True, expand_y=True),
         sg.Column(scr_menu(), key="scr_2", visible=False, expand_x=True, expand_y=True),
         sg.Column(scr_cart(), key="scr_3", visible=False, expand_x=True, expand_y=True),
         sg.Column(scr_conf(), key="scr_4", visible=False, expand_x=True, expand_y=True)]
    ]

window = sg.Window("", layout, size=(450,700))

while True:
    # window.read(): Pauses execution and waits for a user action (click, close, type).
    # 'event' is the key of the element clicked.
    # event, values = window.read()    # needed to do event handling!!!
    event, values = window.read(timeout=sts_tout)

    if event in (sg.WIN_CLOSED,"Finish"):          # the x or the button called Finish
        break                                      # "finish" is there to stop the program from crashing
                                                   # even though we dont have an object called "Finish"

    # when clicking + / - in menu
    if event.startswith("key_menu_"):
        # Extract pizza name from the key
        key_parts = event.split("_")
        clicked_item = key_parts[3]

        # Menu: [name, image, description, ingredient, price, quantity ever ordered]]
        # next() to find the first matching record in menu if name (item[0]) = pizza name being clicked (clicked_item)
        # return None if not found. Part of the matched_menu is saved in ord_itm later.
        matched_menu = next((item for item in menu if item[0] == clicked_item), None)

        # ord_itm: [name, price, quantity]]
        # Update cart, check if the pizza already exist in ord_itm
        match_ord = next((item for item in ord_itm if item[0] == clicked_item), None)
        if event.startswith("key_menu_inc"):                            # clicked + button
            if match_ord is None:                                       # new item, append
                ord_itm.append([matched_menu[0], matched_menu[4], 1])   # only append name, price, 1 to ord_itm
            else:                                                       # existing item, add quantity
                match_ord[2] += 1
        elif match_ord is not None and match_ord[2] > 0:                # clicked - button, and in order list
            match_ord[2] -= 1

        # Update quantity and refresh screen
        match_ord = next((item for item in ord_itm if item[0] == clicked_item), None)
        if match_ord is not None:
            window[f"txt_menu_qty_{clicked_item}"].update(match_ord[2])
            window.refresh()

    if event in ("go_menu","go_back"):
        show_screen(2)

    if event == "go_cart":
        # remove items with 0 quantity
        ord_itm = [row for row in ord_itm if row[2] > 0]
        if not ord_itm:
            sg.popup("Please add an item to your cart first!", title="OnlyPizza", modal=True, keep_on_top=True)
        else:
            # sort order by name and get total
            ord_itm.sort(key=lambda x: x[0].lower())

            #for each item in ord_itm, get order total cost = price (item[1]) * quantity (item[2])
            ord_tot = sum(item[1] * item[2] for item in ord_itm)
            window["txt_cart_tot"].update(f"Total: ${ord_tot:.2f}")

            cart_list = []
            # for each item in the sorted (by name in alphabetical order) ord_itm,
            # create a string with quantity (item[2]) in 2 digits
            # name (item[0]) with 20 char length and total cost with 2 decimal places
            # e.g. 2 x Meat Lover        $32.00
            # append to cart_list, to be displayed in screen 3 (review order/cart)
            for item in sorted(ord_itm):
                cart_list.append(f"{item[2]:2d} x {item[0]:<20}  ${item[1]*item[2]:>7.2f}")
            window["txt_cart_list"].update("\n".join(cart_list))

            show_screen(3)

    if event == "go_pay":
        choice_pay = sg.popup_ok_cancel("You are about to make the payment!", title="OnlyPizza")
        if choice_pay == "OK":      # customer confirm go ahead, order made and paid
            upd_id(dsn_sid)         # get next ID in line and update ID file
            window["txt_conf_num"].update(f"#{sys_id}")
            conf_list = []
            for item in sorted(ord_itm):
                conf_list.append(f"  • {item[2]:2d} x {item[0]}")
            window["txt_conf_list"].update("\n".join(conf_list))

            # update order file
            upd_ord(ord_itm, sys_id, ord_tot)

            # start time out counter and show confirmation page
            sts_tout = time_cnt
            show_screen(4)

    if event in ("go_home2", "go_home3"):
        if ord_itm:
            choice_clear = sg.popup_ok_cancel("You are about to clear your cart!", title="OnlyPizza")
            if choice_clear == "OK":
                homereset()
        else:
            homereset()

    if event == "go_home4" or event == "__TIMEOUT__":
        homereset()

    # customer clicked one of the review buttons
    if event.startswith("key_conf_rev_"):
        key_parts = event.split("_")
        happy = key_parts[3].title()
        if happy == "Unhappy":
            window["txt_conf_thank"].update("Oh, please tell a staff member so we can fix it immediately.")
        else:
            window["txt_conf_thank"].update("Thank you for your review.")
        window.refresh()

        # Saving customer review with order num and date/time
        now = dt.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        numeric_ts = str(int(now.timestamp()))
        try:
            with open(dsn_revw, "a") as f:
                f.write(",".join([str(sys_id), date_str, numeric_ts, happy]) + "\n")
        except Exception as e:
            sg.popup_error("File Error", f"Could not save customer review:\n{e}")

        for key in list(window.key_dict.keys()):
            if isinstance(key, str) and key.startswith("key_conf_rev_"):
                window[key].update(disabled=True)       # disable all review buttons
        window.refresh()

# .close(): Properly shuts down the window and cleans up system resources
window.close()
