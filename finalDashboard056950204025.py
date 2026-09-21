"""
โปรแกรมเดียวจบ: คำนวณข้อมูลผ่อนชำระคอนโด + สร้างรายงาน/กราฟนำเสนอข้อมูล
--------------------------------------------------------------------------
- อ่านข้อมูลลูกค้าจาก condo.csv (ถ้าไม่พบจะลองอ่าน condo.txt แทน)
- คำนวณ ค่างวด/เดือน, ยอดชำระรวม (total) และดอกเบี้ยรวม ด้วยอัตราดอกเบี้ยอ้างอิง 5.25%
- บันทึกผลลัพธ์ลงไฟล์ condo_output.csv
- พิมพ์สรุปข้อมูลภาพรวมออกทางหน้าจอ (console)
- สร้างกราฟนำเสนอข้อมูล 2 รูป บันทึกเป็นไฟล์ภาพ (.png):
    1) condo_bar_chart.png   : เงินต้น vs ดอกเบี้ยรวม ต่อลูกค้า (แท่งซ้อน)
    2) condo_scatter_chart.png : ความสัมพันธ์ จำนวนปีที่ผ่อน กับ ค่างวด/เดือน

ไม่ต้องเชื่อมต่อ GitHub หรือ Streamlit ใด ๆ — รันได้ตรง ๆ ด้วยคำสั่ง:
    python condo_report.py

ไลบรารีที่ต้องติดตั้ง (ถ้ายังไม่มี):
    pip install pandas matplotlib
"""

import csv
import os
import re

import matplotlib
matplotlib.use("Agg")  # ให้บันทึกไฟล์ภาพได้โดยไม่ต้องเปิดหน้าต่างแสดงผล
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# ค่าคงที่
# ---------------------------------------------------------------------------
DEFAULT_CSV_FILE = "condo.csv"
DEFAULT_TXT_FILE = "condo.txt"
OUTPUT_FILENAME = "condo_output.csv"
BAR_CHART_FILENAME = "condo_bar_chart.png"
SCATTER_CHART_FILENAME = "condo_scatter_chart.png"
INTEREST_RATE = 0.0525  # อัตราดอกเบี้ยอ้างอิง 5.25% ต่อปี

OUTPUT_HEADERS = [
    "ชื่อลูกค้า",
    "จำนวนเงินต้น",
    "จำนวนปีที่ผ่อน",
    "ค่างวด/เดือน",
    "ยอดชำระรวม",
    "ดอกเบี้ยรวม",
]

# เลือกฟอนต์ที่รองรับภาษาไทยอัตโนมัติจากฟอนต์ที่มีอยู่ในเครื่อง (กันปัญหากราฟขึ้นเป็นสี่เหลี่ยม/ตัวอักษรไทยไม่ขึ้น)
# ถ้าไม่พบฟอนต์ไทยเลย จะใช้ฟอนต์เริ่มต้นของระบบแทน (อาจแสดงภาษาไทยไม่ได้)
_THAI_FONT_CANDIDATES = ["Tahoma", "Leelawadee UI", "Leelawadee", "Angsana New", "Cordia New", "TH Sarabun New"]
_available_fonts = {f.name for f in font_manager.fontManager.ttflist}
_chosen_font = next((f for f in _THAI_FONT_CANDIDATES if f in _available_fonts), None)
if _chosen_font:
    plt.rcParams["font.family"] = _chosen_font
plt.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------------------
# ฟังก์ชันช่วยแปลงค่า
# ---------------------------------------------------------------------------
def extract_years(text):
    """ดึงจำนวนปีที่เป็นตัวเลขออกจากข้อความ เช่น '5 ปี' -> 5"""
    match = re.search(r"\d+(\.\d+)?", str(text))
    if not match:
        raise ValueError(f"ไม่พบจำนวนปีที่ถูกต้องในค่า: {text!r}")
    return float(match.group())


def extract_number(text):
    """ดึงตัวเลขออกจากข้อความ เช่น '1,000,000' -> 1000000.0"""
    return float(str(text).replace(",", "").strip())


def resolve_input_file():
    """ใช้ condo.csv เป็นหลัก ถ้าไม่พบให้ลองใช้ condo.txt แทน"""
    if os.path.exists(DEFAULT_CSV_FILE):
        return DEFAULT_CSV_FILE
    if os.path.exists(DEFAULT_TXT_FILE):
        return DEFAULT_TXT_FILE
    return None


