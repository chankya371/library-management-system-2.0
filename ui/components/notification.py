import customtkinter as ctk
from tkinter import filedialog
from ui.theme import Theme
from utils.icon_factory import IconFactory


class ConfirmDialog(ctk.CTkToplevel):
    """Modern modal dialog for user confirmation of destructive or important actions."""

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        on_confirm,
        confirm_text: str = "Confirm",
        danger: bool = False,
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("440x220")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 220
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self.on_confirm = on_confirm

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=24)

        # Header with icon
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        icon_name = "trash" if danger else "alert"
        icon_color = Theme.DANGER if danger else Theme.WARNING
        icon_img = IconFactory.get_icon(icon_name, size=(22, 22), color_light="#ef4444" if danger else "#f59e0b", color_dark="#ef4444" if danger else "#f59e0b")
        icon_lbl = ctk.CTkLabel(header, text="", image=icon_img)
        icon_lbl.pack(side="left", padx=(0, 10))

        title_lbl = ctk.CTkLabel(header, text=title, font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY)
        title_lbl.pack(side="left")

        # Message
        msg_lbl = ctk.CTkLabel(
            container,
            text=message,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
            wraplength=380,
            justify="left",
        )
        msg_lbl.pack(fill="x", pady=(0, 20))

        # Action Buttons
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            font=Theme.FONT_BODY,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        conf_btn = ctk.CTkButton(
            btn_box,
            text=confirm_text,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.DANGER if danger else Theme.PRIMARY,
            hover_color=Theme.DANGER_HOVER if danger else Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=120,
            height=36,
            command=self._handle_confirm,
        )
        conf_btn.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()


class AlertDialog(ctk.CTkToplevel):
    """Modern modal dialog for notifications and messages."""

    def __init__(self, parent, title: str, message: str, level: str = "info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x200")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=24)

        icon_map = {
            "success": ("check", "#10b981"),
            "error": ("alert", "#ef4444"),
            "info": ("check", "#3b82f6"),
        }
        ic_name, ic_color = icon_map.get(level, ("check", "#3b82f6"))
        icon_img = IconFactory.get_icon(ic_name, size=(22, 22), color_light=ic_color, color_dark=ic_color)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        icon_lbl = ctk.CTkLabel(header, text="", image=icon_img)
        icon_lbl.pack(side="left", padx=(0, 10))

        title_lbl = ctk.CTkLabel(header, text=title, font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY)
        title_lbl.pack(side="left")

        msg_lbl = ctk.CTkLabel(
            container,
            text=message,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
            wraplength=360,
            justify="left",
        )
        msg_lbl.pack(fill="x", pady=(0, 16))

        ok_btn = ctk.CTkButton(
            container,
            text="OK",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=100,
            height=34,
            command=self.destroy,
        )
        ok_btn.pack(side="right")


class ReceiptDialog(ctk.CTkToplevel):
    """Dialog displaying a formatted receipt with Print / Save and Copy features."""

    def __init__(self, parent, title: str, receipt_text: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        self.receipt_text = receipt_text

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        title_lbl = ctk.CTkLabel(header, text=title, font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY)
        title_lbl.pack(side="left")

        # Text box
        self.textbox = ctk.CTkTextbox(
            container,
            font=("Courier New", 11),
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=8,
            wrap="none",
        )
        self.textbox.pack(fill="both", expand=True, pady=(0, 16))
        self.textbox.insert("1.0", receipt_text)
        self.textbox.configure(state="disabled")

        # Buttons
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x")

        close_btn = ctk.CTkButton(
            btn_box,
            text="Close",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=90,
            height=36,
            command=self.destroy,
        )
        close_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_box,
            text="Save to File",
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=110,
            height=36,
            command=self._save_to_file,
        )
        save_btn.pack(side="right", padx=(8, 0))

        copy_btn = ctk.CTkButton(
            btn_box,
            text="Copy Text",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self._copy_clipboard,
        )
        copy_btn.pack(side="right")

    def _copy_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.receipt_text)
        AlertDialog(self, "Copied", "Receipt text copied to clipboard!", level="success")

    def _save_to_file(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Receipt",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.receipt_text)
                AlertDialog(self, "Saved", f"Receipt saved successfully to {path}", level="success")
            except Exception as e:
                AlertDialog(self, "Error", f"Could not save file: {e}", level="error")
