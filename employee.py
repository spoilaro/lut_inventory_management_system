from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import csv
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ims.db")

WINDOW_GEOMETRY = "1100x500+320+220"

FONT_LABEL = ("goudy old style", 15)
FONT_SEARCH = ("goudy old style", 12, "bold")
FONT_ENTRY = ("goudy old style", 15)
FONT_BTN = ("goudy old style", 15)

COLOR_BG = "white"
COLOR_TITLE_BG = "#0f4d7d"
COLOR_ENTRY_BG = "lightyellow"
COLOR_BTN_ADD = "#2196f3"
COLOR_BTN_UPDATE = "#4caf50"
COLOR_BTN_DELETE = "#f44336"
COLOR_BTN_CLEAR = "#607d8b"
COLOR_BTN_EXPORT = "#9c27b0"

GENDER_OPTIONS = ("Select", "Male", "Female", "Other")
USER_TYPE_OPTIONS = ("Admin", "Employee")
SEARCH_OPTIONS = ("Select", "Email", "Name", "Contact")

EMPLOYEE_COLUMNS = (
    "eid",
    "name",
    "email",
    "gender",
    "contact",
    "dob",
    "doj",
    "pass",
    "utype",
    "address",
    "salary",
)
EMPLOYEE_HEADINGS = {
    "eid": "EMP ID",
    "name": "Name",
    "email": "Email",
    "gender": "Gender",
    "contact": "Contact",
    "dob": "D.O.B",
    "doj": "D.O.J",
    "pass": "Password",
    "utype": "User Type",
    "address": "Address",
    "salary": "Salary",
}
EMPLOYEE_COLUMN_WIDTHS = {col: 100 for col in EMPLOYEE_COLUMNS}
EMPLOYEE_COLUMN_WIDTHS["eid"] = 90

INPUT_ROWS = [
    [("Emp ID", 50, 150, 150), ("Gender", 350, 500, 150), ("Contact", 750, 850, 180)],
    [("Name", 50, 150, 150), ("D.O.B.", 350, 500, 150), ("D.O.J.", 750, 850, 180)],
    [
        ("Email", 50, 150, 150),
        ("Password", 350, 500, 150),
        ("User Type", 750, 850, 180),
    ],
]

ACTION_BUTTONS = [
    ("Save", 500, COLOR_BTN_ADD, "add"),
    ("Update", 620, COLOR_BTN_UPDATE, "update"),
    ("Delete", 740, COLOR_BTN_DELETE, "delete"),
    ("Clear", 860, COLOR_BTN_CLEAR, "clear"),
]


