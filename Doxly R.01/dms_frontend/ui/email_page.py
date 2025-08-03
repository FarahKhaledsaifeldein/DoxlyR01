from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit,
                             QComboBox, QFrame, QDialog, QFormLayout, QMessageBox,
                             QFileDialog, QListWidget, QListWidgetItem, QSplitter)

import subprocess
import os
from PyQt6.QtGui import QIcon
from api.notifications_api import NotificationAPI 
import requests

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from typing import List, Dict, Any, Optional, Tuple, IO
import sys
import logging
from api.emails_api import EmailAPI


logger = logging.getLogger(__name__)

class EmailPage(QWidget):
    def __init__(self, token=None, username=None, parent=None):
        super().__init__(parent)
        self.token = token
        self.username = username
        
        # Initialize APIs
        self.email_api = EmailAPI()
        self.notification_api = NotificationAPI()
        
        self.current_folder = "inbox"
        self.emails = []
        self.current_date=""
        
        self.setup_ui()
        self.load_emails_and_notifications()
        self.setup_notification_panel()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Email Client")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        self.setup_header(main_layout)
        
        # Email interface
        self.setup_email_interface(main_layout)

    def setup_header(self, main_layout):
        """Set up the header section"""
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title = QLabel("E-Mail")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Notification badge
        self.notification_badge = QLabel("0")
        self.notification_badge.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 12px;
                min-width: 20px;
                text-align: center;
            }
        """)
        self.notification_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.notification_badge)
        
        # Notification button
        self.notification_btn = QPushButton()
        self.notification_btn.setIcon(QIcon.fromTheme("notifications"))
        self.notification_btn.setIconSize(QSize(24, 24))
        self.notification_btn.setToolTip("View notifications")
        self.notification_btn.clicked.connect(self.show_notifications)
        header_layout.addWidget(self.notification_btn)
        
        # Outlook integration button
        outlook_btn = QPushButton("Open in Outlook")
        outlook_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        outlook_btn.clicked.connect(self.open_outlook)
        header_layout.addWidget(outlook_btn)
        
        # New email button
        new_email_btn = QPushButton("New Email")
        new_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        new_email_btn.clicked.connect(self.compose_new_email)
        header_layout.addWidget(new_email_btn)
        
        main_layout.addWidget(self.header)

    def setup_email_interface(self, main_layout):
        """Set up the main email interface"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Email folders list
        folders_frame = QFrame()
        folders_frame.setFrameShape(QFrame.Shape.StyledPanel)
        folders_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        folders_layout = QVBoxLayout(folders_frame)
        
        folders_title = QLabel("Folders")
        folders_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        folders_layout.addWidget(folders_title)
        
        self.folders_list = QListWidget()
        self.folders_list.addItems(["Inbox", "Sent Items", "Drafts"])#, "Deleted Items", "Junk Email", "Outbox"])
        self.folders_list.setCurrentRow(0)
        self.folders_list.currentItemChanged.connect(self.folder_changed)
        self.folders_list.setStyleSheet("color: black;")
        folders_layout.addWidget(self.folders_list)
        
        # Email list and preview
        email_container = QWidget()
        email_layout = QVBoxLayout(email_container)
        
        # Search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search emails...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        search_layout.addWidget(self.search_box)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_emails)
        search_layout.addWidget(search_btn)
        
        email_layout.addWidget(search_container)
        
        # Email list
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["To", "Subject", "Date", "Attachments"])
        self.email_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: black;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: black;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                color: black;
            }
        """)
        self.email_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.email_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.email_table.itemClicked.connect(self.email_selected)
        email_layout.addWidget(self.email_table)
        
        # Email preview
        self.setup_email_preview(email_layout)
        
        # Add widgets to splitter
        splitter.addWidget(folders_frame)
        splitter.addWidget(email_container)
        splitter.setSizes([150, 650])
        
        main_layout.addWidget(splitter)

    def setup_email_preview(self, layout):
        """Set up the email preview section"""
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        self. email_subject = QLabel("Select an email to preview")
        self.email_subject.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        preview_layout.addWidget(self.email_subject)
        
        self.email_from = QLabel("")
        self.email_from.setStyleSheet("color: black;")
        preview_layout.addWidget(self.email_from)
        
        self.email_date = QLabel("")
        self.email_date.setStyleSheet("color: black;")
        preview_layout.addWidget(self.email_date)
        
        message_label = QLabel("Message:")
        message_label.setStyleSheet("color: black;")
        preview_layout.addWidget(message_label)
        
        self.email_body = QTextEdit()
        self.email_body.setReadOnly(True)
        self.email_body.setStyleSheet("color: black; background-color: white;")
        preview_layout.addWidget(self.email_body)
        
        # Email actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        
        reply_btn = QPushButton("Reply")
        reply_btn.clicked.connect(self.reply_email)
        actions_layout.addWidget(reply_btn)
        
        forward_btn = QPushButton("Forward")
        forward_btn.clicked.connect(self.forward_email)
        actions_layout.addWidget(forward_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_email)
        actions_layout.addWidget(delete_btn)
        
        preview_layout.addWidget(actions_container)
        
        layout.addWidget(preview_frame)

    def setup_notification_panel(self):
        """Initialize and update the notification panel"""
        self.update_notification_count()

    def update_notification_count(self):
        """Update the notification badge count"""
        try:
            notifications = self.notification_api.get_notifications(self.token)
            self.notification_badge.setText(str(len(notifications)))
            self.notification_badge.setVisible(bool(notifications))
        except Exception as e:
            logger.error(f"Failed to update notification count: {str(e)}")

    def show_notifications(self):
        """Display notifications in a dialog"""
        try:
            notifications = self.notification_api.get_notifications(self.token)
            if not notifications:
                QMessageBox.information(self, "Notifications", "No new notifications")
                return
                
            dialog = QDialog(self)
            dialog.setWindowTitle("Notifications")
            dialog.setMinimumSize(400, 300)
            layout = QVBoxLayout(dialog)
            
            list_widget = QListWidget()
            for notification in notifications:
                item = QListWidgetItem(f"{notification.get('subject', 'No subject')} - {notification.get('sent_at', 'No date')}")
                item.setData(Qt.ItemDataRole.UserRole, notification.get('id'))
                list_widget.addItem(item)
            
            layout.addWidget(list_widget)
            
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            
            mark_read_btn = QPushButton("Mark as Read")
            mark_read_btn.clicked.connect(lambda: self.mark_notification_read(list_widget, dialog))
            btn_layout.addWidget(mark_read_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(close_btn)
            
            layout.addWidget(btn_container)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Failed to show notifications: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load notifications: {str(e)}")

    def mark_notification_read(self, list_widget, dialog):
        """Mark selected notifications as read"""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select notifications to mark as read")
            return
            
        for item in selected_items:
            notification_id = item.data(Qt.ItemDataRole.UserRole)
            if self.notification_api.mark_as_read(self.token, notification_id):
                list_widget.takeItem(list_widget.row(item))
        
        if list_widget.count() == 0:
            dialog.accept()
        
        self.update_notification_count()

    def load_emails_and_notifications(self):
        """Load both emails and notifications"""
        self.load_emails()
        self.update_notification_count()

    def load_emails(self):
        """Load emails for the current folder"""
        try:
            folder_map = {
                "Inbox": "inbox",
                "Sent Items": {"status":"sent"},
                "Drafts": "drafts",
                #"Junk Email": "spam",
                #"Outbox": "outbox"
            }
            
            current_folder = self.folders_list.currentItem().text()
            self.current_folder = folder_map.get(current_folder, "inbox")
            
            if self.current_folder == "drafts":
                self.load_drafts()
            else:
                self.emails = self.email_api.get_emails(self.token, self.current_folder)
                self.display_emails()
                
        except Exception as e:
            logger.error(f"Failed to load emails: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load emails: {str(e)}")

    def display_emails(self):
        """Display emails in the table"""
        self.email_table.setRowCount(len(self.emails))
        
        for row, email in enumerate(self.emails):
            raw_date = email.get('sent_at', email.get('sent_at', ''))
            self.current_date = raw_date[:10] if raw_date else ""
            self.email_table.setItem(row, 0, QTableWidgetItem(email.get("recipient_email", "")))
            self.email_table.setItem(row, 1, QTableWidgetItem(email.get("subject", "")))
            self.email_table.setItem(row, 2, QTableWidgetItem(self.current_date))
            self.email_table.setItem(row, 3, QTableWidgetItem(email.get("status", "")))

    def load_drafts(self):
        """Load draft emails"""
        try:
            self.emails = self.email_api.get_drafts(self.token)
            if not self.emails:
                QMessageBox.information(self, "Drafts", "No draft emails found")
            
            self.email_table.setRowCount(len(self.emails))
            self.email_table.setHorizontalHeaderLabels(["To", "Subject", "Date", "Status"])
            
            for row, draft in enumerate(self.emails):
                raw_date = draft.get('sent_at', draft.get('sent_at', ''))
                self.current_date = raw_date[:10] if raw_date else ""
                self.email_table.setItem(row, 0, QTableWidgetItem(draft.get("recipient_email", "")))
                self.email_table.setItem(row, 1, QTableWidgetItem(draft.get("subject", "")))
                self.email_table.setItem(row, 2, QTableWidgetItem(self.current_date))
                self.email_table.setItem(row, 3, QTableWidgetItem("Draft"))
                
        except Exception as e:
            logger.error(f"Failed to load drafts: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load drafts: {str(e)}")

    def folder_changed(self, current, previous):
        """Handle folder selection change"""
        if current:
            self.load_emails()
            self.clear_email_preview()

    def clear_email_preview(self):
        """Clear the email preview pane"""
        self.email_subject.setText("Select an email to preview")
        self.email_from.setText("")
        self.email_date.setText("")
        self.email_body.setText("")

    def email_selected(self, item):
        """Display the selected email"""
        row = item.row()
        if row < 0 or row >= len(self.emails):
            return
            
        email = self.emails[row]
        raw_date = email.get('sent_at', email.get('sent_at', ''))
        self.current_date = raw_date[:10] if raw_date else ""
        self.email_subject.setText(f"Subject: {email.get('subject', 'No subject')}")
        self.email_from.setText(f"to: {email.get('recipient_email', 'Unknown')}")
        self.email_date.setText(f"Date: {self.current_date}")
        self.email_body.setText(email.get("body", "No content"))
        #self.email_status.setText(f"Status: {email.get('status', 'Unknown')}")

    def search_emails(self):
        """Search emails based on search text"""
        search_text = self.search_box.text().strip().lower()
        if not search_text:
            self.display_emails()
            return
            
        filtered_emails = [
            email for email in self.emails
            if (search_text in email.get("recipient_email", "").lower() or 
                search_text in email.get("subject", "").lower() or 
                search_text in email.get("body", "").lower())
        ]
        
        self.email_table.setRowCount(len(filtered_emails))
        for row, email in enumerate(filtered_emails):
            raw_date = email.get('sent_at', email.get('sent_at', ''))
            self.current_date = raw_date[:10] if raw_date else ""
            self.email_table.setItem(row, 0, QTableWidgetItem(email.get("recipient_email", "")))
            self.email_table.setItem(row, 1, QTableWidgetItem(email.get("subject", "")))
            self.email_table.setItem(row, 2, QTableWidgetItem(self.current_date))
            self.email_table.setItem(row, 3, QTableWidgetItem(email.get("status", "")))

    def open_outlook(self):
        """Open Outlook application"""
        try:
            # Try different ways to open Outlook depending on OS
            if os.name == 'nt':  # Windows
                os.startfile("outlook")
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(["open", "-a", "Microsoft Outlook"] if sys.platform == 'darwin' 
                               else ["xdg-open", "mailto:"])
        except Exception as e:
            logger.error(f"Failed to open Outlook: {str(e)}")
            QMessageBox.warning(
                self,
                "Outlook Not Available",
                "Could not open Microsoft Outlook. Please ensure it is installed and configured."
            )

    def compose_new_email(self):
        """Open compose email dialog"""
        dialog = ComposeEmailDialog(self.token, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_emails()

    def reply_email(self):
        """Reply to selected email"""
        selected = self.email_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an email to reply to")
            return
            
        row = selected[0].row()
        if row >= len(self.emails):
            return
            
        email = self.emails[row]
        dialog = ComposeEmailDialog(self.token, parent=self)
        
        to_address = email.get("from", "")
        subject = email.get("subject", "")
        body = email.get("body", "")
        raw_date = email.get("sent_at", "")
        self.current_date = raw_date[:10] if raw_date else ""
        date = self.current_date
        
        dialog.to_field.setText(to_address)
        dialog.subject_field.setText(f"Re: {subject}" if subject else "Re: ")
        dialog.message_field.setText(
            f"\n\n-------- Original Message --------\n"
            f"From: {to_address}\n"
            f"Date: {date}\n"
            f"Subject: {subject}\n\n"
            f"{body}"
        )
        
        dialog.exec()

    def forward_email(self):
        """Forward selected email"""
        selected = self.email_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an email to forward")
            return
            
        row = selected[0].row()
        if row >= len(self.emails):
            return
            
        email = self.emails[row]
        dialog = ComposeEmailDialog(self.token, parent=self)
        
        subject = email.get("subject", "")
        body = email.get("body", "")
        from_address = email.get("from", "")
        raw_date = email.get("sent_at", "")
        self.current_date = raw_date[:10] if raw_date else ""
        date = self.current_date
        
        dialog.subject_field.setText(f"Fwd: {subject}" if subject else "Fwd: ")
        dialog.message_field.setText(
            f"\n\n-------- Forwarded Message --------\n"
            f"From: {from_address}\n"
            f"Date: {date}\n"
            f"Subject: {subject}\n\n"
            f"{body}"
        )
        
        dialog.exec()

    def delete_email(self):
        """Delete selected email"""
        selected = self.email_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an email to delete")
            return
            
        row = selected[0].row()
        if row >= len(self.emails):
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this email?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # In a real implementation, this would call an API to delete the email
            self.email_table.removeRow(row)
            if row < len(self.emails):
                del self.emails[row]
            self.clear_email_preview()


class ComposeEmailDialog(QDialog):
    """Dialog for composing new emails with multipart form data support"""
    
    MAX_ATTACHMENTS = 5
    MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, token: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.token = token
        self.email_api = EmailAPI()
        self.setWindowTitle("Compose Email")
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the compose email UI"""
        layout = QVBoxLayout(self)
        
        # Email form
        form_layout = QFormLayout()
        
        # Recipient fields
        self.to_field = QLineEdit()
        self.to_field.setPlaceholderText("recipient@example.com")
        self.cc_field = QLineEdit()
        self.cc_field.setPlaceholderText("cc@example.com")
        self.bcc_field = QLineEdit()
        self.bcc_field.setPlaceholderText("bcc@example.com")
        self.subject_field = QLineEdit()
        self.subject_field.setPlaceholderText("Subject")
        
        form_layout.addRow("To:", self.to_field)
        form_layout.addRow("Cc:", self.cc_field)
        form_layout.addRow("Bcc:", self.bcc_field)
        form_layout.addRow("Subject:", self.subject_field)
        
        layout.addLayout(form_layout)
        
        # Message body
        self.message_field = QTextEdit()
        self.message_field.setPlaceholderText("Type your message here...")
        layout.addWidget(self.message_field)
        
        # Attachments
        self.setup_attachments_section(layout)
        
        # Buttons
        self.setup_action_buttons(layout)
    
    def setup_attachments_section(self, layout):
        """Set up the attachments section"""
        attachments_label = QLabel("Attachments:")
        layout.addWidget(attachments_label)
        
        attachments_container = QWidget()
        attachments_layout = QHBoxLayout(attachments_container)
        attachments_layout.setContentsMargins(0, 0, 0, 0)
        
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(100)
        attachments_layout.addWidget(self.attachments_list)
        
        attach_btn = QPushButton("Attach File")
        attach_btn.clicked.connect(self.attach_file)
        attachments_layout.addWidget(attach_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_attachment)
        attachments_layout.addWidget(remove_btn)
        
        layout.addWidget(attachments_container)
    
    def setup_action_buttons(self, layout):
        """Set up the action buttons"""
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        send_btn.clicked.connect(self.send_email)
        
        save_draft_btn = QPushButton("Save Draft")
        save_draft_btn.clicked.connect(self.save_draft)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(send_btn)
        buttons_layout.addWidget(save_draft_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addWidget(buttons_container)
    
    def attach_file(self):
        """Attach a file to the email"""
        if self.attachments_list.count() >= self.MAX_ATTACHMENTS:
            QMessageBox.warning(
                self,
                "Maximum Attachments",
                f"You can attach a maximum of {self.MAX_ATTACHMENTS} files"
            )
            return
            
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        
        if file_dialog.exec():
            for file_path in file_dialog.selectedFiles():
                if self.attachments_list.count() >= self.MAX_ATTACHMENTS:
                    break
                    
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.MAX_ATTACHMENT_SIZE:
                        QMessageBox.warning(
                            self,
                            "File Too Large",
                            f"{os.path.basename(file_path)} exceeds the maximum size of "
                            f"{self.MAX_ATTACHMENT_SIZE // (1024 * 1024)}MB"
                        )
                        continue
                        
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setData(Qt.ItemDataRole.UserRole, file_path)
                    self.attachments_list.addItem(item)
                except Exception as e:
                    logger.error(f"Failed to attach file: {str(e)}")
                    QMessageBox.warning(
                        self,
                        "Attachment Error",
                        f"Could not attach {os.path.basename(file_path)}: {str(e)}"
                    )
    
    def remove_attachment(self):
        """Remove selected attachment"""
        selected = self.attachments_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an attachment to remove")
            return
            
        for item in selected:
            self.attachments_list.takeItem(self.attachments_list.row(item))
    
    def prepare_email_data(self) -> Dict[str, Any]:
        """Prepare the email data dictionary"""
        return {
            'to': self.to_field.text().strip(),
            'subject': self.subject_field.text().strip(),
            'body': self.message_field.toPlainText().strip(),
            'cc': self.cc_field.text().strip(),
            'bcc': self.bcc_field.text().strip()
        }
    
    def prepare_attachments(self) -> List[Tuple[str, str]]:
        """Prepare attachments list of (filename, filepath) tuples"""
        attachments = []
        for i in range(self.attachments_list.count()):
            item = self.attachments_list.item(i)
            filepath = item.data(Qt.ItemDataRole.UserRole)
            if os.path.exists(filepath):
                attachments.append((os.path.basename(filepath), filepath))
        return attachments
    
    def send_email(self):
        """Send email with attachments using multipart form data"""
        email_data = self.prepare_email_data()
        
        # Validate required fields
        if not email_data['to']:
            QMessageBox.warning(self, "Error", "Please specify at least one recipient")
            return
        
        try:
            attachments = self.prepare_attachments()
            
            if self.email_api.send_email(self.token, email_data, attachments):
                QMessageBox.information(self, "Success", "Email sent successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to send email")
                
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to send email: {str(e)}"
            )
    
    def save_draft(self):
        """Save draft with attachments using multipart form data"""
        email_data = self.prepare_email_data()
        
        try:
            attachments = self.prepare_attachments()
            
            if self.email_api.save_draft(self.token, email_data, attachments):
                QMessageBox.information(self, "Success", "Draft saved successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to save draft")
                
        except Exception as e:
            logger.error(f"Failed to save draft: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save draft: {str(e)}"
            )
