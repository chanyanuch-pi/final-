"""
โปรแกรม GUI สำหรับบันทึกข้อมูลลูกค้า (เงินกู้/ผ่อนคอนโด) ลงไฟล์ condo.csv
คอลัมน์: ชื่อลูกค้า, จำนวนเงินต้น, จำนวนปีที่ผ่อน
ใช้ tkinter (มีมาพร้อม Python มาตรฐาน ไม่ต้องติดตั้งเพิ่ม)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

CSV_FILENAME = "condo.csv"
HEADERS = ["ชื่อลูกค้า", "จำนวนเงินต้น", "จำนวนปีที่ผ่อน"]

# ข้อมูลตัวอย่างตามที่กำหนด (สามารถกดปุ่มโหลดข้อมูลตัวอย่างได้)
SAMPLE_DATA = [
    ["นายสมชาย ใจดี", "1000000", "5 ปี"],
    ["นางสาวสุภาวดี มีสุข", "2000000", "10 ปี"],
    ["นายวิทยา รุ่งเรือง", "3000000", "15 ปี"],
    ["นางสาวพิมพ์ชนก แสงทอง", "4000000", "20 ปี"],
    ["นายธนกร มั่นคง", "5000000", "25 ปี"],
]


class CondoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมบันทึกข้อมูลลูกค้า - condo.csv")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        self._build_input_frame()
        self._build_table()
        self._build_button_frame()

        self.load_csv_to_table()  # โหลดข้อมูลเดิม (ถ้ามีไฟล์อยู่แล้ว) มาแสดง

    # ---------- ส่วนกรอกข้อมูล ----------
    def _build_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="กรอกข้อมูลลูกค้า")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="ชื่อลูกค้า:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = ttk.Entry(frame, width=30)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="จำนวนเงินต้น:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_principal = ttk.Entry(frame, width=15)
        self.entry_principal.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame, text="จำนวนปีที่ผ่อน:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_years = ttk.Entry(frame, width=12)
        self.entry_years.grid(row=0, column=5, padx=5, pady=5)

    # ---------- ส่วนตารางแสดงข้อมูล ----------
    def _build_table(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame, columns=HEADERS, show="headings", height=10)
        for col in HEADERS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=190)
        self.tree.pack(fill="both", expand=True)

    # ---------- ส่วนปุ่มกด ----------
    def _build_button_frame(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(frame, text="เพิ่มข้อมูล", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(frame, text="ลบรายการที่เลือก", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(frame, text="โหลดข้อมูลตัวอย่าง (5 รายการ)", command=self.load_sample_data).pack(side="left", padx=5)
        ttk.Button(frame, text="บันทึกลง condo.csv", command=self.save_to_csv).pack(side="left", padx=5)
        ttk.Button(frame, text="ล้างตาราง", command=self.clear_table).pack(side="left", padx=5)

    # ---------- ฟังก์ชันการทำงาน ----------
    def add_record(self):
        name = self.entry_name.get().strip()
        principal = self.entry_principal.get().strip()
        years = self.entry_years.get().strip()

        if not name or not principal or not years:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return

        self.tree.insert("", "end", values=(name, principal, years))

        # ล้างช่องกรอกหลังเพิ่มข้อมูลแล้ว
        self.entry_name.delete(0, "end")
        self.entry_principal.delete(0, "end")
        self.entry_years.delete(0, "end")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
            return
        for item in selected:
            self.tree.delete(item)

    def load_sample_data(self):
        # ล้างข้อมูลเดิมในตารางก่อน แล้วโหลดข้อมูลตัวอย่าง 5 รายการ
        self.clear_table()
        for row in SAMPLE_DATA:
            self.tree.insert("", "end", values=row)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def save_to_csv(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("ไม่มีข้อมูล", "ไม่มีข้อมูลให้บันทึก กรุณาเพิ่มข้อมูลก่อน")
            return

        try:
            with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS)
                writer.writerows(rows)
            messagebox.showinfo(
                "บันทึกสำเร็จ",
                f"บันทึกข้อมูลจำนวน {len(rows)} รายการ ลงไฟล์ {os.path.abspath(CSV_FILENAME)} เรียบร้อยแล้ว",
            )
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {e}")

    def load_csv_to_table(self):
        # ถ้ามีไฟล์ condo.csv อยู่แล้ว ให้โหลดข้อมูลเดิมขึ้นมาแสดงในตาราง
        if os.path.exists(CSV_FILENAME):
            try:
                with open(CSV_FILENAME, mode="r", newline="", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # ข้ามหัวคอลัมน์
                    for row in reader:
                        if row:
                            self.tree.insert("", "end", values=row)
            except Exception:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CondoApp(root)
    root.mainloop()