# ---------------------------------------------------------------------------
# อ่านข้อมูล + คำนวณ
# ---------------------------------------------------------------------------
def read_input(filename):
    """อ่านไฟล์ข้อมูลลูกค้า คอลัมน์: ชื่อลูกค้า, จำนวนเงินต้น, จำนวนปีที่ผ่อน"""
    rows = []
    with open(filename, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # ข้ามแถวหัวคอลัมน์
        for row in reader:
            if not row or len(row) < 3:
                continue
            name, principal_text, years_text = row[0].strip(), row[1].strip(), row[2].strip()
            rows.append((name, principal_text, years_text))
    return rows


def calculate_row(name, principal_text, years_text):
    principal = extract_number(principal_text)
    years = extract_years(years_text)

    total_interest = principal * INTEREST_RATE * years          # ดอกเบี้ยรวม
    total_payment = principal + total_interest                  # ยอดชำระรวม (total)
    monthly_payment = total_payment / (years * 12)               # ค่างวด/เดือน

    return {
        "ชื่อลูกค้า": name,
        "จำนวนเงินต้น": principal,
        "จำนวนปีที่ผ่อน": years,
        "ค่างวด/เดือน": monthly_payment,
        "ยอดชำระรวม": total_payment,
        "ดอกเบี้ยรวม": total_interest,
    }


def save_output(results, filename=OUTPUT_FILENAME):
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        for r in results:
            writer.writerow(
                {
                    "ชื่อลูกค้า": r["ชื่อลูกค้า"],
                    "จำนวนเงินต้น": f"{r['จำนวนเงินต้น']:,.2f}",
                    "จำนวนปีที่ผ่อน": f"{r['จำนวนปีที่ผ่อน']:.0f} ปี",
                    "ค่างวด/เดือน": f"{r['ค่างวด/เดือน']:,.2f}",
                    "ยอดชำระรวม": f"{r['ยอดชำระรวม']:,.2f}",
                    "ดอกเบี้ยรวม": f"{r['ดอกเบี้ยรวม']:,.2f}",
                }
            )


# ---------------------------------------------------------------------------
# นำเสนอข้อมูล: สรุปทางหน้าจอ + กราฟ
# ---------------------------------------------------------------------------
def print_summary(results):
    total_customers = len(results)
    total_principal = sum(r["จำนวนเงินต้น"] for r in results)
    total_payment = sum(r["ยอดชำระรวม"] for r in results)
    total_interest = sum(r["ดอกเบี้ยรวม"] for r in results)

    print("=" * 70)
    print("สรุปข้อมูลภาพรวมการผ่อนชำระคอนโด")
    print("=" * 70)
    print(f"จำนวนลูกค้าทั้งหมด   : {total_customers} คน")
    print(f"เงินต้นรวมทั้งหมด    : {total_principal:,.2f} บาท")
    print(f"ยอดชำระรวมทั้งหมด   : {total_payment:,.2f} บาท")
    print(f"ดอกเบี้ยรวมทั้งหมด   : {total_interest:,.2f} บาท")
    print(f"(อัตราดอกเบี้ยอ้างอิง {INTEREST_RATE * 100:.2f}% ต่อปี)")
    print("=" * 70)

    # ตารางเปรียบเทียบแบบข้อความ (console table)
    header = f"{'ชื่อลูกค้า':<24}{'เงินต้น':>14}{'ปีที่ผ่อน':>10}{'ค่างวด/ด.':>14}{'ยอดชำระรวม':>16}{'ดอกเบี้ยรวม':>16}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['ชื่อลูกค้า']:<24}"
            f"{r['จำนวนเงินต้น']:>14,.0f}"
            f"{r['จำนวนปีที่ผ่อน']:>10.0f}"
            f"{r['ค่างวด/เดือน']:>14,.0f}"
            f"{r['ยอดชำระรวม']:>16,.0f}"
            f"{r['ดอกเบี้ยรวม']:>16,.0f}"
        )
    print()


def create_bar_chart(results, filename=BAR_CHART_FILENAME):
    """กราฟแท่งซ้อน: เงินต้น vs ดอกเบี้ยรวม ต่อลูกค้า"""
    names = [r["ชื่อลูกค้า"] for r in results]
    principals = [r["จำนวนเงินต้น"] for r in results]
    interests = [r["ดอกเบี้ยรวม"] for r in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(names, principals, label="เงินต้น", color="#4C78A8")
    ax.bar(names, interests, bottom=principals, label="ดอกเบี้ยรวม", color="#E45756")
    ax.set_title("สัดส่วนเงินต้น vs ดอกเบี้ยรวม (ยอดชำระรวม)")
    ax.set_ylabel("จำนวนเงิน (บาท)")
    ax.set_xlabel("ลูกค้า")
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def create_scatter_chart(results, filename=SCATTER_CHART_FILENAME):
    """กราฟกระจาย: จำนวนปีที่ผ่อน กับ ค่างวด/เดือน"""
    fig, ax = plt.subplots(figsize=(8, 5))
    for r in results:
        ax.scatter(r["จำนวนปีที่ผ่อน"], r["ค่างวด/เดือน"], s=120, label=r["ชื่อลูกค้า"])
    ax.set_title("ความสัมพันธ์ระหว่างจำนวนปีที่ผ่อน (ปี) กับค่างวด/เดือน")
    ax.set_xlabel("จำนวนปีที่ผ่อน (ปี)")
    ax.set_ylabel("ค่างวด/เดือน (บาท)")
    ax.legend(title="ลูกค้า", fontsize=8)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    input_filename = resolve_input_file()
    if input_filename is None:
        print(f"ไม่พบไฟล์ข้อมูลนำเข้า (ต้องมี {DEFAULT_CSV_FILE} หรือ {DEFAULT_TXT_FILE} อยู่ในโฟลเดอร์เดียวกัน)")
        return

    raw_rows = read_input(input_filename)
    if not raw_rows:
        print("ไม่พบข้อมูลในไฟล์นำเข้า")
        return

    results = []
    for name, principal_text, years_text in raw_rows:
        try:
            results.append(calculate_row(name, principal_text, years_text))
        except ValueError as e:
            print(f"ข้ามแถวที่มีข้อมูลไม่ถูกต้อง ({name}): {e}")

    if not results:
        print("ไม่มีข้อมูลที่คำนวณได้")
        return

    save_output(results)
    print_summary(results)
    create_bar_chart(results)
    create_scatter_chart(results)

    print(f"บันทึกไฟล์ผลลัพธ์: {os.path.abspath(OUTPUT_FILENAME)}")
    print(f"บันทึกกราฟ       : {os.path.abspath(BAR_CHART_FILENAME)}")
    print(f"บันทึกกราฟ       : {os.path.abspath(SCATTER_CHART_FILENAME)}")


if __name__ == "__main__":
    main()