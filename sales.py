from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
BILL_DIR = os.path.join(BASE_DIR, "bill")

os.makedirs(BILL_DIR, exist_ok=True)

WINDOW_GEOMETRY = "1100x500+320+220"

FONT_TITLE = ("goudy old style", 30)
FONT_LABEL = ("times new roman", 15)
FONT_BTN = ("times new roman", 15, "bold")
FONT_LIST = ("goudy old style", 15)
FONT_BILL_TITLE = ("goudy old style", 20)

COLOR_BG = "white"
COLOR_TITLE_BG = "#184a45"
COLOR_SEARCH_BG = "#2196f3"
COLOR_BILL_TITLE_BG = "orange"
COLOR_ENTRY_BG = "lightyellow"

BILL_LIST_WIDTH = 200
BILL_LIST_HEIGHT = 330
BILL_AREA_WIDTH = 410
BILL_AREA_HEIGHT = 330
IMAGE_WIDTH = 450
IMAGE_HEIGHT = 300


class salesClass:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.config(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.focus_force()

        self.invoice_numbers: list[str] = []
        self.var_invoice = StringVar()

        self._setup_ui()
        self.show()

    def _setup_ui(self) -> None:
        self._setup_title()
        self._setup_search_bar()
        self._setup_bill_list()
        self._setup_bill_area()
        self._setup_image()

    def _setup_title(self) -> None:
        Label(
            self.root,
            text="View Customer Bills",
            font=FONT_TITLE,
            bg=COLOR_TITLE_BG,
            fg="white",
            bd=3,
            relief=RIDGE,
        ).pack(side=TOP, fill=X, padx=10, pady=20)

    def _setup_search_bar(self) -> None:
        Label(self.root, text="Invoice No.", font=FONT_LABEL, bg=COLOR_BG).place(
            x=50, y=100
        )

        Entry(
            self.root, textvariable=self.var_invoice, font=FONT_LABEL, bg=COLOR_ENTRY_BG
        ).place(x=160, y=100, width=180, height=28)

        Button(
            self.root,
            text="Search",
            command=self.search,
            font=FONT_BTN,
            bg=COLOR_SEARCH_BG,
            fg="white",
            cursor="hand2",
        ).place(x=360, y=100, width=120, height=28)

        Button(
            self.root,
            text="Clear",
            command=self.clear,
            font=FONT_BTN,
            bg="lightgray",
            cursor="hand2",
        ).place(x=490, y=100, width=120, height=28)

    def _setup_bill_list(self) -> None:
        frame = Frame(self.root, bd=3, relief=RIDGE)
        frame.place(x=50, y=140, width=BILL_LIST_WIDTH, height=BILL_LIST_HEIGHT)

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.sales_list = Listbox(
            frame, font=FONT_LIST, bg=COLOR_BG, yscrollcommand=scrollbar.set
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.sales_list.yview)
        self.sales_list.pack(fill=BOTH, expand=1)
        self.sales_list.bind("<ButtonRelease-1>", self.get_data)

    def _setup_bill_area(self) -> None:
        frame = Frame(self.root, bd=3, relief=RIDGE)
        frame.place(x=280, y=140, width=BILL_AREA_WIDTH, height=BILL_AREA_HEIGHT)

        Label(
            frame,
            text="Customer Bill Area",
            font=FONT_BILL_TITLE,
            bg=COLOR_BILL_TITLE_BG,
        ).pack(side=TOP, fill=X)

        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.bill_area = Text(frame, bg=COLOR_ENTRY_BG, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.bill_area.yview)
        self.bill_area.pack(fill=BOTH, expand=1)

    def _setup_image(self) -> None:
        image_path = os.path.join(IMAGE_DIR, "cat2.jpg")
        photo = Image.open(image_path)
        photo = photo.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        self.bill_photo = ImageTk.PhotoImage(photo)

        Label(self.root, image=self.bill_photo, bd=0).place(x=700, y=110)

    def _get_bill_files(self) -> list[str]:
        try:
            return [
                f
                for f in os.listdir(BILL_DIR)
                if os.path.isfile(os.path.join(BILL_DIR, f)) and f.endswith(".txt")
            ]
        except FileNotFoundError:
            return []

    def _load_bill_content(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as fp:
                return fp.read()
        except (FileNotFoundError, PermissionError):
            return ""

    def _display_bill(self, file_path: str) -> bool:
        content = self._load_bill_content(file_path)
        if content:
            self.bill_area.delete("1.0", END)
            self.bill_area.insert(END, content)
            return True
        return False

    def show(self) -> None:
        self.invoice_numbers.clear()
        self.sales_list.delete(0, END)

        bill_files = self._get_bill_files()
        for filename in bill_files:
            self.sales_list.insert(END, filename)
            invoice = filename.rsplit(".", 1)[0]
            self.invoice_numbers.append(invoice)

    def get_data(self, ev: Event) -> None:
        selection = self.sales_list.curselection()
        if not selection:
            return

        filename = self.sales_list.get(selection)
        file_path = os.path.join(BILL_DIR, filename)
        self._display_bill(file_path)

    def search(self) -> None:
        invoice = self.var_invoice.get().strip()

        if not invoice:
            messagebox.showerror("Error", "Invoice no. is required", parent=self.root)
            return

        if invoice not in self.invoice_numbers:
            messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
            return

        file_path = os.path.join(BILL_DIR, f"{invoice}.txt")
        if not self._display_bill(file_path):
            messagebox.showerror("Error", "Could not load bill", parent=self.root)

    def clear(self) -> None:
        self.var_invoice.set("")
        self.bill_area.delete("1.0", END)
        self.show()


if __name__ == "__main__":
    root = Tk()
    obj = salesClass(root)
    root.mainloop()
