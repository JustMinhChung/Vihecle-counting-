from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class LogTable(QTableWidget):
    """
    QTableWidget subclass configured to display counting logs
    with color-coded directions and action buttons to clip events.
    """
    clip_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["No.", "Timestamp", "Type", "ID", "Direction", "Action"])
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Table sizing policies
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(0, 45)   # No.
        self.setColumnWidth(1, 90)   # Timestamp
        self.setColumnWidth(2, 85)   # Class Type
        self.setColumnWidth(3, 55)   # Vehicle ID
        self.setColumnWidth(4, 75)   # Direction (In/Out)
        
        self.events = []

    def clear_logs(self):
        """
        Clears all logs in the grid.
        """
        self.setRowCount(0)
        self.events.clear()

    def add_log(self, event_data):
        """
        Appends a new event log entry to the table view.
        """
        self.events.append(event_data)
        row = self.rowCount()
        self.insertRow(row)
        
        # Column 0: Index Number
        num_item = QTableWidgetItem(str(row + 1))
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 0, num_item)
        
        # Column 1: Video Timestamp
        time_item = QTableWidgetItem(event_data['timestamp_str'])
        time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 1, time_item)
        
        # Column 2: Vehicle Type Class
        class_item = QTableWidgetItem(event_data['class_name'])
        class_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 2, class_item)
        
        # Column 3: Tracker ID
        id_item = QTableWidgetItem(str(event_data['id']))
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 3, id_item)
        
        # Column 4: Direction (colored dynamically)
        dir_item = QTableWidgetItem(event_data['direction'])
        dir_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if event_data['direction'] == 'In':
            dir_item.setForeground(QColor("#10B981"))  # Green
        else:
            dir_item.setForeground(QColor("#EF4444"))  # Red
        self.setItem(row, 4, dir_item)
        
        # Column 5: Action Button to clip this event
        btn = QPushButton("Save Clip")
        btn.setObjectName("action_btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use a lambda closure to capture the event_data dictionary
        btn.clicked.connect(lambda checked=False, data=event_data: self.clip_requested.emit(data))
        
        # Wrap button in a QWidget to center align it in the cell
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(btn)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setLayout(layout)
        
        self.setCellWidget(row, 5, container)
        
        # Auto-scroll to the latest log item
        self.scrollToBottom()
