from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import time
import sqlite3
import os

from employee import employeeClass
from supplier import supplierClass
from category import categoryClass
from product import productClass
from sales import salesClass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
BILL_DIR = os.path.join(BASE_DIR, "bill")
DB_PATH = os.path.join(BASE_DIR, "ims.db")

os.makedirs(BILL_DIR, exist_ok=True)

WINDOW_GEOMETRY = "1350x700+110+80"
WINDOW_WIDTH = 1350
WINDOW_HEIGHT = 700

MENU_WIDTH = 200
MENU_Y = 102
MENU_HEIGHT = 565

TITLE_HEIGHT = 70
CLOCK_HEIGHT = 30
CLOCK_Y = 70

FONT_TITLE = ("times new roman", 40, "bold")
FONT_MENU = ("times new roman", 20, "bold")
FONT_FOOTER = ("times new roman", 12)
FONT_STATS = ("goudy old style", 20, "bold")

COLOR_BG = "white"
COLOR_TITLE_BG = "#010c48"
COLOR_FOOTER_BG = "#4d636d"
COLOR_MENU_HEADER_BG = "#009688"
COLOR_MENU_BTN_BG = "white"
COLOR_LOGOUT_BG = "yellow"

STAT_COLORS = {
    "employee": "#33bbf9",
    "supplier": "#ff5722",
    "category": "#009688",
    "product": "#607d8b",
    "sales": "#ffc107",
}


