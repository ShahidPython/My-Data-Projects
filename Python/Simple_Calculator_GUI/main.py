import tkinter
from tkinter import *

root = Tk()
root.title("Simple Calculator")
root.geometry("570x600+100+200")
root.resizable(False, False)
root.config(bg="#17161b")

equation = ""

def show(value):
    global equation
    equation += value
    label_result.config(text=equation)

# to clear the equation and reset the display
def clear():
    global equation
    equation = ""
    label_result.config(text=equation)

# to evaluate the expression and show the result
def calculate():
    global equation
    result = ""
    if equation != "":
        try:
            # Handle percentage calculations
            if "%" in equation:
                if equation.endswith("%"):
                    # Case: 50% → 0.5
                    result = str(float(equation[:-1]) / 100)
                else:
                    # Case: 50%200 → 100 (50% of 200)
                    parts = equation.split("%")
                    if len(parts) == 2:
                        result = str(float(parts[0]) / 100 * float(parts[1]))
            else:
                # Normal calculation
                result = str(eval(equation))
            
            equation = result
        except:
            result = "Error"
            equation = ""
    label_result.config(text=result)

# Display label to show input and output
label_result = Label(root, width=25, height=2, text="", font=("Arial", 30))
label_result.pack()

# Calculator buttons
Button(root, text="C", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#3697f5", command=clear).place(x=10, y=100)
Button(root, text="/", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("/")).place(x=150, y=100)
Button(root, text="%", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("%")).place(x=290, y=100)
Button(root, text="*", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("*")).place(x=430, y=100)

Button(root, text="7", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("7")).place(x=10, y=200)
Button(root, text="8", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("8")).place(x=150, y=200)
Button(root, text="9", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("9")).place(x=290, y=200)
Button(root, text="-", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("-")).place(x=430, y=200)

Button(root, text="4", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("4")).place(x=10, y=300)
Button(root, text="5", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("5")).place(x=150, y=300)
Button(root, text="6", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("6")).place(x=290, y=300)
Button(root, text="+", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("+")).place(x=430, y=300)

Button(root, text="1", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("1")).place(x=10, y=400)
Button(root, text="2", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("2")).place(x=150, y=400)
Button(root, text="3", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("3")).place(x=290, y=400)
Button(root, text="0", width=11, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show("0")).place(x=10, y=500)

Button(root, text=".", width=5, height=1, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#2a2d36", command=lambda: show(".")).place(x=290, y=500)
Button(root, text="=", width=5, height=3, font=("Arial", 30,"bold"), bd=1, fg="#fff", bg="#fe9037", command=calculate).place(x=430, y=400)

# Start the main application loop
root.mainloop()