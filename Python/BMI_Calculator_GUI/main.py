#!/usr/bin/env python3
"""BMI Calculator (CLI + GUI in one file) - Dark Theme with Enhanced Units"""

import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk  # Requires sv_ttk package: pip install sv_ttk


# ---------------- Core Logic ----------------
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculates BMI from weight in kg and height in meters."""
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be positive numbers")
    return round(weight_kg / (height_m ** 2), 2)


def kg_to_lbs(kg: float) -> float:
    """Converts kilograms to pounds."""
    return kg * 2.20462


def lbs_to_kg(lbs: float) -> float:
    """Converts pounds to kilograms."""
    return lbs * 0.453592


def cm_to_ft_in(cm: float) -> tuple[float, float]:
    """Converts centimeters to feet and inches."""
    inches = cm * 0.393701
    return (inches // 12, inches % 12)


def ft_in_to_cm(ft: float, inches: float) -> float:
    """Converts feet and inches to centimeters."""
    return (ft * 12 + inches) * 2.54


def bmi_from_metric(weight_kg: float, height_cm: float) -> float:
    """Calculates BMI from metric units."""
    return calculate_bmi(weight_kg, height_cm / 100.0)


def bmi_from_imperial(weight_lbs: float, height_in: float) -> float:
    """Calculates BMI from imperial units."""
    kg = lbs_to_kg(weight_lbs)
    m = height_in * 0.0254
    return calculate_bmi(kg, m)


def classify_bmi(bmi: float) -> tuple[str, str]:
    """Classifies BMI and returns a category and corresponding color."""
    if bmi < 16:
        return ("Severe Thinness", "#3498db")
    elif bmi < 17:
        return ("Moderate Thinness", "#5dade2")
    elif bmi < 18.5:
        return ("Mild Thinness", "#85c1e9")
    elif bmi < 25:
        return ("Normal", "#2ecc71")
    elif bmi < 30:
        return ("Overweight", "#f39c12")
    elif bmi < 35:
        return ("Obese Class I", "#e67e22")
    elif bmi < 40:
        return ("Obese Class II", "#d35400")
    else:
        return ("Obese Class III", "#c0392b")


# ---------------- CLI ----------------
def run_cli():
    """Runs the CLI version of the BMI calculator."""
    parser = argparse.ArgumentParser(description="BMI Calculator")
    parser.add_argument("--units", choices=["metric", "imperial"], default="metric")
    parser.add_argument("--weight", type=float, required=True, help="Weight (kg or lbs)")
    parser.add_argument("--height", type=float, required=True, help="Height (cm or in)")
    args = parser.parse_args()

    if args.units == "metric":
        bmi = bmi_from_metric(args.weight, args.height)
    else:
        bmi = bmi_from_imperial(args.weight, args.height)

    category, _ = classify_bmi(bmi)
    print(f"BMI: {bmi:.2f}")
    print(f"Category: {category}")


# ---------------- GUI ----------------
class BMIApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(20, 10))
        self.parent = parent
        parent.title("BMI Calculator")
        parent.geometry("450x550")
        parent.minsize(450, 600)
        
        # Add logo icon to window
        try:
            icon = tk.PhotoImage(file="assets/logo.png")
            parent.iconphoto(False, icon)
        except (tk.TclError, FileNotFoundError):
            # Logo file not found, continue without icon
            pass

        # Force dark theme
        sv_ttk.set_theme("dark")
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Result.TLabel", font=("Segoe UI", 12))

        # Variables
        self.weight_unit = tk.StringVar(value="kg")
        self.height_unit = tk.StringVar(value="cm")
        self.category = tk.StringVar()
        self.bmi_value = tk.DoubleVar()
        self.current_marker_position = 0.0  # Track marker position

        # Build UI
        self._create_widgets()
        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Set initial focus
        self.weight_entry.focus()

    def _create_widgets(self):
        # Allow the main frame column to expand horizontally
        self.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        ttk.Label(header_frame, text="BMI Calculator", style="Title.TLabel").pack(side="left")

        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Weight input
        weight_frame = ttk.Frame(input_frame)
        weight_frame.pack(fill="x", pady=10)

        ttk.Label(weight_frame, text="Weight:").pack(side="left", padx=(0, 5))

        # Weight unit buttons
        weight_btn_frame = ttk.Frame(weight_frame)
        weight_btn_frame.pack(side="left")

        self.kg_btn = ttk.Button(
            weight_btn_frame, text="kg", width=3,
            command=lambda: self._set_weight_unit("kg")
        )
        self.kg_btn.pack(side="left")

        self.lbs_btn = ttk.Button(
            weight_btn_frame, text="lbs", width=3,
            command=lambda: self._set_weight_unit("lbs")
        )
        self.lbs_btn.pack(side="left", padx=(2, 5))

        self.weight_entry = ttk.Entry(weight_frame, width=10)
        self.weight_entry.pack(side="left")

        # Height input
        height_frame = ttk.Frame(input_frame)
        height_frame.pack(fill="x", pady=10)

        ttk.Label(height_frame, text="Height:").pack(side="left", padx=(0, 5))

        # Height unit buttons
        height_btn_frame = ttk.Frame(height_frame)
        height_btn_frame.pack(side="left")

        self.cm_btn = ttk.Button(
            height_btn_frame, text="cm", width=3,
            command=lambda: self._set_height_unit("cm")
        )
        self.cm_btn.pack(side="left")

        self.ft_btn = ttk.Button(
            height_btn_frame, text="ft", width=3,
            command=lambda: self._set_height_unit("ft")
        )
        self.ft_btn.pack(side="left", padx=(2, 5))

        # Metric height input
        self.height_cm_frame = ttk.Frame(height_frame)
        self.height_cm_entry = ttk.Entry(self.height_cm_frame, width=10)
        self.height_cm_entry.pack(side="left")

        # Imperial height input (hidden by default)
        self.height_ft_frame = ttk.Frame(height_frame)
        self.height_ft_entry = ttk.Entry(self.height_ft_frame, width=3)
        self.height_ft_entry.pack(side="left")
        ttk.Label(self.height_ft_frame, text="ft").pack(side="left", padx=(5, 0))
        self.height_in_entry = ttk.Entry(self.height_ft_frame, width=3)
        self.height_in_entry.pack(side="left", padx=(5, 0))
        ttk.Label(self.height_ft_frame, text="in").pack(side="left", padx=(5, 0))

        # Calculate button
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, pady=20)
        ttk.Button(
            btn_frame, text="Calculate BMI", style="Accent.TButton",
            command=self.calculate
        ).pack(fill="x")

        # Result display
        result_frame = ttk.Frame(self)
        result_frame.grid(row=3, column=0, sticky="nsew", pady=10)

        # Frame for the result number's colored background
        self.result_bg_frame = ttk.Frame(result_frame)
        self.result_bg_frame.pack(pady=5)

        # Use tk.Label for direct background color control
        self.result_label = tk.Label(
            self.result_bg_frame,
            text="Enter your details",
            font=("Segoe UI", 12, "bold"),
            foreground="white",
            background="#2b2b2b",  # Default dark background
            padx=10, pady=5
        )
        self.result_label.pack(side="left")

        self.category_label = ttk.Label(
            result_frame, textvariable=self.category,
            font=("Segoe UI", 12)
        )
        self.category_label.pack(pady=5)

        # BMI scale visualization
        self.scale_frame = ttk.Frame(self)
        self.scale_frame.grid(row=4, column=0, sticky="nsew", pady=20)
        self.scale_frame.grid_columnconfigure(tuple(range(8)), weight=1)  # Give all columns equal weight

        # Create colored scale segments
        segments = [
            (0, 16, "#3498db"),     # Severe Thinness
            (16, 17, "#5dade2"),    # Moderate Thinness
            (17, 18.5, "#85c1e9"),  # Mild Thinness
            (18.5, 25, "#2ecc71"),  # Normal
            (25, 30, "#f39c12"),    # Overweight
            (30, 35, "#e67e22"),    # Obese I
            (35, 40, "#d35400"),    # Obese II
            (40, 50, "#c0392b")     # Obese III
        ]

        for i, (start, end, color) in enumerate(segments):
            segment = tk.Frame(self.scale_frame, bg=color, height=20)
            segment.grid(row=0, column=i, sticky="nsew", padx=1)

            # Add labels for key points
            if start in [0, 18.5, 25, 30, 40]:
                label = ttk.Label(self.scale_frame, text=str(start))
                label.grid(row=1, column=i, sticky="w")

        # BMI indicator marker
        self.marker = tk.Frame(self.scale_frame, bg="white", width=2, height=30)
        self.marker.grid(row=0, column=0, sticky="s")
        self.marker.tkraise()

        # Footer
        footer_frame = ttk.Frame(self)
        footer_frame.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        footer_label = ttk.Label(footer_frame, text="© 2025 BMI Calculator", font=("Segoe UI", 8))
        footer_label.pack(side="right")

        # Bind Enter key to calculate
        self.parent.bind("<Return>", lambda e: self.calculate())

        # Initialize units
        self._set_weight_unit("kg")
        self._set_height_unit("cm")

    def _set_weight_unit(self, unit):
        """Set weight unit and update UI"""
        self.weight_unit.set(unit)

        # Update button states
        if unit == "kg":
            self.kg_btn.state(["pressed", "disabled"])
            self.lbs_btn.state(["!pressed", "!disabled"])
            self.weight_entry.config(state="normal")
        else:
            self.kg_btn.state(["!pressed", "!disabled"])
            self.lbs_btn.state(["pressed", "disabled"])
            self.weight_entry.config(state="normal")

    def _set_height_unit(self, unit):
        """Set height unit and update UI"""
        self.height_unit.set(unit)

        # Update button states
        if unit == "cm":
            self.cm_btn.state(["pressed", "disabled"])
            self.ft_btn.state(["!pressed", "!disabled"])
        else:
            self.cm_btn.state(["!pressed", "!disabled"])
            self.ft_btn.state(["pressed", "disabled"])

        # Update UI visibility
        if unit == "cm":
            self.height_cm_frame.pack(side="left")
            self.height_ft_frame.pack_forget()
        else:
            self.height_cm_frame.pack_forget()
            self.height_ft_frame.pack(side="left")

    def _safe_float_convert(self, value_str: str, field_name: str) -> float:
        """Safely converts string to float with better error messages."""
        if not value_str or not value_str.strip():
            raise ValueError(f"{field_name} cannot be empty")
        
        # Clean the input - remove extra whitespace
        value_str = value_str.strip()
        
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Please enter a valid number for {field_name}")

    def calculate(self):
        try:
            # Get and convert weight
            weight_str = self.weight_entry.get()
            if self.weight_unit.get() == "kg":
                weight_kg = self._safe_float_convert(weight_str, "weight")
            else:
                weight_lbs = self._safe_float_convert(weight_str, "weight")
                weight_kg = lbs_to_kg(weight_lbs)

            # Get and convert height
            if self.height_unit.get() == "cm":
                height_str = self.height_cm_entry.get()
                height_cm = self._safe_float_convert(height_str, "height")
            else:
                height_ft_str = self.height_ft_entry.get().strip()
                height_in_str = self.height_in_entry.get().strip()
                
                # Handle empty imperial height inputs more gracefully
                if not height_ft_str and not height_in_str:
                    raise ValueError("Please enter height in feet and/or inches")
                
                height_ft = self._safe_float_convert(height_ft_str, "feet") if height_ft_str else 0
                height_in = self._safe_float_convert(height_in_str, "inches") if height_in_str else 0
                
                if height_ft == 0 and height_in == 0:
                    raise ValueError("Height cannot be zero")
                
                height_cm = ft_in_to_cm(height_ft, height_in)

            # Validate positive values
            if weight_kg <= 0:
                raise ValueError("Weight must be greater than zero")
            if height_cm <= 0:
                raise ValueError("Height must be greater than zero")

            # Additional reasonable range checks
            if weight_kg > 1000:  # 1000kg = 2200lbs
                raise ValueError("Weight seems unreasonably high")
            if height_cm > 300:  # 3 meters = ~10 feet
                raise ValueError("Height seems unreasonably high")
            if height_cm < 30:  # 30cm = ~1 foot
                raise ValueError("Height seems unreasonably low")

            bmi = bmi_from_metric(weight_kg, height_cm)
            category, color = classify_bmi(bmi)

            # Update result label with BMI value and matching background color
            self.result_label.config(text=f"BMI: {bmi:.1f}", background=color)
            self.category.set(category)
            
            # Create a unique style for this specific color
            style_name = f"Category{bmi:.1f}.TLabel"
            self.style.configure(style_name, foreground=color)
            self.category_label.config(style=style_name)

            # Update the marker position and flash the result
            self._update_marker(bmi)
            self._flash_result(color)

        except ValueError as e:
            # Handle all value-related errors with specific messages
            messagebox.showerror("Input Error", str(e))
            self.result_label.config(text="Invalid input", background="#2b2b2b")
            self.category.set("")
            # Reset to default style
            self.category_label.config(style="TLabel")
            self._update_marker(0)
        except Exception as e:
            # Handle any other unexpected errors
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.result_label.config(text="Error", background="#2b2b2b")
            self.category.set("")
            # Reset to default style
            self.category_label.config(style="TLabel")
            self._update_marker(0)

    def _update_marker(self, new_bmi):
        """Smoothly moves the BMI marker to the correct position based on BMI ranges."""
        if new_bmi == 0:
            target_position = 0
        else:
            # Calculate position based on exact BMI ranges that match color segments
            if new_bmi < 16:
                # Severe Thinness - segment 0
                target_position = 0 + min(new_bmi / 16, 1) * (1/8)
            elif new_bmi < 17:
                # Moderate Thinness - segment 1
                target_position = 1/8 + ((new_bmi - 16) / 1) * (1/8)
            elif new_bmi < 18.5:
                # Mild Thinness - segment 2
                target_position = 2/8 + ((new_bmi - 17) / 1.5) * (1/8)
            elif new_bmi < 25:
                # Normal - segment 3 (GREEN) - This is where BMI 24.9 should go
                target_position = 3/8 + ((new_bmi - 18.5) / 6.5) * (1/8)
            elif new_bmi < 30:
                # Overweight - segment 4 (YELLOW/ORANGE)
                target_position = 4/8 + ((new_bmi - 25) / 5) * (1/8)
            elif new_bmi < 35:
                # Obese Class I - segment 5
                target_position = 5/8 + ((new_bmi - 30) / 5) * (1/8)
            elif new_bmi < 40:
                # Obese Class II - segment 6
                target_position = 6/8 + ((new_bmi - 35) / 5) * (1/8)
            else:
                # Obese Class III - segment 7
                target_position = 7/8 + min((new_bmi - 40) / 10, 1) * (1/8)
        
        total_steps = 20
        step_duration = 10

        def animate_step(step_count):
            if step_count > total_steps:
                return

            # Calculate current position during animation
            current_position = self.current_marker_position + (target_position - self.current_marker_position) * (step_count / total_steps)
            self.update_idletasks()
            scale_frame_width = self.scale_frame.winfo_width()
            pos = current_position * scale_frame_width
            self.marker.place(x=pos)

            self.after(step_duration, animate_step, step_count + 1)

        animate_step(1)
        self.current_marker_position = target_position
        self.bmi_value.set(new_bmi)

    def _flash_result(self, color):
        """Flashes the result label's background color."""
        def flash(count):
            if count % 2 == 0:
                # Flash with the BMI category color
                self.result_label.config(background=color)
            else:
                # Return to default dark background
                self.result_label.config(background="#2b2b2b")
            if count > 0:
                self.after(150, flash, count - 1)
            else:
                # Keep the final color after flashing
                self.result_label.config(background=color)

        flash(4)


def run_gui():
    """Runs the GUI version of the BMI calculator."""
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()


# ---------------- Entry Point ----------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_gui()