class IMS:
    NAV_ITEMS = [
        ("Employee", "employee"),
        ("Supplier", "supplier"),
        ("Category", "category"),
        ("Products", "product"),
        ("Sales", "sales"),
    ]

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.resizable(False, False)
        self.root.config(bg=COLOR_BG)

        self._setup_title()
        self._setup_logout_button()
        self._setup_clock()
        self._setup_menu()
        self._setup_statistics()
        self._setup_footer()

        self.update_content()

    def _setup_title(self) -> None:
        self.icon_title = PhotoImage(file=os.path.join(IMAGE_DIR, "logo1.png"))
        Label(
            self.root,
            text="Inventory Management System",
            image=self.icon_title,
            compound=LEFT,
            font=FONT_TITLE,
            bg=COLOR_TITLE_BG,
            fg="white",
            anchor="w",
            padx=20,
        ).place(x=0, y=0, relwidth=1, height=TITLE_HEIGHT)

    def _setup_logout_button(self) -> None:
        Button(
            self.root,
            text="Logout",
            font=("times new roman", 15, "bold"),
            bg=COLOR_LOGOUT_BG,
            cursor="hand2",
        ).place(x=1150, y=10, height=50, width=150)

    def _setup_clock(self) -> None:
        self.lbl_clock = Label(
            self.root,
            text="Welcome to Inventory Management System\t\t Date: DD:MM:YYYY\t\t Time: HH:MM:SS",
            font=("times new roman", 15),
            bg=COLOR_FOOTER_BG,
            fg="white",
        )
        self.lbl_clock.place(x=0, y=CLOCK_Y, relwidth=1, height=CLOCK_HEIGHT)

    def _setup_menu(self) -> None:
        left_menu = Frame(self.root, bd=2, relief=RIDGE, bg=COLOR_BG)
        left_menu.place(x=0, y=MENU_Y, width=MENU_WIDTH, height=MENU_HEIGHT)

        self._setup_menu_logo(left_menu)
        self._create_menu_buttons(left_menu)

    def _setup_menu_logo(self, parent: Frame) -> None:
        menu_logo = Image.open(os.path.join(IMAGE_DIR, "menu_im.png"))
        menu_logo = menu_logo.resize((MENU_WIDTH, 200))
        self.menu_logo = ImageTk.PhotoImage(menu_logo)

        Label(parent, image=self.menu_logo).pack(side=TOP, fill=X)
        Label(parent, text="Menu", font=FONT_MENU, bg=COLOR_MENU_HEADER_BG).pack(
            side=TOP, fill=X
        )

    def _create_menu_buttons(self, parent: Frame) -> None:
        self.icon_side = PhotoImage(file=os.path.join(IMAGE_DIR, "side.png"))

        for label, method_name in self.NAV_ITEMS:
            Button(
                parent,
                text=label,
                command=getattr(self, method_name),
                image=self.icon_side,
                compound=LEFT,
                padx=5,
                anchor="w",
                font=FONT_MENU,
                bg=COLOR_MENU_BTN_BG,
                bd=3,
                cursor="hand2",
            ).pack(side=TOP, fill=X)

        Button(
            parent,
            text="Exit",
            image=self.icon_side,
            compound=LEFT,
            padx=5,
            anchor="w",
            font=FONT_MENU,
            bg=COLOR_MENU_BTN_BG,
            bd=3,
            cursor="hand2",
            command=self.root.destroy,
        ).pack(side=TOP, fill=X)

    def _setup_statistics(self) -> None:
        stats_config = [
            ("employee", 300, 120),
            ("supplier", 650, 120),
            ("category", 1000, 120),
            ("product", 300, 300),
            ("sales", 650, 300),
        ]

        self.stat_labels = {}
        for name, x, y in stats_config:
            label = Label(
                self.root,
                text=f"Total {name.capitalize()}\n[ 0 ]",
                bd=5,
                relief=RIDGE,
                bg=STAT_COLORS[name],
                fg="white",
                font=FONT_STATS,
            )
            label.place(x=x, y=y, height=150, width=300)
            self.stat_labels[name] = label

    def _setup_footer(self) -> None:
        Label(
            self.root,
            text="IMS-Inventory Management System",
            font=FONT_FOOTER,
            bg=COLOR_FOOTER_BG,
            fg="white",
        ).pack(side=BOTTOM, fill=X)

    def _open_module(self, module_class: type) -> None:
        self.new_win = Toplevel(self.root)
        self.new_obj = module_class(self.new_win)

    def employee(self) -> None:
        self._open_module(employeeClass)

    def supplier(self) -> None:
        self._open_module(supplierClass)

    def category(self) -> None:
        self._open_module(categoryClass)

    def product(self) -> None:
        self._open_module(productClass)

    def sales(self) -> None:
        self._open_module(salesClass)

    def _count_records(self, cur, table: str) -> int:
        cur.execute(f"SELECT * FROM {table}")
        return len(cur.fetchall())

    def _update_stat_label(
        self, cur, table: str, label: Label, label_name: str
    ) -> None:
        count = self._count_records(cur, table)
        label.config(text=f"Total {label_name.capitalize()}\n[ {count} ]")

    def update_content(self) -> None:
        try:
            con = sqlite3.connect(database=DB_PATH)
            cur = con.cursor()

            self._update_stat_label(
                cur, "product", self.stat_labels["product"], "product"
            )
            self._update_stat_label(
                cur, "category", self.stat_labels["category"], "category"
            )
            self._update_stat_label(
                cur, "employee", self.stat_labels["employee"], "employee"
            )
            self._update_stat_label(
                cur, "supplier", self.stat_labels["supplier"], "supplier"
            )

            con.close()

        except sqlite3.OperationalError:
            pass
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)

        self._update_clock()

    def _update_clock(self) -> None:
        current_time = time.strftime("%I:%M:%S")
        current_date = time.strftime("%d-%m-%Y")
        self.lbl_clock.config(
            text=f"Welcome to Inventory Management System\t\t Date: {current_date}\t\t Time: {current_time}"
        )
        self.lbl_clock.after(200, self.update_content)

    def update_sales_count(self) -> None:
        try:
            bill_count = len(os.listdir(BILL_DIR))
            self.stat_labels["sales"].config(text=f"Total Sales\n[ {bill_count} ]")
        except Exception:
            pass


if __name__ == "__main__":
    root = Tk()
    obj = IMS(root)
    root.mainloop()
