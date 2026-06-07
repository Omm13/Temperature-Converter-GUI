from tkinter import *
from tkinter import messagebox, filedialog
import threading
import re
import pandas as pd
from queue import Queue

conversion_queue = Queue()
history = []

# Conversion Functions
def c_to_f(c): return (c * 9 / 5) + 32
def f_to_c(f): return (f - 32) * 5 / 9

# Bulk Conversion Logic
def process_bulk_input(input_str):
    try:
        numbers = [float(num.strip()) for num in input_str.split(",")]
        return numbers
    except:
        return None

# Thread for Single/Bulk Conversion
def threaded_conversion(temps, unit):
    results = []
    for temp in temps:
        if unit == "C":
            result = c_to_f(temp)
            entry = f"{temp}°C = {result:.2f}°F"
        else:
            result = f_to_c(temp)
            entry = f"{temp}°F = {result:.2f}°C"
        conversion_queue.put(entry)
        history.append(entry)
        results.append(entry)
    return results

def convert_temperature():
    temp_input = entry_temp.get()
    if not temp_input:
        label_result.config(text="Please enter a value.")
        return

    temps = process_bulk_input(temp_input)
    if temps is None:
        label_result.config(text="Invalid input. Use numbers or commas.")
        return

    unit = var_unit.get()
    thread = threading.Thread(target=threaded_conversion, args=(temps, unit))
    thread.start()
    thread.join()

    results = []
    for _ in temps:
        results.append(conversion_queue.get())

    label_result.config(text="\n".join(results[-3:]))  # Show last 3
    text_output.delete("1.0", END)
    text_output.insert(END, "\n".join(results))

def show_history():
    if not history:
        messagebox.showinfo("History", "No conversions yet.")
    else:
        messagebox.showinfo("History", "\n".join(history[-5:]))

def clear_fields():
    entry_temp.delete(0, END)
    label_result.config(text="")
    text_output.delete("1.0", END)

def export_to_excel():
    if not history:
        messagebox.showinfo("Export", "No data to export.")
        return

    df = pd.DataFrame(history, columns=["Conversion"])
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if filepath:
        try:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Export", f"Exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export.\n{e}")
            
# Theme Switcher
def toggle_theme():
    global is_dark
    is_dark = not is_dark
    bg = "#1c1c1c" if is_dark else "#f2f2f2"
    fg = "white" if is_dark else "black"
    entry_temp.config(bg="white" if not is_dark else "#333", fg=fg)
    text_output.config(bg="white" if not is_dark else "#333", fg=fg)
    window.config(bg=bg)
    for widget in window.winfo_children():
        widget.config(bg=bg, fg=fg)
        if isinstance(widget, Frame):
            for sub in widget.winfo_children():
                sub.config(bg=bg, fg=fg)

# GUI Setup
window = Tk()
window.title("🌡 Temperature Converter")
window.geometry("400x450")
is_dark = False
window.configure(bg="#f2f2f2")

font_label = ("Arial", 11)

Label(window, text="Enter Temperature(s):", font=font_label, bg="#f2f2f2").pack(pady=5)
entry_temp = Entry(window, font=font_label, width=30, justify='center')
entry_temp.pack(pady=5)

Label(window, text="(e.g., 30 or 10,20,30)", bg="#f2f2f2").pack()

var_unit = StringVar(value="C")
options_frame = Frame(window, bg="#f2f2f2")
options_frame.pack(pady=5)
Radiobutton(options_frame, text="Celsius → Fahrenheit", variable=var_unit, value="C", bg="#f2f2f2").pack(side=LEFT, padx=5)
Radiobutton(options_frame, text="Fahrenheit → Celsius", variable=var_unit, value="F", bg="#f2f2f2").pack(side=LEFT, padx=5)

Button(window, text="Convert", command=convert_temperature, font=font_label, bg="#4CAF50", fg="white", width=12).pack(pady=8)
label_result = Label(window, text="", font=("Arial", 11), bg="#f2f2f2")
label_result.pack(pady=5)

Label(window, text="Output:", font=font_label, bg="#f2f2f2").pack(pady=5)
text_output = Text(window, height=5, width=40, font=("Arial", 10))
text_output.pack()

bottom_frame = Frame(window, bg="#f2f2f2")
bottom_frame.pack(pady=10)

Button(bottom_frame, text="History", command=show_history, bg="#2196F3", fg="white", font=("Arial", 10), width=10).pack(side=LEFT, padx=5)
Button(bottom_frame, text="Clear", command=clear_fields, bg="#f44336", fg="white", font=("Arial", 10), width=10).pack(side=LEFT, padx=5)
Button(bottom_frame, text="Export", command=export_to_excel, bg="#9C27B0", fg="white", font=("Arial", 10), width=10).pack(side=LEFT, padx=5)
Button(window, text="Toggle Theme", command=toggle_theme, bg="#607D8B", fg="white", font=("Arial", 10), width=25).pack(pady=10)

window.mainloop()
