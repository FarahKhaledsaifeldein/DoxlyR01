from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QComboBox, QFrame,
                             QTabWidget, QGridLayout, QDateEdit, QCheckBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPainter, QPen, QColor
import random

# Mock chart widget for demonstration
class ChartWidget(QFrame):
    def __init__(self, chart_type="bar", title="Chart", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.title = title
        self.data = self.generate_random_data()
        self.setMinimumSize(400, 300)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        """)
    
    def generate_random_data(self):
        # Generate random data for demonstration
        if self.chart_type == "bar" or self.chart_type == "line":
            return [random.randint(10, 100) for _ in range(6)]
        elif self.chart_type == "pie":
            return [random.randint(10, 30) for _ in range(4)]
        return [random.randint(10, 100) for _ in range(6)]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw title
        painter.drawText(10, 20, self.title)
        
        # Draw chart based on type
        if self.chart_type == "bar":
            self.draw_bar_chart(painter)
        elif self.chart_type == "line":
            self.draw_line_chart(painter)
        elif self.chart_type == "pie":
            self.draw_pie_chart(painter)
    
    def draw_bar_chart(self, painter):
        width = self.width() - 40
        height = self.height() - 60
        bar_width = width / (len(self.data) * 2)
        max_value = max(self.data) if self.data else 1
        
        # Draw axes
        painter.setPen(QPen(QColor("#2c3e50"), 2))
        painter.drawLine(30, height + 30, width + 30, height + 30)  # x-axis
        painter.drawLine(30, 30, 30, height + 30)  # y-axis
        
        # Draw bars
        for i, value in enumerate(self.data):
            bar_height = (value / max_value) * height
            x = 30 + (i * bar_width * 2) + bar_width / 2
            y = height + 30 - bar_height
            
            # Draw bar
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3498db"))
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
            
            # Draw value
            painter.setPen(QColor("#2c3e50"))
            painter.drawText(int(x), int(y - 5), str(value))
            
            # Draw label
            painter.drawText(int(x), int(height + 45), f"Item {i+1}")
    
    def draw_line_chart(self, painter):
        width = self.width() - 40
        height = self.height() - 60
        point_width = width / (len(self.data) - 1) if len(self.data) > 1 else width
        max_value = max(self.data) if self.data else 1
        
        # Draw axes
        painter.setPen(QPen(QColor("#2c3e50"), 2))
        painter.drawLine(30, height + 30, width + 30, height + 30)  # x-axis
        painter.drawLine(30, 30, 30, height + 30)  # y-axis
        
        # Draw line
        painter.setPen(QPen(QColor("#e74c3c"), 2))
        
        for i in range(len(self.data) - 1):
            x1 = 30 + (i * point_width)
            y1 = height + 30 - (self.data[i] / max_value) * height
            x2 = 30 + ((i + 1) * point_width)
            y2 = height + 30 - (self.data[i + 1] / max_value) * height
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
            # Draw points
            painter.setBrush(QColor("#e74c3c"))
            painter.drawEllipse(int(x1) - 3, int(y1) - 3, 6, 6)
        
        # Draw last point
        if self.data:
            x = 30 + ((len(self.data) - 1) * point_width)
            y = height + 30 - (self.data[-1] / max_value) * height
            painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
    
    def draw_pie_chart(self, painter):
        width = self.width() - 40
        height = self.height() - 60
        radius = min(width, height) / 2
        center_x = width / 2 + 20
        center_y = height / 2 + 30
        
        total = sum(self.data)
        start_angle = 0
        
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
        
        for i, value in enumerate(self.data):
            # Calculate angles
            angle = (value / total) * 360 * 16  # QPainter uses 1/16th of a degree
            
            # Draw pie slice
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(colors[i % len(colors)]))
            painter.drawPie(int(center_x - radius), int(center_y - radius), 
                           int(radius * 2), int(radius * 2), 
                           int(start_angle), int(angle))
            
            # Update start angle for next slice
            start_angle += angle
            
            # Draw legend
            legend_y = 50 + i * 20
            painter.fillRect(width - 80, legend_y, 15, 15, QColor(colors[i % len(colors)]))
            painter.setPen(QColor("#2c3e50"))
            painter.drawText(width - 60, legend_y + 12, f"Item {i+1}: {value}")


class AnalysisPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.username = username
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("Analysis and Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        # Filter section
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Date range
        date_label = QLabel("Date Range:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        # Project filter
        project_label = QLabel("Project:")
        self.project_combo = QComboBox()
        self.project_combo.addItem("All Projects")
        self.project_combo.addItems([f"Project {i}" for i in range(1, 6)])
        
        # Apply button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        apply_btn.clicked.connect(self.apply_filters)
        
        # Export button
        export_btn = QPushButton("Export Report")
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_report)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(project_label)
        filter_layout.addWidget(self.project_combo)
        filter_layout.addWidget(apply_btn)
        filter_layout.addWidget(export_btn)
        
        header_layout.addWidget(filter_widget)
        main_layout.addWidget(header)
        
        # Create tabs for different analysis views
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Summary cards
        summary_widget = QWidget()
        summary_layout = QHBoxLayout(summary_widget)
        
        # Create summary cards
        total_docs_card = self.create_summary_card("Total Documents", "256", "#3498db")
        active_projects_card = self.create_summary_card("Active Projects", "12", "#2ecc71")
        pending_tasks_card = self.create_summary_card("Pending Tasks", "18", "#e74c3c")
        recent_uploads_card = self.create_summary_card("Recent Uploads", "34", "#f39c12")
        
        summary_layout.addWidget(total_docs_card)
        summary_layout.addWidget(active_projects_card)
        summary_layout.addWidget(pending_tasks_card)
        summary_layout.addWidget(recent_uploads_card)
        
        overview_layout.addWidget(summary_widget)
        
        # Charts
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        
        # Create charts
        documents_by_type = ChartWidget(chart_type="bar", title="Documents by Type")
        activity_over_time = ChartWidget(chart_type="line", title="Activity Over Time")
        project_distribution = ChartWidget(chart_type="pie", title="Project Distribution")
        user_activity = ChartWidget(chart_type="bar", title="User Activity")
        
        charts_layout.addWidget(documents_by_type, 0, 0)
        charts_layout.addWidget(activity_over_time, 0, 1)
        charts_layout.addWidget(project_distribution, 1, 0)
        charts_layout.addWidget(user_activity, 1, 1)
        
        overview_layout.addWidget(charts_widget)
        
        # Documents tab
        documents_tab = QWidget()
        documents_layout = QVBoxLayout(documents_tab)
        
        # Document statistics
        doc_stats_widget = QWidget()
        doc_stats_layout = QHBoxLayout(doc_stats_widget)
        
        # Create document statistics cards
        uploads_card = self.create_summary_card("Uploads", "128", "#3498db")
        downloads_card = self.create_summary_card("Downloads", "96", "#2ecc71")
        shares_card = self.create_summary_card("Shares", "64", "#e74c3c")
        views_card = self.create_summary_card("Views", "320", "#f39c12")
        
        doc_stats_layout.addWidget(uploads_card)
        doc_stats_layout.addWidget(downloads_card)
        doc_stats_layout.addWidget(shares_card)
        doc_stats_layout.addWidget(views_card)
        
        documents_layout.addWidget(doc_stats_widget)
        
        # Document activity chart
        doc_activity_chart = ChartWidget(chart_type="line", title="Document Activity Over Time")
        documents_layout.addWidget(doc_activity_chart)
        
        # Document table
        self.doc_table = QTableWidget()
        self.doc_table.setColumnCount(5)
        self.doc_table.setHorizontalHeaderLabels(["Document Name", "Type", "Views", "Downloads", "Last Accessed"])
        self.doc_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Add sample data
        self.doc_table.setRowCount(5)
        doc_data = [
            ["Project Proposal.docx", "Word", "45", "12", "2023-09-15"],
            ["Budget.xlsx", "Excel", "32", "8", "2023-09-14"],
            ["Contract.pdf", "PDF", "28", "15", "2023-09-13"],
            ["Presentation.pptx", "PowerPoint", "20", "5", "2023-09-12"],
            ["Requirements.docx", "Word", "18", "3", "2023-09-11"]
        ]
        
        for i, row_data in enumerate(doc_data):
            for j, cell_data in enumerate(row_data):
                self.doc_table.setItem(i, j, QTableWidgetItem(cell_data))
        
        documents_layout.addWidget(self.doc_table)
        
        # User Activity tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        # User activity chart
        user_activity_chart = ChartWidget(chart_type="bar", title="User Activity by Action")
        users_layout.addWidget(user_activity_chart)
        
        # User table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["User", "Documents Created", "Documents Viewed", "Comments", "Last Active"])
        self.user_table.setStyleSheet(self.doc_table.styleSheet())
        
        # Add sample data
        self.user_table.setRowCount(5)
        user_data = [
            ["John Doe", "15", "45", "12", "2023-09-15"],
            ["Jane Smith", "12", "32", "8", "2023-09-14"],
            ["Bob Johnson", "8", "28", "15", "2023-09-13"],
            ["Alice Williams", "10", "20", "5", "2023-09-12"],
            [self.username, "18", "38", "9", "2023-09-15"]
        ]
        
        for i, row_data in enumerate(user_data):
            for j, cell_data in enumerate(row_data):
                self.user_table.setItem(i, j, QTableWidgetItem(cell_data))
        
        users_layout.addWidget(self.user_table)
        
        # Add tabs
        tabs.addTab(overview_tab, "Overview")
        tabs.addTab(documents_tab, "Document Analysis")
        tabs.addTab(users_tab, "User Activity")
        
        main_layout.addWidget(tabs)
    
    def create_summary_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 5px;
                border-left: 5px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def apply_filters(self):
        # In a real app, this would update the charts and tables based on the selected filters
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        project = self.project_combo.currentText()
        
        # For demonstration, just show a message
        print(f"Applying filters: Date range {start_date} to {end_date}, Project: {project}")
        
        # Regenerate random data for charts to simulate filter application
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QTabWidget):
                self.refresh_charts_in_tab_widget(widget)
    
    def refresh_charts_in_tab_widget(self, tab_widget):
        for i in range(tab_widget.count()):
            tab = tab_widget.widget(i)
            for j in range(tab.layout().count()):
                item = tab.layout().itemAt(j)
                if item and item.widget():
                    self.refresh_charts_in_widget(item.widget())
    
    def refresh_charts_in_widget(self, widget):
        if isinstance(widget, ChartWidget):
            widget.data = widget.generate_random_data()
            widget.update()
        elif widget.layout():
            for i in range(widget.layout().count()):
                item = widget.layout().itemAt(i)
                if item and item.widget():
                    self.refresh_charts_in_widget(item.widget())
    
    def export_report(self):
        # In a real app, this would generate a PDF or Excel report
        print("Exporting report...")
        
        # For demonstration, just show a message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Export Report", "Report exported successfully!")