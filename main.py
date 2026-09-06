from app import vault, crypto
import customtkinter as ctk
from tkinter import messagebox, filedialog
import pyperclip
import json


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 18, "bold")
FONT_BODY = ("Segoe UI", 16)
FONT_BODY_BOLD = ("Segoe UI", 16, "bold")
FONT_SMALL = ("Segoe UI", 12)
FONT_MONO = ("Consolas", 16)
FONT_ENTRY = ("Segoe UI", 16)

class PasswordVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Password Vault")
        self.geometry("600x450")
        self.minsize(500, 250)

        self.current_screen = None
        self.password_visible = {}   # словарь: индекс записи -> True (показан) / False (скрыт)
        self.theme_mode = "system"
        self.color_theme = "blue"
        self.master_password = None
        self.vault_file = None
        self.passwords = []          # список словарей
        self.current_dialog = None   # ссылка на активный диалог инициализации

        self.show_login_screen()

    def clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.current_screen.pack(fill="both", expand=True, padx=20, pady=20)

    def apply_theme(self, mode: str):
        ctk.set_appearance_mode(mode)
        self.theme_mode = mode
        self.update_idletasks()

    def apply_color_theme(self, color: str):
        ctk.set_default_color_theme(color)
        self.color_theme = color
        if self.current_dialog is not None:
            self.current_dialog.destroy()
            self.current_dialog = None
        self.show_login_screen()

    def copy_to_clipboard(self, text):
        try:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")

    # ---------- РАБОТА С ХРАНИЛИЩЕМ ----------
    def load_vault(self) -> bool:
        try:
            vault_data = vault.read(self.vault_file)
        except Exception:
            return False

        if vault_data is None:
            self.passwords = []
            return True
        try:
            key = crypto.get_key(self.master_password.encode(), vault_data["salt"])
            plaintext = crypto.decrypt(key, vault_data["token"]).decode()
            self.passwords = json.loads(plaintext)
            if not isinstance(self.passwords, list):
                self.passwords = []
            return True
        except Exception:
            return False

    def save_vault(self):
        salt = crypto.get_random_salt()
        key = crypto.get_key(self.master_password.encode(), salt)
        plaintext = json.dumps(self.passwords).encode()
        token = crypto.encrypt(key, plaintext)
        vault.write(salt, token, self.vault_file)

    # ---------- ИНИЦИАЛИЗАЦИЯ ХРАНИЛИЩА ----------
    def initialize_vault(self) -> bool:
        dialog = ctk.CTkToplevel(self)
        self.current_dialog = dialog
        dialog.title("Vault Setup")
        dialog.geometry("550x300")
        dialog.minsize(500, 300)
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dialog, text="Welcome to Password Vault", font=FONT_SUBTITLE).grid(
            row=0, column=0, pady=(20, 10)
        )
        ctk.CTkLabel(dialog, text="Choose an existing vault or create a new one to get started.",
                     font=FONT_BODY).grid(row=1, column=0, pady=(0, 20))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)

        select_btn = ctk.CTkButton(
            btn_frame, text="Select Existing Vault", width=180, height=45,
            font=FONT_BODY, command=lambda: self._handle_select_existing(dialog)
        )
        select_btn.grid(row=0, column=0, padx=10)

        create_btn = ctk.CTkButton(
            btn_frame, text="Create New Vault", width=180, height=45,
            font=FONT_BODY, command=lambda: self._handle_create_new(dialog)
        )
        create_btn.grid(row=0, column=1, padx=10)

        settings_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        settings_frame.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        settings_frame.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(settings_frame, text="Appearance:", font=FONT_BODY).grid(
            row=0, column=0, sticky="w", padx=5)
        theme_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["dark", "light", "system"],
            command=self.apply_theme,
            width=120,
            font=FONT_BODY,
            dropdown_font=FONT_BODY
        )
        theme_menu.set(self.theme_mode)
        theme_menu.grid(row=0, column=1, sticky="e", padx=5)

        ctk.CTkLabel(settings_frame, text="Color Theme:", font=FONT_BODY).grid(
            row=1, column=0, sticky="w", padx=5, pady=(10,0))
        color_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["blue", "green", "gold"],
            command=self.apply_color_theme,
            width=120,
            font=FONT_BODY,
            dropdown_font=FONT_BODY
        )
        color_menu.set(self.color_theme)
        color_menu.grid(row=1, column=1, sticky="e", padx=5, pady=(10,0))

        self.wait_window(dialog)
        self.current_dialog = None
        return self.vault_file is not None and self.master_password is not None

    def _handle_select_existing(self, parent_dialog):
        file_path = filedialog.askopenfilename(
            title="Select Vault File",
            filetypes=[("Vault files", "*.passvault"), ("All files", "*.*")]
        )
        if not file_path:
            return

        pwd_dialog = ctk.CTkToplevel(self)
        pwd_dialog.title("Enter Master Password")
        pwd_dialog.geometry("400x200")
        pwd_dialog.minsize(400, 200)
        pwd_dialog.transient(self)
        pwd_dialog.grab_set()
        pwd_dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(pwd_dialog, text=f"File: {file_path.split('/')[-1]}",
                     font=FONT_BODY).grid(row=0, column=0, padx=20, pady=(20,5))
        ctk.CTkLabel(pwd_dialog, text="Master Password:", font=FONT_BODY).grid(
            row=1, column=0, sticky="w", padx=20, pady=(10,0))
        pwd_entry = ctk.CTkEntry(pwd_dialog, show="•", width=300, height=35, font=FONT_BODY)
        pwd_entry.grid(row=2, column=0, padx=20, pady=5)
        pwd_entry.focus()

        def ok():
            password = pwd_entry.get()
            if not password:
                messagebox.showerror("Error", "Password cannot be empty!", parent=pwd_dialog)
                return
            self.master_password = password
            self.vault_file = file_path
            if self.load_vault():
                pwd_dialog.destroy()
                parent_dialog.destroy()
            else:
                messagebox.showerror("Error", "Invalid password or corrupted vault!", parent=pwd_dialog)
                self.master_password = None
                self.vault_file = None

        ok_btn = ctk.CTkButton(pwd_dialog, text="OK", command=ok, width=100, height=30, font=FONT_BODY)
        ok_btn.grid(row=3, column=0, pady=20)

    def _handle_create_new(self, parent_dialog):
        create_dialog = ctk.CTkToplevel(self)
        create_dialog.title("Create New Vault")
        create_dialog.geometry("450x300")
        create_dialog.minsize(400, 300)
        create_dialog.transient(self)
        create_dialog.grab_set()
        create_dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(create_dialog, text="Set Master Password", font=FONT_SUBTITLE).grid(
            row=0, column=0, pady=(20,10))
        ctk.CTkLabel(create_dialog, text="Password:", font=FONT_BODY).grid(
            row=1, column=0, sticky="w", padx=20, pady=(10,0))
        pwd_entry = ctk.CTkEntry(create_dialog, show="•", width=300, height=35, font=FONT_BODY)
        pwd_entry.grid(row=2, column=0, padx=20, pady=5)

        ctk.CTkLabel(create_dialog, text="Confirm Password:", font=FONT_BODY).grid(
            row=3, column=0, sticky="w", padx=20, pady=(10,0))
        confirm_entry = ctk.CTkEntry(create_dialog, show="•", width=300, height=35, font=FONT_BODY)
        confirm_entry.grid(row=4, column=0, padx=20, pady=5)

        def create():
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()
            if not pwd:
                messagebox.showerror("Error", "Password cannot be empty!", parent=create_dialog)
                return
            if pwd != confirm:
                messagebox.showerror("Error", "Passwords do not match!", parent=create_dialog)
                return

            file_path = filedialog.asksaveasfilename(
                title="Save Vault As",
                defaultextension=".passvault",
                filetypes=[("Vault files", "*.passvault"), ("All files", "*.*")]
            )
            if not file_path:
                return

            self.master_password = pwd
            self.vault_file = file_path
            self.passwords = []
            try:
                self.save_vault()
                create_dialog.destroy()
                parent_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create vault: {e}", parent=create_dialog)
                self.master_password = None
                self.vault_file = None

        create_btn = ctk.CTkButton(create_dialog, text="Create", command=create,
                                   width=120, height=35, font=FONT_BODY)
        create_btn.grid(row=5, column=0, pady=20)

    # ---------- ЭКРАН ВХОДА ----------
    def show_login_screen(self):
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme(self.color_theme)

        self.clear_screen()
        if self.vault_file is None:
            if not self.initialize_vault():
                self.current_screen.destroy()
                self.current_screen = ctk.CTkFrame(self, fg_color="transparent")
                self.current_screen.pack(fill="both", expand=True, padx=20, pady=20)
                ctk.CTkLabel(self.current_screen, text="Vault not initialized.",
                             font=FONT_BODY).pack()
                return
            self.show_main_screen()
            return

        frame = self.current_screen
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        login_container = ctk.CTkFrame(frame, fg_color="transparent")
        login_container.grid(row=0, column=0, sticky="nsew")
        login_container.grid_columnconfigure(0, weight=1)
        login_container.grid_rowconfigure((0,1,2,3), weight=1)

        title_label = ctk.CTkLabel(login_container, text="Password Vault", font=FONT_TITLE)
        title_label.grid(row=1, column=0, pady=(10, 20))

        self.master_password_entry = ctk.CTkEntry(
            login_container, placeholder_text="Master Password", show="•",
            width=300, height=45, font=FONT_BODY
        )
        self.master_password_entry.grid(row=2, column=0, pady=10)
        self.master_password_entry.bind("<Return>", lambda e: self.check_master_password())

        login_button = ctk.CTkButton(
            login_container, text="Unlock Vault", command=self.check_master_password,
            width=250, height=45, font=FONT_BODY_BOLD
        )
        login_button.grid(row=3, column=0, pady=10)

        hint_label = ctk.CTkLabel(login_container, text="Enter your master password",
                                  font=FONT_BODY, text_color="gray")
        hint_label.grid(row=4, column=0, pady=(0, 20))

    def check_master_password(self):
        entered = self.master_password_entry.get()
        if not entered:
            messagebox.showerror("Error", "Password cannot be empty!")
            return

        self.master_password = entered
        if self.load_vault():
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Invalid master password or corrupted vault!")

    # ---------- ГЛАВНЫЙ ЭКРАН ----------
    def show_main_screen(self):
        self.clear_screen()

        frame = self.current_screen
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, text="Saved Passwords", font=FONT_SUBTITLE)
        title.grid(row=0, column=0, sticky="w")

        buttons_frame = ctk.CTkFrame(header, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")

        add_btn = ctk.CTkButton(buttons_frame, text="＋ Add", width=80, height=35,
                                font=FONT_BODY, command=self.add_entry)
        add_btn.pack(side="left", padx=5)

        logout_btn = ctk.CTkButton(buttons_frame, text="Logout", width=80, height=35,
                                   fg_color="gray", hover_color="darkgray",
                                   font=FONT_BODY, command=self.logout)
        logout_btn.pack(side="left", padx=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.refresh_password_list()

    def logout(self):
        self.master_password = None
        self.passwords = []
        self.password_visible.clear()
        self.show_login_screen()

    def refresh_password_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Сброс состояний видимости: все пароли скрыты
        self.password_visible.clear()

        for idx, entry in enumerate(self.passwords):
            self.create_password_card(idx, entry)

    def create_password_card(self, idx: int, entry: dict):
        card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, border_width=1)
        card.grid(row=idx, column=0, sticky="ew", padx=0, pady=8)
        card.grid_columnconfigure(0, weight=1)

        service_text = entry.get("service", "")
        login_text = entry.get("login", "")
        password_text = entry.get("password", "")
        note_text = entry.get("note", "")

        service_label = ctk.CTkLabel(card, text=f"Service: {service_text}",
                                     font=FONT_ENTRY, anchor="w")
        service_label.grid(row=0, column=0, sticky="w", padx=(15, 5), pady=(10, 2))
        if service_text:
            service_label.bind("<Button-1>", lambda e, t=service_text: self.copy_to_clipboard(t))

        login_label = ctk.CTkLabel(card, text=f"Login: {login_text}",
                                   font=FONT_ENTRY, anchor="w")
        login_label.grid(row=1, column=0, sticky="w", padx=(15, 5), pady=2)
        if login_text:
            login_label.bind("<Button-1>", lambda e, t=login_text: self.copy_to_clipboard(t))

        pwd_frame = ctk.CTkFrame(card, fg_color="transparent")
        pwd_frame.grid(row=2, column=0, sticky="w", padx=(15, 5), pady=2)

        # Определяем видимость пароля (по умолчанию скрыт)
        is_visible = self.password_visible.get(idx, False)
        if password_text:
            if is_visible:
                pwd_display_text = f"Password: {password_text}"
                toggle_btn_text = "🙈"
            else:
                pwd_display_text = "Password: ••••••"
                toggle_btn_text = "👁"
        else:
            pwd_display_text = "Password: "
            toggle_btn_text = None  # нет кнопки, если пароль пуст

        pwd_label = ctk.CTkLabel(pwd_frame, text=pwd_display_text,
                                 font=FONT_MONO, anchor="w")
        pwd_label.pack(side="left")

        if password_text:
            toggle_btn = ctk.CTkButton(pwd_frame, text=toggle_btn_text, width=30, height=22,
                                       font=FONT_SMALL, hover_color="gray")
            toggle_btn.pack(side="left", padx=(5, 0))
            toggle_btn.configure(command=lambda i=idx, lbl=pwd_label, btn=toggle_btn:
                                 self.toggle_password(i, lbl, btn))
            # копирование пароля по клику на текст (не важно скрыт или открыт)
            pwd_label.bind("<Button-1>", lambda e, t=password_text: self.copy_to_clipboard(t))
        else:
            pwd_label.bind("<Button-1>", lambda e: None)

        note_label = ctk.CTkLabel(card, text=f"Note: {note_text}",
                                  font=FONT_ENTRY, text_color="gray",
                                  anchor="w", wraplength=600, justify="left")
        note_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=15, pady=(0, 10))
        if note_text:
            note_label.bind("<Button-1>", lambda e, t=note_text: self.copy_to_clipboard(t))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=10, pady=(10, 0))

        edit_btn = ctk.CTkButton(btn_frame, text="Edit", width=70, height=30,
                                 font=FONT_BODY, command=lambda i=idx: self.edit_entry(i))
        edit_btn.pack(side="top", padx=2, pady=2)

        delete_btn = ctk.CTkButton(btn_frame, text="Delete", width=70, height=30,
                                   font=FONT_BODY, fg_color="red", hover_color="darkred",
                                   command=lambda i=idx: self.delete_entry(i))
        delete_btn.pack(side="top", padx=2, pady=2)

    def toggle_password(self, idx, label, button):
        """Переключает видимость пароля для записи с индексом idx."""
        entry = self.passwords[idx]
        password = entry.get("password", "")
        if not password:
            return
        new_state = not self.password_visible.get(idx, False)
        self.password_visible[idx] = new_state
        if new_state:
            label.configure(text=f"Password: {password}")
            button.configure(text="🙈")
        else:
            label.configure(text="Password: ••••••")
            button.configure(text="👁")

    # ---------- ДОБАВЛЕНИЕ / РЕДАКТИРОВАНИЕ / УДАЛЕНИЕ ----------
    def add_entry(self):
        self.open_entry_dialog()

    def edit_entry(self, idx: int):
        entry = self.passwords[idx]
        self.open_entry_dialog(
            idx=idx,
            service=entry.get("service", ""),
            login=entry.get("login", ""),
            password=entry.get("password", ""),
            note=entry.get("note", "")
        )

    def open_entry_dialog(self, idx: int = -1, service: str = "", login: str = "", password: str = "", note: str = ""):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Entry" if idx == -1 else "Edit Entry")
        dialog.geometry("500x400")
        dialog.minsize(450, 400)
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dialog, text="Service:", font=FONT_BODY).grid(row=0, column=0, sticky="w", padx=20, pady=(15,0))
        service_entry = ctk.CTkEntry(dialog, width=400, height=35, font=FONT_BODY)
        service_entry.insert(0, service)
        service_entry.grid(row=1, column=0, padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Login:", font=FONT_BODY).grid(row=2, column=0, sticky="w", padx=20, pady=(10,0))
        login_entry = ctk.CTkEntry(dialog, width=400, height=35, font=FONT_BODY)
        login_entry.insert(0, login)
        login_entry.grid(row=3, column=0, padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Password:", font=FONT_BODY).grid(row=4, column=0, sticky="w", padx=20, pady=(10,0))
        password_entry = ctk.CTkEntry(dialog, width=400, height=35, font=FONT_BODY, show="•")
        password_entry.insert(0, password)
        password_entry.grid(row=5, column=0, padx=20, pady=5)

        ctk.CTkLabel(dialog, text="Note (optional):", font=FONT_BODY).grid(row=6, column=0, sticky="w", padx=20, pady=(10,0))
        note_entry = ctk.CTkEntry(dialog, width=400, height=35, font=FONT_BODY)
        note_entry.insert(0, note)
        note_entry.grid(row=7, column=0, padx=20, pady=5)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=8, column=0, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)

        def save():
            new_service = service_entry.get().strip()
            new_login = login_entry.get().strip()
            new_password = password_entry.get().strip()
            new_note = note_entry.get().strip()

            if not new_service and not new_login and not new_password:
                messagebox.showerror("Error", "At least one of Service, Login or Password must be filled!")
                return

            new_record = {}
            if new_service:
                new_record["service"] = new_service
            if new_login:
                new_record["login"] = new_login
            if new_password:
                new_record["password"] = new_password
            if new_note:
                new_record["note"] = new_note

            if idx == -1:
                self.passwords.append(new_record)
            else:
                self.passwords[idx] = new_record

            self.refresh_password_list()
            self.save_vault()
            dialog.destroy()

        save_btn = ctk.CTkButton(btn_frame, text="Save", command=save,
                                 width=120, height=35, font=FONT_BODY)
        save_btn.grid(row=0, column=0, padx=5)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                                   width=120, height=35, font=FONT_BODY,
                                   fg_color="gray", hover_color="darkgray")
        cancel_btn.grid(row=0, column=1, padx=5)

    def delete_entry(self, idx: int):
        if messagebox.askyesno("Confirm Delete", "Delete this entry?"):
            if 0 <= idx < len(self.passwords):
                del self.passwords[idx]
                # Так как индексы сдвинулись, очищаем состояния видимости
                self.password_visible.clear()
                self.refresh_password_list()
                self.save_vault()


if __name__ == "__main__":
    app = PasswordVaultApp()
    app.mainloop()