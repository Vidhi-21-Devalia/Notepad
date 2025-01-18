
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, colorchooser
from tkinter.scrolledtext import ScrolledText
import os
import time
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from docx import Document
import win32gui
import win32con
import subprocess

class EnhancedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Notepad")
        self.root.geometry("1200x800")
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create Main Toolbar
        self.create_toolbar()
        
        # Create Format Toolbar
        self.create_format_toolbar()
        
        # Create Main Menu
        self.create_menu()
        
        # Create Text Area
        self.create_text_area()
        
        # Auto-save settings
        self.auto_save_interval = 60
        self.last_autosave = time.time()
        self.current_file = None
        self.check_autosave()

    def create_toolbar(self):
        # Main Toolbar
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)

        # Font Family
        self.font_families = list(font.families())
        self.font_family = ttk.Combobox(self.toolbar, values=self.font_families, width=20)
        self.font_family.set("Arial")
        self.font_family.pack(side=tk.LEFT, padx=5)
        self.font_family.bind('<<ComboboxSelected>>', self.apply_font)

        # Font Size
        self.font_sizes = list(range(8, 73, 2))
        self.font_size = ttk.Combobox(self.toolbar, values=self.font_sizes, width=5)
        self.font_size.set("12")
        self.font_size.pack(side=tk.LEFT, padx=5)
        self.font_size.bind('<<ComboboxSelected>>', self.apply_font)

        # Style Buttons
        self.create_style_buttons()

    def create_format_toolbar(self):
        self.format_bar = ttk.Frame(self.root)
        self.format_bar.pack(fill=tk.X, padx=5, pady=2)

        # Text Color Button
        self.text_color_btn = ttk.Button(self.format_bar, text="Text Color", command=self.choose_text_color)
        self.text_color_btn.pack(side=tk.LEFT, padx=5)

        # Background Color Button
        self.bg_color_btn = ttk.Button(self.format_bar, text="Background", command=self.choose_bg_color)
        self.bg_color_btn.pack(side=tk.LEFT, padx=5)

        # Border Styles
        self.border_styles = ['flat', 'solid', 'raised', 'sunken', 'ridge', 'groove']
        self.border_var = ttk.Combobox(self.format_bar, values=self.border_styles, width=10)
        self.border_var.set("Border Style")
        self.border_var.pack(side=tk.LEFT, padx=5)
        self.border_var.bind('<<ComboboxSelected>>', self.change_border)

        # Alignment Buttons
        self.create_alignment_buttons()

    def create_style_buttons(self):
        # Bold Button
        self.bold_btn = ttk.Button(self.toolbar, text="B", width=3, command=self.toggle_bold)
        self.bold_btn.pack(side=tk.LEFT, padx=2)

        # Italic Button
        self.italic_btn = ttk.Button(self.toolbar, text="I", width=3, command=self.toggle_italic)
        self.italic_btn.pack(side=tk.LEFT, padx=2)

        # Underline Button
        self.underline_btn = ttk.Button(self.toolbar, text="U", width=3, command=self.toggle_underline)
        self.underline_btn.pack(side=tk.LEFT, padx=2)

    def create_alignment_buttons(self):
        # Left Align
        self.align_left = ttk.Button(self.format_bar, text="⫷", command=lambda: self.align_text('left'))
        self.align_left.pack(side=tk.LEFT, padx=2)

        # Center Align
        self.align_center = ttk.Button(self.format_bar, text="⫼", command=lambda: self.align_text('center'))
        self.align_center.pack(side=tk.LEFT, padx=2)

        # Right Align
        self.align_right = ttk.Button(self.format_bar, text="⫸", command=lambda: self.align_text('right'))
        self.align_right.pack(side=tk.LEFT, padx=2)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)

        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=lambda: self.text_area.event_generate("<<Undo>>"))
        self.edit_menu.add_command(label="Redo", command=lambda: self.text_area.event_generate("<<Redo>>"))

        # Export Menu
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)
        self.export_menu.add_command(label="Export as PDF", command=self.export_pdf)
        self.export_menu.add_command(label="Export as DOC", command=self.export_doc)
        self.export_menu.add_command(label="Export as PNG", command=self.export_png)
        self.export_menu.add_command(label="Export as JPEG", command=self.export_jpeg)

    def create_text_area(self):
        self.text_area = ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12), undo=True)
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Status Bar
        self.status_bar = ttk.Label(self.root, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def check_autosave(self):
        current_time = time.time()
        if current_time - self.last_autosave >= self.auto_save_interval:
            self.auto_save()
            self.last_autosave = current_time
        self.root.after(1000, self.check_autosave)

    def auto_save(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.status_bar.config(text=f"Auto-saved at {time.strftime('%H:%M:%S')}")

    def new_file(self):
        if messagebox.askyesno("Confirm", "Create new file? Unsaved changes will be lost."):
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.status_bar.config(text="New File")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, file.read())
            self.status_bar.config(text=f"Opened: {file_path}")

    def save_file(self):
        if not self.current_file:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                self.current_file = file_path
        
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.status_bar.config(text=f"Saved to {self.current_file}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            text = self.text_area.get(1.0, tk.END)
            pdf.multi_cell(0, 10, txt=text)
            pdf.output(file_path)
            self.status_bar.config(text=f"Exported to PDF: {file_path}")

    def export_doc(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx")])
        if file_path:
            doc = Document()
            doc.add_paragraph(self.text_area.get(1.0, tk.END))
            doc.save(file_path)
            self.status_bar.config(text=f"Exported to DOCX: {file_path}")

    def export_png(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")])
        if file_path:
            text = self.text_area.get(1.0, tk.END)
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 14)
            draw.text((10, 10), text, font=font, fill='black')
            img.save(file_path)
            self.status_bar.config(text=f"Exported to PNG: {file_path}")

    def export_jpeg(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG Files", "*.jpg")])
        if file_path:
            text = self.text_area.get(1.0, tk.END)
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 14)
            draw.text((10, 10), text, font=font, fill='black')
            img.save(file_path, 'JPEG')
            self.status_bar.config(text=f"Exported to JPEG: {file_path}")

    def exit_app(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            if self.current_file:
                self.save_file()
            self.root.destroy()

    def apply_font(self, event=None):
        font_family = self.font_family.get()
        font_size = int(self.font_size.get())
        self.text_area.configure(font=(font_family, font_size))

    def toggle_bold(self):
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "bold" in current_tags:
                self.text_area.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("bold", "sel.first", "sel.last")
                self.text_area.tag_configure("bold", font=(self.font_family.get(), int(self.font_size.get()), "bold"))
        except tk.TclError:
            pass

    def toggle_italic(self):
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "italic" in current_tags:
                self.text_area.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("italic", "sel.first", "sel.last")
                self.text_area.tag_configure("italic", font=(self.font_family.get(), int(self.font_size.get()), "italic"))
        except tk.TclError:
            pass

    def toggle_underline(self):
        try:
            current_tags = self.text_area.tag_names("sel.first")
            if "underline" in current_tags:
                self.text_area.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("underline", "sel.first", "sel.last")
                self.text_area.tag_configure("underline", underline=True)
        except tk.TclError:
            pass

    def choose_text_color(self):
        try:
            color = colorchooser.askcolor(title="Choose Text Color")[1]
            if color:
                self.text_area.tag_add("colored", "sel.first", "sel.last")
                self.text_area.tag_configure("colored", foreground=color)
        except tk.TclError:
            pass

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.text_area.configure(bg=color)

    def change_font_family(self, event=None):
        font_family = self.font_family.get()
        self.text_area.configure(font=(font_family, int(self.font_size.get())))
        self.text_area.tag_configure("bold", font=(font_family, int(self.font_size.get()), "bold"))
        self.text_area.tag_configure("italic", font=(font_family, int(self.font_size.get()), "italic"))
        self.text_area.tag_configure("underline", underline=True)
        self.text_area.tag_configure("colored", foreground=self.text_color.get())
     
     
    def change_border(self, event=None):
        border_style = self.border_var.get()
        self.text_area.configure(relief=border_style)

    def align_text(self, alignment):
        try:
            self.text_area.tag_add(alignment, "sel.first", "sel.last")
            self.text_area.tag_configure(alignment, justify=alignment)
        except tk.TclError:
            pass

    def open_file_manager(self):
        if os.name == 'nt':  # Windows
            subprocess.Popen('explorer')
        else:  # Linux/Mac
            subprocess.Popen(['xdg-open', os.path.expanduser('~')])

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedNotepad(root)
    root.mainloop()


