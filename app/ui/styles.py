DARK_THEME_STYLE = """
/* Global Window Theme */
QMainWindow {
    background-color: #12141C;
}

QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* ToolBar Styling */
QToolBar {
    background-color: #1A1D29;
    border-bottom: 1px solid #2D3142;
    spacing: 8px;
    padding: 6px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
    color: #94A3B8;
}

QToolButton:hover {
    background-color: #2D3142;
    color: #F8FAFC;
    border: 1px solid #3E445E;
}

QToolButton:pressed {
    background-color: #0F172A;
}

QToolButton:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #0EA5E9;
}

/* Sidebar & Box Widgets styling */
QFrame#sidebar {
    background-color: #1A1D29;
    border-left: 1px solid #2D3142;
    padding: 10px;
}

QGroupBox {
    border: 1px solid #2D3142;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    color: #F1F5F9;
    background-color: #1E2230;
    padding: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

/* Buttons */
QPushButton {
    background-color: #0EA5E9;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #38BDF8;
}

QPushButton:pressed {
    background-color: #0284C7;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748B;
}

QPushButton#secondary_btn {
    background-color: #334155;
    color: #E2E8F0;
}

QPushButton#secondary_btn:hover {
    background-color: #475569;
}

QPushButton#action_btn {
    background-color: #10B981; /* Emerald green */
}

QPushButton#action_btn:hover {
    background-color: #34D399;
}

/* Input Fields & Spinboxes */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #F8FAFC;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #0EA5E9;
}

/* Logs and Tables */
QTableWidget {
    background-color: #131520;
    border: 1px solid #2D3142;
    border-radius: 8px;
    gridline-color: #2D3142;
    color: #E2E8F0;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #334155;
    color: #0EA5E9;
}

QHeaderView::section {
    background-color: #1E2230;
    color: #94A3B8;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2D3142;
    font-weight: 600;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1D29;
    border-top: 1px solid #2D3142;
    color: #64748B;
}

/* Custom Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #0F172A;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Quick Stat Counters */
QLabel#stat_val_in {
    font-size: 32px;
    font-weight: bold;
    color: #10B981; /* green */
}

QLabel#stat_val_out {
    font-size: 32px;
    font-weight: bold;
    color: #EF4444; /* red */
}

QLabel#stat_lbl {
    font-size: 11px;
    color: #64748B;
    text-transform: uppercase;
    font-weight: 600;
}
"""