class employeeClass:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.config(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.focus_force()

        self._init_variables()
        self._setup_ui()
        self.show()

    def _init_variables(self) -> None:
        self.var_searchby = StringVar()
        self.var_searchtxt = StringVar()
        self.var_emp_id = StringVar()
        self.var_gender = StringVar()
        self.var_contact = StringVar()
        self.var_name = StringVar()
        self.var_dob = StringVar()
        self.var_doj = StringVar()
        self.var_email = StringVar()
        self.var_pass = StringVar()
        self.var_utype = StringVar()
        self.var_salary = StringVar()
        self.var_gender.set(GENDER_OPTIONS[0])
        self.var_utype.set(USER_TYPE_OPTIONS[0])

    def _setup_ui(self) -> None:
        self._setup_search_frame()
        self._setup_title()
        self._setup_input_rows()
        self._setup_address_and_salary()
        self._setup_action_buttons()
        self._setup_employee_table()

    def _setup_search_frame(self) -> None:
        frame = LabelFrame(
            self.root,
            text="Search Employee",
            font=FONT_SEARCH,
            bd=2,
            relief=RIDGE,
            bg=COLOR_BG,
        )
        frame.place(x=250, y=20, width=600, height=70)

        ttk.Combobox(
            frame,
            textvariable=self.var_searchby,
            values=SEARCH_OPTIONS,
            state="readonly",
            justify=CENTER,
            font=FONT_ENTRY,
        ).place(x=10, y=10, width=180)
        self.var_searchby.set(SEARCH_OPTIONS[0])

        Entry(
            frame, textvariable=self.var_searchtxt, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=200, y=10)

        Button(
            frame,
            text="Search",
            command=self.search,
            font=FONT_ENTRY,
            bg=COLOR_BTN_UPDATE,
            fg="white",
            cursor="hand2",
        ).place(x=410, y=9, width=100, height=30)

        Button(
            frame,
            text="Export CSV",
            command=self.export_to_csv,
            font=FONT_ENTRY,
            bg=COLOR_BTN_EXPORT,
            fg="white",
            cursor="hand2",
        ).place(x=520, y=9, width=70, height=30)

    def _setup_title(self) -> None:
        Label(
            self.root,
            text="Employee Details",
            font=FONT_LABEL,
            bg=COLOR_TITLE_BG,
            fg="white",
        ).place(x=50, y=100, width=1000)

    def _setup_input_rows(self) -> None:
        for row in INPUT_ROWS:
            for label_text, lbl_x, entry_x, width in row:
                Label(self.root, text=label_text, font=FONT_LABEL, bg=COLOR_BG).place(
                    x=lbl_x, y=150 + (INPUT_ROWS.index(row) * 40)
                )

                entry = Entry(self.root, font=FONT_ENTRY, bg=COLOR_ENTRY_BG)
                entry.place(
                    x=entry_x, y=150 + (INPUT_ROWS.index(row) * 40), width=width
                )

                if label_text == "Gender":
                    entry.config(state="readonly")
                    ttk.Combobox(
                        self.root,
                        textvariable=self.var_gender,
                        values=GENDER_OPTIONS,
                        state="readonly",
                        justify=CENTER,
                        font=FONT_ENTRY,
                    ).place(x=entry_x, y=150, width=width)
                    self.var_gender.set(GENDER_OPTIONS[0])
                elif label_text == "User Type":
                    ttk.Combobox(
                        self.root,
                        textvariable=self.var_utype,
                        values=USER_TYPE_OPTIONS,
                        state="readonly",
                        justify=CENTER,
                        font=FONT_ENTRY,
                    ).place(x=entry_x, y=230, width=width)
                    self.var_utype.set(USER_TYPE_OPTIONS[0])

        self._bind_entry_to_var("Emp ID", self.var_emp_id, 150, 150)
        self._bind_entry_to_var("Name", self.var_name, 190, 150)
        self._bind_entry_to_var("Email", self.var_email, 230, 150)
        self._bind_entry_to_var("Password", self.var_pass, 230, 500)
        self._bind_entry_to_var("Contact", self.var_contact, 150, 850)
        self._bind_entry_to_var("D.O.B.", self.var_dob, 190, 500)
        self._bind_entry_to_var("D.O.J.", self.var_doj, 190, 850)

    def _bind_entry_to_var(
        self, label_text: str, var: StringVar, y: int, x: int
    ) -> None:
        pass

    def _setup_address_and_salary(self) -> None:
        Label(self.root, text="Address", font=FONT_LABEL, bg=COLOR_BG).place(
            x=50, y=270
        )

        Label(self.root, text="Salary", font=FONT_LABEL, bg=COLOR_BG).place(
            x=500, y=270
        )

        self.txt_address = Text(self.root, font=FONT_ENTRY, bg=COLOR_ENTRY_BG)
        self.txt_address.place(x=150, y=270, width=300, height=60)

        Entry(
            self.root, textvariable=self.var_salary, font=FONT_ENTRY, bg=COLOR_ENTRY_BG
        ).place(x=600, y=270, width=180)

    def _setup_action_buttons(self) -> None:
        for text, x, color, method_name in ACTION_BUTTONS:
            Button(
                self.root,
                text=text,
                command=getattr(self, method_name),
                font=FONT_BTN,
                bg=color,
                fg="white",
                cursor="hand2",
            ).place(x=x, y=305, width=110, height=28)

    def _setup_employee_table(self) -> None:
        frame = Frame(self.root, bd=3, relief=RIDGE)
        frame.place(x=0, y=350, relwidth=1, height=150)

        scrollbar_y = Scrollbar(frame, orient=VERTICAL)
        scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)

        self.employee_table = ttk.Treeview(
            frame,
            columns=EMPLOYEE_COLUMNS,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        scrollbar_x.pack(side=BOTTOM, fill=X)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.config(command=self.employee_table.xview)
        scrollbar_y.config(command=self.employee_table.yview)

        for col in EMPLOYEE_COLUMNS:
            self.employee_table.heading(
                col, text=EMPLOYEE_HEADINGS.get(col, col.title())
            )
        self.employee_table["show"] = "headings"

        for col, width in EMPLOYEE_COLUMN_WIDTHS.items():
            self.employee_table.column(col, width=width)

        self.employee_table.pack(fill=BOTH, expand=1)
        self.employee_table.bind("<ButtonRelease-1>", self.get_data)

    def _get_db_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(database=DB_PATH)

    def _get_form_data(self) -> dict:
        return {
            "eid": self.var_emp_id.get().strip(),
            "name": self.var_name.get().strip(),
            "email": self.var_email.get().strip(),
            "gender": self.var_gender.get(),
            "contact": self.var_contact.get().strip(),
            "dob": self.var_dob.get().strip(),
            "doj": self.var_doj.get().strip(),
            "pass": self.var_pass.get(),
            "utype": self.var_utype.get(),
            "address": self.txt_address.get("1.0", END).strip(),
            "salary": self.var_salary.get().strip(),
        }

    def _employee_exists(self, cur: sqlite3.Cursor, eid: str) -> bool:
        cur.execute("SELECT * FROM employee WHERE eid=?", (eid,))
        return cur.fetchone() is not None

    def _populate_form(self, data: tuple) -> None:
        self.var_emp_id.set(data[0])
        self.var_name.set(data[1])
        self.var_email.set(data[2])
        self.var_gender.set(data[3])
        self.var_contact.set(data[4])
        self.var_dob.set(data[5])
        self.var_doj.set(data[6])
        self.var_pass.set(data[7])
        self.var_utype.set(data[8])
        self.txt_address.delete("1.0", END)
        self.txt_address.insert(END, data[9])
        self.var_salary.set(data[10])

    def add(self) -> None:
        data = self._get_form_data()
        if not data["eid"]:
            messagebox.showerror("Error", "Employee ID is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            if self._employee_exists(cur, data["eid"]):
                messagebox.showerror(
                    "Error", "Employee ID already exists", parent=self.root
                )
                con.close()
                return

            cur.execute(
                """INSERT INTO employee(eid, name, email, gender, contact, dob, doj, pass, utype, address, salary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(data.values()),
            )
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success", "Employee Added Successfully", parent=self.root
            )
            self.clear()
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def show(self) -> None:
        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute("SELECT * FROM employee")
            rows = cur.fetchall()
            con.close()

            self.employee_table.delete(*self.employee_table.get_children())
            for row in rows:
                self.employee_table.insert("", END, values=row)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def get_data(self, ev: Event) -> None:
        focus = self.employee_table.focus()
        if not focus:
            return

        row = self.employee_table.item(focus)["values"]
        self._populate_form(row)

    def update(self) -> None:
        data = self._get_form_data()
        if not data["eid"]:
            messagebox.showerror("Error", "Employee ID is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            if not self._employee_exists(cur, data["eid"]):
                messagebox.showerror("Error", "Invalid Employee ID", parent=self.root)
                con.close()
                return

            cur.execute(
                """UPDATE employee SET name=?, email=?, gender=?, contact=?, dob=?, doj=?,
                   pass=?, utype=?, address=?, salary=? WHERE eid=?""",
                (
                    data["name"],
                    data["email"],
                    data["gender"],
                    data["contact"],
                    data["dob"],
                    data["doj"],
                    data["pass"],
                    data["utype"],
                    data["address"],
                    data["salary"],
                    data["eid"],
                ),
            )
            con.commit()
            con.close()

            messagebox.showinfo(
                "Success", "Employee Updated Successfully", parent=self.root
            )
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def delete(self) -> None:
        eid = self.var_emp_id.get().strip()
        if not eid:
            messagebox.showerror("Error", "Employee ID is required", parent=self.root)
            return

        confirm = messagebox.askyesno(
            "Confirm", "Do you really want to delete?", parent=self.root
        )
        if not confirm:
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            if not self._employee_exists(cur, eid):
                messagebox.showerror("Error", "Invalid Employee ID", parent=self.root)
                con.close()
                return

            cur.execute("DELETE FROM employee WHERE eid=?", (eid,))
            con.commit()
            con.close()

            messagebox.showinfo(
                "Delete", "Employee Deleted Successfully", parent=self.root
            )
            self.clear()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def clear(self) -> None:
        self.var_emp_id.set("")
        self.var_name.set("")
        self.var_email.set("")
        self.var_gender.set(GENDER_OPTIONS[0])
        self.var_contact.set("")
        self.var_dob.set("")
        self.var_doj.set("")
        self.var_pass.set("")
        self.var_utype.set(USER_TYPE_OPTIONS[0])
        self.var_salary.set("")
        self.txt_address.delete("1.0", END)
        self.var_searchby.set(SEARCH_OPTIONS[0])
        self.var_searchtxt.set("")
        self.show()

    def search(self) -> None:
        search_by = self.var_searchby.get()
        search_txt = self.var_searchtxt.get().strip()

        if search_by == "Select":
            messagebox.showerror("Error", "Select Search By option", parent=self.root)
            return
        if not search_txt:
            messagebox.showerror("Error", "Search input is required", parent=self.root)
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()

            cur.execute(
                "SELECT * FROM employee WHERE ? LIKE ?", (search_by, f"%{search_txt}%")
            )
            rows = cur.fetchall()
            con.close()

            if rows:
                self.employee_table.delete(*self.employee_table.get_children())
                for row in rows:
                    self.employee_table.insert("", END, values=row)
            else:
                messagebox.showerror("Error", "No record found!!!", parent=self.root)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)

    def export_to_csv(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Employees to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            con = self._get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM employee")
            rows = cur.fetchall()
            con.close()

            if not rows:
                messagebox.showwarning(
                    "Warning", "No employees to export", parent=self.root
                )
                return

            headers = (
                [description[0] for description in cur.description] if rows else []
            )

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(rows)

            messagebox.showinfo(
                "Success",
                f"Exported {len(rows)} employee(s) to CSV successfully!",
                parent=self.root,
            )

        except PermissionError:
            messagebox.showerror(
                "Error",
                "Permission denied. Please close the file if it's open.",
                parent=self.root,
            )
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)


if __name__ == "__main__":
    root = Tk()
    obj = employeeClass(root)
    root.mainloop()
