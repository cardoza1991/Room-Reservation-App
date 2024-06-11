from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import time
from datetime import datetime, timedelta
import sqlite3

class RoomReservationApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()
        self.loadBuildings()

    def initUI(self):
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle('Room Reservation App')

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Segoe UI, sans-serif;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QComboBox, QSpinBox, QLineEdit, QTimeEdit, QDateEdit, QPushButton, QListWidget {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QListWidget::item {
                padding: 10px;
            }
        """)

        self.rooms = {}
        self.currentRoom = None
        self.currentBuilding = None

        # Main layout
        mainLayout = QtWidgets.QVBoxLayout(self)

        # Real-time clock display
        self.clockLabel = QtWidgets.QLabel(self)
        mainLayout.addWidget(self.clockLabel, alignment=QtCore.Qt.AlignRight)

        # Building Selection
        self.buildingCombo = QtWidgets.QComboBox()
        self.buildingCombo.currentIndexChanged.connect(self.loadRooms)
        mainLayout.addWidget(QtWidgets.QLabel("Building:"))
        mainLayout.addWidget(self.buildingCombo)

        # Filtering Options
        filterLayout = QtWidgets.QHBoxLayout()

        self.floorCombo = QtWidgets.QComboBox()
        self.floorCombo.addItems(["Any", "1", "2", "3"])
        self.floorCombo.currentIndexChanged.connect(self.filterRooms)
        filterLayout.addWidget(QtWidgets.QLabel("Floor:"))
        filterLayout.addWidget(self.floorCombo)

        self.capacitySpin = QtWidgets.QSpinBox()
        self.capacitySpin.setRange(0, 100)
        self.capacitySpin.setValue(0)
        self.capacitySpin.valueChanged.connect(self.filterRooms)
        filterLayout.addWidget(QtWidgets.QLabel("Capacity:"))
        filterLayout.addWidget(self.capacitySpin)

        self.featuresCombo = QtWidgets.QComboBox()
        self.featuresCombo.addItems(["Any", "Audio", "Display", "Video"])
        self.featuresCombo.currentIndexChanged.connect(self.filterRooms)
        filterLayout.addWidget(QtWidgets.QLabel("Features:"))
        filterLayout.addWidget(self.featuresCombo)

        mainLayout.addLayout(filterLayout)

        # Room List
        self.roomList = QtWidgets.QListWidget()
        mainLayout.addWidget(self.roomList)

        # Buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        
        self.createBuildingButton = QtWidgets.QPushButton('Create Building', self)
        self.createBuildingButton.clicked.connect(self.createBuilding)
        buttonLayout.addWidget(self.createBuildingButton)

        self.createRoomButton = QtWidgets.QPushButton('Create Room', self)
        self.createRoomButton.clicked.connect(self.openCreateRoomDialog)
        buttonLayout.addWidget(self.createRoomButton)

        self.reserveRoomButton = QtWidgets.QPushButton('Reserve Room', self)
        self.reserveRoomButton.clicked.connect(self.enableRoomReservation)
        buttonLayout.addWidget(self.reserveRoomButton)

        self.viewReservationsButton = QtWidgets.QPushButton('View Reservations', self)
        self.viewReservationsButton.clicked.connect(self.openViewReservationsDialog)
        buttonLayout.addWidget(self.viewReservationsButton)

        self.deleteRoomsButton = QtWidgets.QPushButton('Delete Rooms', self)
        self.deleteRoomsButton.clicked.connect(self.openDeleteRoomsDialog)
        buttonLayout.addWidget(self.deleteRoomsButton)

        self.saveButton = QtWidgets.QPushButton('Save', self)
        self.saveButton.clicked.connect(self.saveState)
        buttonLayout.addWidget(self.saveButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.show()

        # Move the call to updateClock here after the UI is initialized
        self.updateClock()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateClock)
        self.timer.start(1000)

    def initDB(self):
        self.conn = sqlite3.connect('rooms.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                name TEXT,
                building_id INTEGER,
                floor INTEGER,
                capacity INTEGER,
                features TEXT,
                FOREIGN KEY(building_id) REFERENCES buildings(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY,
                room_id INTEGER,
                start_time TEXT,
                end_time TEXT,
                teacher_name TEXT,
                student_name TEXT,
                purpose TEXT,
                FOREIGN KEY(room_id) REFERENCES rooms(id)
            )
        ''')
        self.conn.commit()

    def loadBuildings(self):
        self.buildingCombo.clear()
        self.buildingCombo.addItem("Select Building")
        self.cursor.execute('SELECT * FROM buildings')
        for row in self.cursor.fetchall():
            building_id, name = row
            self.buildingCombo.addItem(name, userData=building_id)
        self.loadRooms()

    def loadRooms(self):
        self.rooms.clear()
        self.roomList.clear()
        self.currentBuilding = self.buildingCombo.currentData()
        if self.currentBuilding:
            self.cursor.execute('SELECT * FROM rooms WHERE building_id=?', (self.currentBuilding,))
            for row in self.cursor.fetchall():
                room_id, name, building_id, floor, capacity, features = row
                self.rooms[name] = {
                    'id': room_id,
                    'building_id': building_id,
                    'floor': floor,
                    'capacity': capacity,
                    'features': features.split(","),
                    'status': 'vacant',
                    'label': name,
                    'reserved_slots': []
                }
            self.loadReservations()
            self.filterRooms()

    def loadReservations(self):
        self.cursor.execute('SELECT * FROM reservations')
        for row in self.cursor.fetchall():
            res_id, room_id, start_time, end_time, teacher_name, student_name, purpose = row
            for room in self.rooms.values():
                if room['id'] == room_id:
                    room['reserved_slots'].append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'teacher_name': teacher_name,
                        'student_name': student_name,
                        'purpose': purpose
                    })
                    break

    def saveState(self):
        self.conn.commit()
        print("State saved to database.")

    def updateClock(self):
        currentTime = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        self.clockLabel.setText(currentTime)
        self.checkReservations(currentTime)

    def filterRooms(self):
        self.roomList.clear()
        building = self.buildingCombo.currentText()
        floor = self.floorCombo.currentText()
        capacity = self.capacitySpin.value()
        features = self.featuresCombo.currentText()

        for room, info in self.rooms.items():
            if building != "Any" and info['building_id'] != self.currentBuilding:
                continue
            if floor != "Any" and str(info['floor']) != floor:
                continue
            if capacity != 0 and info['capacity'] < capacity:
                continue
            if features != "Any" and features not in info['features']:
                continue
            roomItem = QtWidgets.QListWidgetItem(f"{info['label']} - {'vacant' if info['status'] == 'vacant' else 'occupied'}")
            self.roomList.addItem(roomItem)

    def checkReservations(self, currentTime):
        current_time = datetime.strptime(currentTime, '%Y-%m-%d %H:%M')
        for room, info in self.rooms.items():
            reserved_slots = info.get('reserved_slots', [])
            is_occupied = any(
                datetime.strptime(slot['start_time'], '%Y-%m-%d %H:%M') <= current_time < datetime.strptime(slot['end_time'], '%Y-%m-%d %H:%M')
                for slot in reserved_slots
            )
            info['status'] = 'occupied' if is_occupied else 'vacant'
        self.filterRooms()

    def createBuilding(self):
        building_name, ok = QtWidgets.QInputDialog.getText(self, 'Create Building', 'Enter building name:')
        if ok and building_name:
            self.cursor.execute('INSERT INTO buildings (name) VALUES (?)', (building_name,))
            self.conn.commit()
            self.loadBuildings()

    def openCreateRoomDialog(self):
        if not self.currentBuilding:
            QtWidgets.QMessageBox.warning(self, "No Building Selected", "Please select a building to create a room.")
            return
        dialog = CreateRoomDialog(self.currentBuilding, self)
        dialog.exec_()
        self.loadRooms()

    def enableRoomReservation(self):
        if not self.rooms:
            QtWidgets.QMessageBox.warning(self, "No Rooms Available", "Please create a room first.")
            return

        dialog = ReserveRoomDialog(self.rooms, self)
        dialog.exec_()
        self.loadReservations()
        self.filterRooms()
        print("Room reservation enabled.")

    def reserveRoom(self, room, date, start_time, end_time, teacher_name, student_name, purpose):
        room_id = self.rooms[room]['id']
        start_datetime = f"{date} {start_time}"
        end_datetime = f"{date} {end_time}"

        # Convert the start and end times to 24-hour format before storing
        start_time_24 = datetime.strptime(start_datetime, '%Y-%m-%d %I:%M %p').strftime('%Y-%m-%d %H:%M')
        end_time_24 = datetime.strptime(end_datetime, '%Y-%m-%d %I:%M %p').strftime('%Y-%m-%d %H:%M')

        self.cursor.execute('''
            INSERT INTO reservations (room_id, start_time, end_time, teacher_name, student_name, purpose)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (room_id, start_time_24, end_time_24, teacher_name, student_name, purpose))
        self.conn.commit()
        self.loadReservations()
        self.filterRooms()
        print(f"Room '{room}' reserved from {start_datetime} to {end_datetime}.")

    def deleteRoom(self):
        selected_room_item = self.roomList.currentItem()
        if selected_room_item:
            selected_room_text = selected_room_item.text()
            room_name = selected_room_text.split(' - ')[0]

            confirmation = QtWidgets.QMessageBox.question(self, "Delete Room", f"Are you sure you want to delete the room '{room_name}'?",
                                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if confirmation == QtWidgets.QMessageBox.Yes:
                room_id = self.rooms[room_name]['id']
                self.cursor.execute('DELETE FROM reservations WHERE room_id=?', (room_id,))
                self.cursor.execute('DELETE FROM rooms WHERE id=?', (room_id,))
                self.conn.commit()
                self.loadRooms()
                QtWidgets.QMessageBox.information(self, "Room Deleted", f"The room '{room_name}' has been deleted.")
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a room to delete.")

    def openDeleteRoomsDialog(self):
        dialog = DeleteRoomsDialog(self.rooms, self)
        dialog.exec_()
        self.loadRooms()

    def openViewReservationsDialog(self):
        dialog = ViewReservationsDialog(self)
        dialog.exec_()

class CreateRoomDialog(QtWidgets.QDialog):
    def __init__(self, building_id, parent=None):
        super().__init__(parent)
        self.building_id = building_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Create Room")
        layout = QtWidgets.QFormLayout(self)

        self.roomName = QtWidgets.QLineEdit(self)
        self.floor = QtWidgets.QSpinBox(self)
        self.floor.setRange(1, 10)
        self.capacity = QtWidgets.QSpinBox(self)
        self.capacity.setRange(1, 100)
        self.features = QtWidgets.QLineEdit(self)

        layout.addRow("Room Name:", self.roomName)
        layout.addRow("Floor:", self.floor)
        layout.addRow("Capacity:", self.capacity)
        layout.addRow("Features (comma separated):", self.features)

        self.createButton = QtWidgets.QPushButton("Create", self)
        self.createButton.clicked.connect(self.createRoom)
        layout.addWidget(self.createButton)

        self.setLayout(layout)

    def createRoom(self):
        room_name = self.roomName.text()
        floor = self.floor.value()
        capacity = self.capacity.value()
        features = self.features.text()

        if room_name:
            conn = sqlite3.connect('rooms.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rooms (name, building_id, floor, capacity, features)
                VALUES (?, ?, ?, ?, ?)
            ''', (room_name, self.building_id, floor, capacity, features))
            conn.commit()
            conn.close()
            self.accept()

class ReserveRoomDialog(QtWidgets.QDialog):
    def __init__(self, rooms, parent=None):
        super().__init__(parent)
        self.rooms = rooms
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Reserve Room")
        layout = QtWidgets.QFormLayout(self)

        self.roomCombo = QtWidgets.QComboBox(self)
        for room in self.rooms:
            self.roomCombo.addItem(room)

        self.dateEdit = QtWidgets.QDateEdit(self)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())

        self.startTimeEdit = QtWidgets.QTimeEdit(self)
        self.startTimeEdit.setDisplayFormat("hh:mm AP")

        self.endTimeEdit = QtWidgets.QTimeEdit(self)
        self.endTimeEdit.setDisplayFormat("hh:mm AP")

        self.teacherName = QtWidgets.QLineEdit(self)
        self.studentName = QtWidgets.QLineEdit(self)
        self.purpose = QtWidgets.QLineEdit(self)

        layout.addRow("Room:", self.roomCombo)
        layout.addRow("Date:", self.dateEdit)
        layout.addRow("Start Time:", self.startTimeEdit)
        layout.addRow("End Time:", self.endTimeEdit)
        layout.addRow("Name of Teacher:", self.teacherName)
        layout.addRow("Student:", self.studentName)
        layout.addRow("Purpose:", self.purpose)

        self.submitButton = QtWidgets.QPushButton("Submit", self)
        self.submitButton.clicked.connect(self.submitForm)
        layout.addWidget(self.submitButton)

        self.setLayout(layout)

    def submitForm(self):
        room = self.roomCombo.currentText()
        date = self.dateEdit.date().toString('yyyy-MM-dd')
        start_time = self.startTimeEdit.time().toString('hh:mm AP')
        end_time = self.endTimeEdit.time().toString('hh:mm AP')
        teacher_name = self.teacherName.text()
        student_name = self.studentName.text()
        purpose = self.purpose.text()

        if room and date and start_time and end_time and teacher_name and student_name and purpose:
            self.parent().reserveRoom(room, date, start_time, end_time, teacher_name, student_name, purpose)
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Incomplete Data", "Please fill all fields.")

class ViewReservationsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.loadReservations()

    def initUI(self):
        self.setWindowTitle("Current Reservations")
        self.layout = QtWidgets.QVBoxLayout(self)

        self.reservationsTable = QtWidgets.QTableWidget(self)
        self.reservationsTable.setColumnCount(6)
        self.reservationsTable.setHorizontalHeaderLabels(["Room", "Start Time", "End Time", "Teacher", "Student", "Purpose"])
        self.layout.addWidget(self.reservationsTable)

        self.deleteButton = QtWidgets.QPushButton("Delete Selected", self)
        self.deleteButton.clicked.connect(self.deleteReservation)
        self.layout.addWidget(self.deleteButton)

        self.setLayout(self.layout)

    def loadReservations(self):
        self.parent().cursor.execute('SELECT rooms.name, start_time, end_time, teacher_name, student_name, purpose FROM reservations JOIN rooms ON reservations.room_id = rooms.id')
        reservations = self.parent().cursor.fetchall()
        self.reservationsTable.setRowCount(len(reservations))

        for row_num, row_data in enumerate(reservations):
            for col_num, data in enumerate(row_data):
                if col_num == 1 or col_num == 2:
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M').strftime('%I:%M %p')
                self.reservationsTable.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(data))

    def deleteReservation(self):
        selected_row = self.reservationsTable.currentRow()
        if selected_row >= 0:
            room_name = self.reservationsTable.item(selected_row, 0).text()
            start_time = self.reservationsTable.item(selected_row, 1).text()
            start_time_24 = datetime.strptime(start_time, '%I:%M %p').strftime('%H:%M')
            start_datetime = f"{datetime.now().strftime('%Y-%m-%d')} {start_time_24}"
            self.parent().cursor.execute('''
                DELETE FROM reservations
                WHERE room_id = (SELECT id FROM rooms WHERE name = ?) AND start_time = ?
            ''', (room_name, start_datetime))
            self.parent().conn.commit()
            self.loadReservations()
            self.parent().loadReservations()
            self.parent().filterRooms()
            QtWidgets.QMessageBox.information(self, "Deleted", "The reservation has been deleted.")
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a reservation to delete.")

class DeleteRoomsDialog(QtWidgets.QDialog):
    def __init__(self, rooms, parent=None):
        super().__init__(parent)
        self.rooms = rooms
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Delete Rooms")
        layout = QtWidgets.QVBoxLayout(self)

        self.checkboxes = {}
        for room in self.rooms:
            checkbox = QtWidgets.QCheckBox(room, self)
            layout.addWidget(checkbox)
            self.checkboxes[room] = checkbox

        self.deleteButton = QtWidgets.QPushButton("Delete Selected", self)
        self.deleteButton.clicked.connect(self.deleteSelectedRooms)
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)

    def deleteSelectedRooms(self):
        for room, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                room_id = self.rooms[room]['id']
                self.parent().cursor.execute('DELETE FROM reservations WHERE room_id=?', (room_id,))
                self.parent().cursor.execute('DELETE FROM rooms WHERE id=?', (room_id,))
        self.parent().conn.commit()
        QtWidgets.QMessageBox.information(self, "Rooms Deleted", "The selected rooms have been deleted.")
        self.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = RoomReservationApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


