# 🔐 PDF Protector App (Python + Tkinter GUI)

A beginner-friendly and visually styled Python GUI app that allows you to **add password protection to PDF files** using `PyPDF2`. Built using `tkinter`, this app features a clean layout, drag-and-drop file selection, and a one-click encryption process to secure your documents easily.

---

## 📌 Features

- 📁 **Select PDF File**: Browse and select any `.pdf` file from your system.
- 🔑 **Set Password**: Enter a user password to protect the PDF from unauthorized access.
- 💾 **Save Protected File**: Save the encrypted version of the file to your chosen location.
- 🎨 **Custom GUI**: Clean and fixed layout with image-based buttons and labels for better user experience.

---

## 📂 Project Structure

`34_PDF_Protector_App/`  
├── assets/  
│   ├── icon.png  
│   ├── top image.png  
│   ├── button image.png  
│   ├── screenshot.png  
│   └── button.png  
├── main.py  
├── requirements.txt  
└── README.md  

---

## ▶️ How to Run

1. **Install Python 3.7 or higher**
2. **Install dependencies:**

```bash
pip install -r requirements.txt


```
3. **Run the application:**

```bash
python main.py
```

---

## ⚙️ How It Works

1. GUI Setup
    - Uses `tkinter` to build a windowed interface with labels, buttons, and entry widgets.
2. File Selection
    - Uses `filedialog` to select an existing `.pdf` file.
3. Encryption
    - `PyPDF2` reads the selected file, and each page is added to a new `PdfWriter` object.
    - The password is applied using `encrypt()`.
4. File Saving
    - Asks the user where to save the newly encrypted file and saves it securely.

---

## 📦 Dependencies

- `PyPDF2` – For reading and writing encrypted PDF files
- `tkinter` – Python’s standard GUI toolkit

---

## 📸 Screenshot

![PDF Protector Tool](assets/screenshot.png)

---

## 📚 What You Learn

- GUI programming using `tkinter`
- File dialogs and user input handling
- Basic PDF manipulation with `PyPDF2`
- Password protection for PDFs
- Real-world GUI project structure

---

## 👤 Author

Made with ❤️ by **Shahid Hasan**  
Feel free to connect and collaborate!

---

## 📄 License

This project is licensed under the MIT License – free to use, modify, and distribute.