'''"""

#import mimetypesn 

class EmailPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.username = username
        
        self.notification_api = NotificationsAPI()
        self.setup_ui()
        self.load_emails_and_notifications()
        self.setup_notification_panel()
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("E-Mail")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title)
        
        # Outlook integration button
        outlook_btn = QPushButton("Open in Outlook")
        outlook_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        outlook_btn.clicked.connect(self.open_outlook)
        header_layout.addWidget(outlook_btn)
        
        # New email button
        new_email_btn = QPushButton("New Email")
        new_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        new_email_btn.clicked.connect(self.compose_new_email)
        header_layout.addWidget(new_email_btn)
        
        main_layout.addWidget(self.header)
        
        # Email interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Email folders list
        folders_frame = QFrame()
        folders_frame.setFrameShape(QFrame.Shape.StyledPanel)
        folders_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        folders_layout = QVBoxLayout(folders_frame)
        
        folders_title = QLabel("Folders")
        folders_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        folders_layout.addWidget(folders_title)
        
        self.folders_list = QListWidget()
        self.folders_list.addItems(["Inbox", "Sent Items", "Drafts", "Deleted Items", "Junk Email", "Outbox"])
        self.folders_list.setCurrentRow(0)  # Select Inbox by default
        self.folders_list.currentItemChanged.connect(self.folder_changed)
        self.folders_list.setStyleSheet("color: black;")
        folders_layout.addWidget(self.folders_list)
        
        # Email list and preview
        email_container = QWidget()
        email_layout = QVBoxLayout(email_container)
        
        # Search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search emails...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        search_layout.addWidget(self.search_box)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_emails)
        search_layout.addWidget(search_btn)
        
        email_layout.addWidget(search_container)
        
        # Email list
        self.email_table = QTableWidget()
        self.email_table.setColumnCount(4)
        self.email_table.setHorizontalHeaderLabels(["From", "Subject", "Date", "Attachments"])
        self.email_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: black;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: black;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                color: black;
            }
        """)
        self.email_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.email_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.email_table.itemClicked.connect(self.email_selected)
        
        # Add sample data
        self.load_sample_emails()
        
        email_layout.addWidget(self.email_table)
        
        # Email preview
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.email_subject = QLabel("Select an email to preview")
        self.email_subject.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        preview_layout.addWidget(self.email_subject)
        
        self.email_from = QLabel("")
        self.email_from.setStyleSheet("color: black;")
        preview_layout.addWidget(self.email_from)
        
        self.email_date = QLabel("")
        self.email_date.setStyleSheet("color: black;")
        preview_layout.addWidget(self.email_date)
        
        message_label = QLabel("Message:")
        message_label.setStyleSheet("color: black;")
        preview_layout.addWidget(message_label)
        
        self.email_body = QTextEdit()
        self.email_body.setReadOnly(True)
        self.email_body.setStyleSheet("color: black; background-color: white;")
        preview_layout.addWidget(self.email_body)
        
        # Email actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        
        reply_btn = QPushButton("Reply")
        reply_btn.clicked.connect(self.reply_email)
        actions_layout.addWidget(reply_btn)
        
        forward_btn = QPushButton("Forward")
        forward_btn.clicked.connect(self.forward_email)
        actions_layout.addWidget(forward_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_email)
        actions_layout.addWidget(delete_btn)
        
        preview_layout.addWidget(actions_container)
        
        email_layout.addWidget(preview_frame)
        
        # Add widgets to splitter
        splitter.addWidget(folders_frame)
        splitter.addWidget(email_container)
        splitter.setSizes([100, 500])  # Set initial sizes
        
        main_layout.addWidget(splitter)
    
    def setup_notification_panel(self):
        """Add a notification panel to the UI"""
        self.notification_badge = QLabel("0")
        self.notification_badge.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 12px;
                min-width: 20px;
                text-align: center;
            }
        """)
        self.notification_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to header
        header_layout = self.header.layout()  # Assuming you have access to the header layout
        header_layout.insertWidget(header_layout.count() - 2, self.notification_badge) # Add to appropriate position
        
        # Notification dropdown button
        self.notification_btn = QPushButton()
        self.notification_btn.setIcon(QIcon.fromTheme("notifications"))
        self.notification_btn.clicked.connect(self.show_notifications)
        header_layout.insertWidget(header_layout.count() - 1, self.notification_btn)
    def show_notifications(self):
        """Show notifications in a popup"""
        try:
            notifications = self.notifications_api.get_notifications(self.token)
            if not notifications:
                QMessageBox.information(self, "Notifications", "No new notifications")
                return
                
            dialog = QDialog(self)
            dialog.setWindowTitle("Notifications")
            layout = QVBoxLayout(dialog)
            
            list_widget = QListWidget()
            for notification in notifications:
                item = QListWidgetItem(f"{notification['subject']} - {notification['sent_at']}")
                item.setData(Qt.ItemDataRole.UserRole, notification['id'])
                list_widget.addItem(item)
            
            layout.addWidget(list_widget)
            
            mark_read_btn = QPushButton("Mark as Read")
            mark_read_btn.clicked.connect(lambda: self.mark_notification_read(list_widget))
            layout.addWidget(mark_read_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load notifications: {str(e)}")
    



    def mark_notification_read(self, list_widget):
        """Mark selected notifications as read"""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            notification_id = item.data(Qt.ItemDataRole.UserRole)
            success = self.notifications_api.mark_as_read(self.token, notification_id)
            if success:
                list_widget.takeItem(list_widget.row(item))

    def load_emails_and_notifications(self):
        """Load both emails and notifications"""
        self.load_sample_emails()  # Or replace with real API call
        self.load_notifications()
    def load_notifications(self):
        """Load notifications from API"""
        try:
            notifications = self.notifications_api.get_notifications(self.token)
            if notifications:
                print(f"Loaded {len(notifications)} notifications")
                # Process notifications as needed
                # You could add them to a notifications panel or badge counter
        except Exception as e:
            print(f"Error loading notifications: {str(e)}")
    def send_email(self):
        """Send email using your backend API"""
        # Validate required fields
        if not self.to_field.text():
            QMessageBox.warning(self, "Error", "Please specify at least one recipient")
            return
        
        if not self.subject_field.text():
            reply = QMessageBox.question(self, "Missing Subject", "Send this message without a subject?")
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            # Prepare email data
            email_data = {
                "recipient_email": self.to_field.text(),
                "subject": self.subject_field.text(),
                "body": self.message_field.toPlainText(),
                "cc": self.cc_field.text(),
                "bcc": self.bcc_field.text(),
                # Add attachment handling if needed
            }
            files = []
            for i in range(self.attachments_list.count()):
                item = self.attachments_list.item(i)
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if os.path.exists(file_path):
                    files.append(('attachments', (
                        os.path.basename(file_path),
                        open(file_path, 'rb'),
                        'application/octet-stream'
                    )))
            
            # Send via your API
            
            response = requests.post(
                f"http://localhost:8000/api/notifications/email/send/",
                headers = {
                'Authorization': f'Bareer {self.token}',
                
            },
                data=email_data,
                files=files
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Email sent successfully!")
                self.load_notifications()  # Refresh notifications
                self.accept()
            else:
                QMessageBox.warning(self, "Error", f"Failed to send email: {response.text}")
                
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
        finally:
        # Close all file handles
            for _, file_tuple in files:
                file_tuple[1].close()


    
    def load_sample_emails(self):
        # Sample data for demonstration
        try:
            response = requests.get(
                "http://localhost:8000/api/notifications/emails/",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                emails = response.json()
                
            else:
                emails = []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sample emails: {str(e)}")
            return
        
        
        self.email_table.setRowCount(len(emails))
        self.emails = emails  # Store for reference
        
        for i, email in enumerate(emails):
            self.email_table.setItem(i, 0, QTableWidgetItem(email["from"]))
            self.email_table.setItem(i, 1, QTableWidgetItem(email["subject"]))
            self.email_table.setItem(i, 2, QTableWidgetItem(email["date"]))
            self.email_table.setItem(i, 3, QTableWidgetItem(email["attachments"]))
    
    def folder_changed(self, current, previous):
        if current:
            folder_name = current.text()
            if folder_name == "Drafts":
                self.load_drafts()
            else:
                self.load_sample_emails()
        
            # In a real app, this would load emails from the selected folder
            print(f"Selected folder: {folder_name}")
            
            # For demonstration, just show a message
            self.email_subject.setText(f"Folder: {folder_name}")
            self.email_from.setText("")
            self.email_date.setText("")
            self.email_body.setText(f"Viewing emails in {folder_name}")
            
            # Reload sample emails
            try:
                self.load_sample_emails()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reload emails: {str(e)}")
    
    def load_drafts(self):
        try:
        # Initialize compose dialog if it doesn't exist
            if not hasattr(self, 'compose_dialog') or self.compose_dialog is None:

                self.compose_dialog = ComposeEmailDialog(parent=self, token=self.token)
            
        # Load drafts directly from API instead of through compose_dialog
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(
            "http://localhost:8000/api/notifications/emails/drafts/",
            headers=headers
        )
        
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            
            drafts = response.json()
        
            if not drafts:
                self.email_table.setRowCount(0)
                QMessageBox.information(self, "Drafts", "No draft emails found")
                return
            
        # Configure table
        self.email_table.setRowCount(len(drafts))
        self.email_table.setHorizontalHeaderLabels(["To", "Subject", "Date", "Status"])
        self.email_table.setColumnWidth(0, 200)  # Set column widths
        self.email_table.setColumnWidth(1, 300)
        self.email_table.setColumnWidth(2, 150)
        self.email_table.setColumnWidth(3, 100)
        
        # Populate table
        for i, draft in enumerate(drafts):
            if not isinstance(draft, dict):
                continue
                
            self.email_table.setItem(i, 0, QTableWidgetItem(draft.get('recipient_email', '')))
            self.email_table.setItem(i, 1, QTableWidgetItem(draft.get('subject', '')))
            self.email_table.setItem(i, 2, QTableWidgetItem(draft.get('created_at', '')))  # Changed from sent_at
            self.email_table.setItem(i, 3, QTableWidgetItem("Draft"))
            
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(self, "Network Error", 
            f"Failed to connect to server: {str(e)}")
        self.email_table.setRowCount(0)
    except Exception as e:
        QMessageBox.critical(self, "Error", 
            f"Failed to load drafts: {str(e)}")
        self.email_table.setRowCount(0)
    def email_selected(self, item):
        row = item.row()
        email = self.emails[row]
        
        self.email_subject.setText(email["subject"])
        self.email_from.setText(f"From: {email['from']}")
        self.email_date.setText(f"Date: {email['date']}")
        self.email_body.setText(email["body"])
    
    def search_emails(self):
        search_text = self.search_box.text().lower()
        if not search_text:
            # If search is empty, reload all emails
            self.load_sample_emails()
            return
        
        # Filter emails based on search text
        filtered_emails = []
        for email in self.emails:
            if (search_text in email["from"].lower() or 
                search_text in email["subject"].lower() or 
                search_text in email["body"].lower()):
                filtered_emails.append(email)
        
        # Update table with filtered results
        self.email_table.setRowCount(len(filtered_emails))
        for i, email in enumerate(filtered_emails):
            self.email_table.setItem(i, 0, QTableWidgetItem(email["from"]))
            self.email_table.setItem(i, 1, QTableWidgetItem(email["subject"]))
            self.email_table.setItem(i, 2, QTableWidgetItem(email["date"]))
            self.email_table.setItem(i, 3, QTableWidgetItem(email["attachments"]))
    
    def open_outlook(self):
        """Open Outlook with proper error handling"""
        app_available, app_path = self.office_handler.check_office_app('outlook')
        
        if not app_available:
            QMessageBox.warning(
                self,
                "Application Not Found",
                "Microsoft Outlook is not installed on your system. Please install Microsoft Office or configure your email client."
            )
            return
        
        try:
            subprocess.Popen([app_path])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not open Outlook: {str(e)}\n\nPlease make sure Microsoft Outlook is properly installed and configured."
            )
    
    def compose_new_email(self):
        dialog = ComposeEmailDialog(token=self.token,parent=self)
        dialog.exec()
    
    def reply_email(self):
        selected_items = self.email_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an email to reply to")
            return
        
        row = selected_items[0].row()
        email = self.emails[row]
        
        dialog = ComposeEmailDialog(parent=self,token=self.token)
        dialog.to_field.setText(email["from"])
        dialog.subject_field.setText(f"RE: {email['subject']}")
        dialog.message_field.setText(f"\n\n-------- Original Message --------\nFrom: {email['from']}\nDate: {email['date']}\nSubject: {email['subject']}\n\n{email['body']}")
        dialog.exec()
    
    def forward_email(self):
        selected_items = self.email_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an email to forward")
            return
        
        row = selected_items[0].row()
        email = self.emails[row]
        
        dialog = ComposeEmailDialog(self,token=self.token)
        dialog.subject_field.setText(f"FW: {email['subject']}")
        dialog.message_field.setText(f"\n\n-------- Forwarded Message --------\nFrom: {email['from']}\nDate: {email['date']}\nSubject: {email['subject']}\n\n{email['body']}")
        dialog.exec()
    
    def delete_email(self):
        selected_items = self.email_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an email to delete")
            return
        
        row = selected_items[0].row()
        
        # Remove from table
        self.email_table.removeRow(row)
        
        # Remove from data
        if row < len(self.emails):
            del self.emails[row]
        
        # Clear preview
        self.email_subject.setText("Select an email to preview")
        self.email_from.setText("")
        self.email_date.setText("")
        self.email_body.setText("")


class ComposeEmailDialog(QDialog):
    def __init__(self, token,parent=None):
        super().__init__(parent)
        self.token=token
        self.setWindowTitle("Compose Email")
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: black;
            }
            QLineEdit, QTextEdit {
                color: black;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        # Email form
        form_layout = QFormLayout()
        
        self.to_field = QLineEdit()
        self.cc_field = QLineEdit()
        self.bcc_field = QLineEdit()
        self.subject_field = QLineEdit()
        
        # Create labels with proper styling
        to_label = QLabel("To:")
        cc_label = QLabel("Cc:")
        bcc_label = QLabel("Bcc:")
        subject_label = QLabel("Subject:")
        
        form_layout.addRow(to_label, self.to_field)
        form_layout.addRow(cc_label, self.cc_field)
        form_layout.addRow(bcc_label, self.bcc_field)
        form_layout.addRow(subject_label, self.subject_field)
        
        layout.addLayout(form_layout)
        
        # Message body
        message_label = QLabel("Message:")
        layout.addWidget(message_label)
        
        self.message_field = QTextEdit()
        layout.addWidget(self.message_field)
        
        # Attachments
        attachments_container = QWidget()
        attachments_layout = QHBoxLayout(attachments_container)
        attachments_layout.setContentsMargins(0, 0, 0, 0)
        
        self.attachments_list = QListWidget()
        self.attachments_list.setStyleSheet("color: black;")
        attachments_layout.addWidget(self.attachments_list)
        
        attach_btn = QPushButton("Attach File")
        attach_btn.clicked.connect(self.attach_file)
        attachments_layout.addWidget(attach_btn)
        
        attachments_label = QLabel("Attachments:")
        layout.addWidget(attachments_label)
        layout.addWidget(attachments_container)
        
        # Buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: black;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        send_btn.clicked.connect(self.send_email)
        
        save_draft_btn = QPushButton("Save Draft")
        save_draft_btn.clicked.connect(self.save_draft)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(send_btn)
        buttons_layout.addWidget(save_draft_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addWidget(buttons_container)
    
    def attach_file(self):
        try:
            
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            if file_dialog.exec():
                for file_path in file_dialog.selectedFiles():
                    if os.path.exists(file_path):
                        item = QListWidgetItem(os.path.basename(file_path))
                        item.setData(Qt.ItemDataRole.UserRole, file_path)
                        self.attachments_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Attachment Error", f"Could not attach file: {str(e)}")
                   
    
    def send_email(self):
        # Validate required fields
        if not self.to_field.text():
            QMessageBox.warning(self, "Error", "Please specify at least one recipient")
            return
        try:
            # Prepare the email data
            data = {
                "recipient_email": self.to_field.text(),
                "subject": self.subject_field.text(),
                "body": self.message_field.toPlainText(),
                "cc": self.cc_field.text(),
                "bcc": self.bcc_field.text()
            }
            files = []
            for i in range(self.attachments_list.count()):
                item = self.attachments_list.item(i)
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if os.path.exists(file_path):
                    files.append(('attachments', (
                        os.path.basename(file_path),
                        open(file_path, 'rb'),
                        'application/octet-stream'
                )))
            
            # Get the parent EmailPage to access the token
            
            if hasattr(self, 'token'):
                headers = {"Authorization": f"Token {self.token}"}
                response = requests.post(
                    f"http://localhost:8000/api/notifications/email/send/",
                    headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'multipart/form-data'
                
            },
                    data=data,
                    files=files
                )
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Email sent successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to send email: {response.text}")
            else:
                QMessageBox.warning(self, "Error", "Authentication token not available")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
        finally:
            for _, file_tuple in files:
                file_tuple[1].close()

        
       
    def save_draft(self):
        # In a real app, this would save the email as a draft
        try:
            draft_data = {
            "recipient_email": self.to_field.text(),
            "subject": self.subject_field.text(),
            "body": self.message_field.toPlainText(),
            "cc": self.cc_field.text(),
            "bcc": self.bcc_field.text()
        }
            response = requests.post(
                f"http://localhost:8000/api/notifications/emails/draft/save/",
                headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'multipart/form-data'
            },
                data=draft_data
            )
            if response.status_code==200:
                QMessageBox.information(self, "Success", "Email saved as draft!")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save draft: {str(e)}")
        finally:
            self.accept()
    def load_drafts(self):
        """Load drafts from backend"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(
                "http://localhost:8000/api/notifications/emails/drafts/",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load drafts: {str(e)}")
            return []
"""'''