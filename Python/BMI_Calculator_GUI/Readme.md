# 🏋️‍♂️ BMI Calculator Pro

A professional-grade Body Mass Index calculator with dual CLI/GUI interfaces, featuring a modern dark theme, real-time visualizations, and comprehensive unit support.

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![GUI](https://img.shields.io/badge/GUI-tkinter-orange)
![Theme](https://img.shields.io/badge/Theme-Dark%20Mode-purple)

## ✨ Features

### 🎯 Dual Interface Architecture
- **CLI Mode**: Scriptable command-line for automation and quick calculations
- **GUI Mode**: Modern graphical interface with smooth animations and visual feedback

### 🌍 Comprehensive Unit Support
- **Weight**: Kilograms (kg) and Pounds (lbs) with real-time conversion
- **Height**: Centimeters (cm) and Feet/Inches (ft/in) with precise calculations

### 🎨 Premium Visual Experience
- **Dark Theme**: Professional Sun Valley ttk theme
- **Animated Scale**: Smooth BMI marker transitions with color-coded categories
- **Real-time Feedback**: Visual flashing effects and instant classification
- **Responsive Design**: Adaptive layout for various screen sizes

### 📊 Medical-Grade Calculations
- WHO-standard BMI classification
- 8 precise health categories with color coding
- Comprehensive input validation
- Reasonable range checking

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/bmi-calculator-pro.git
cd bmi-calculator-pro
```
# Install dependencies
```
pip install -r requirements.txt
```
Dependencies
```
sv-ttk>=2.0
```
💻 Usage
GUI Mode (Recommended)
bash

python bmi_calculator.py

CLI Mode

Metric Units:
bash

python bmi_calculator.py --units metric --weight 70 --height 175

Imperial Units:
bash

python bmi_calculator.py --units imperial --weight 154 --height 68

🖥️ GUI Overview
Input Section

    Weight: Toggle between kg/lbs with dedicated buttons

    Height: Switch between cm or ft/in input fields

    Real-time Validation: Intelligent input checking with helpful error messages

Results Display

    BMI Value: Large, color-coded result display

    Health Category: Immediate classification with color coordination

    Visual Scale: Animated marker positioning across 8 BMI ranges

Interactive Elements

    Keyboard Support: Enter key for quick calculations

    Unit Toggles: Instant switching between measurement systems

    Smooth Animations: Professional transitions and visual feedback

🏗️ Architecture
Core Modules
python

# BMI Calculation Engine
- calculate_bmi()          # Pure calculation logic
- classify_bmi()           # WHO classification with colors
- unit_conversion()        # Precise unit transformations

# CLI Interface  
- argparse integration     # Professional command-line interface
- formatted output         # Clean, readable results

# GUI Framework
- tkinter with sv_ttk      # Modern theming system
- custom widgets           # Enhanced user experience
- animation system         # Smooth visual transitions

Code Quality

    Type hints throughout

    Comprehensive error handling

    Modular, maintainable structure

    Professional documentation

📊 BMI Classification System
Category	BMI Range	Color	Health Risk
Severe Thinness	< 16	#3498db	High
Moderate Thinness	16 - 17	#5dade2	Moderate
Mild Thinness	17 - 18.5	#85c1e9	Mild
Normal Range	18.5 - 25	#2ecc71	Low
Overweight	25 - 30	#f39c12	Increased
Obese Class I	30 - 35	#e67e22	High
Obese Class II	35 - 40	#d35400	Very High
Obese Class III	≥ 40	#c0392b	Extremely High
🎨 Customization
Theme Modification
python

# Switch to light theme
sv_ttk.set_theme("light")

# Custom color scheme
def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight", "#your-custom-color"

Adding Features

The modular architecture makes it easy to extend:

    New unit systems

    Additional health metrics

    Custom themes and styling

    Data export capabilities

🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:

    Bug reports and feature requests

    Code style and pull request process

    Development environment setup

📝 License

MIT License - feel free to use this project for personal or commercial purposes.
⚠️ Medical Disclaimer

This software provides general health information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any medical questions.
<div align="center">

Built with ❤️ using Python, tkinter, and modern UI principles

Precision meets design in health calculation
</div> ```
