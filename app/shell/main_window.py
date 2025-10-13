from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QDialogButtonBox, QMessageBox, QHBoxLayout, QVBoxLayout, QFormLayout
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from pathlib import Path
from core import db

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		# Window setup
		self.setWindowTitle("Travel & Commute Time Logger")
		self.setFixedSize(1000, 400)
		self.screen = QApplication.primaryScreen().availableGeometry()
		self.move(int((self.screen.width() - self.width()) / 2), int((self.screen.height() - self.height()) / 2))
		self.showNormal()
		
		# Data storage
		self.tables = []
		
		# UI components initialization
		self.title = QLabel("TRAVEL & COMMUTE TIME LOGGER")
		self.title.setObjectName("title")
		self.table_selector = QComboBox()
		self.table_selector.setEnabled(False)
		self.create_table_btn = QPushButton("Create Table")
		self.rename_table_btn = QPushButton("Rename Table")
		self.rename_table_btn.setEnabled(False)
		self.delete_table_btn = QPushButton("Delete Table")
		self.delete_table_btn.setEnabled(False)
		self.table = QTableWidget()
		self.total_duration_display = QLabel("Total Duration Time:")
		self.average_duration_display = QLabel("Average Duration Time:")
		self.add_log_btn = QPushButton("Add Log")
		self.add_log_btn.setEnabled(False)
		self.delete_log_btn = QPushButton("Delete Log")
		self.delete_log_btn.setEnabled(False)
		self.clear_all_logs_btn = QPushButton("Clear All Logs")
		self.clear_all_logs_btn.setEnabled(False)
		
		# Layout setup
		table_selector_layout = QFormLayout()
		table_selector_layout.addRow("Table:", self.table_selector)

		table_manager_layout = QHBoxLayout()
		table_manager_layout.addLayout(table_selector_layout)
		table_manager_layout.addWidget(self.create_table_btn)
		table_manager_layout.addWidget(self.rename_table_btn)
		table_manager_layout.addWidget(self.delete_table_btn)

		duration_display_layout = QVBoxLayout()
		duration_display_layout.addWidget(self.total_duration_display)
		duration_display_layout.addWidget(self.average_duration_display)
		
		table_btn_layout = QVBoxLayout()
		table_btn_layout.addWidget(self.add_log_btn)
		table_btn_layout.addWidget(self.delete_log_btn)
		table_btn_layout.addWidget(self.clear_all_logs_btn)
		table_btn_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

		left_layout = QVBoxLayout()
		left_layout.addLayout(duration_display_layout)
		left_layout.addLayout(table_btn_layout)
		
		self.table_layout = QHBoxLayout()
		self.table_layout.addWidget(self.table, 5)
		self.table_layout.addLayout(left_layout, 1)
		
		general_layout = QVBoxLayout()
		general_layout.addWidget(self.title, 1, alignment=Qt.AlignmentFlag.AlignCenter)
		general_layout.addLayout(table_manager_layout, 2)
		general_layout.addLayout(self.table_layout, 5)
		
		main_layout = QWidget()
		main_layout.setLayout(general_layout)
		self.setCentralWidget(main_layout)
		
		# Signal connections
		self.table_selector.currentIndexChanged.connect(self.switch_table)
		self.create_table_btn.clicked.connect(self.open_child_create_table)
		self.rename_table_btn.clicked.connect(self.open_child_rename_table)
		self.delete_table_btn.clicked.connect(self.delete_table)
		self.add_log_btn.clicked.connect(self.open_child_add_log)
		self.delete_log_btn.clicked.connect(self.delete_log)
		self.clear_all_logs_btn.clicked.connect(self.clear_all_logs)

		self.load_stylesheet()
		self.load_from_database()

	def load_stylesheet(self):
		# Load and apply QSS stylesheet for UI styling
		qss_file_path = Path(__file__).resolve().parent.parent / "core" / "styles.qss"

		if qss_file_path.exists():
			with qss_file_path.open("r", encoding="utf-8") as f:
				file = f.read()
				app = QApplication.instance()
				app.setStyleSheet(file)
		
	def load_from_database(self):
		# Load logs from database and populate table with travel data
		logs = db.get_all_logs()

		if logs:
			# Create default table if none exists
			if not self.tables:
				self.create_default_table()
			
			current_table = self.tables[0]
			current_table.setSortingEnabled(False)
			current_table.setRowCount(0)
			
			# Populate table with database records
			for log in logs:
				row = current_table.rowCount()
				current_table.insertRow(row)
				
				log_id, origin, destination, mode, start, end, description = log
				
				# Parse database datetime format to display format
				start_dt = QDateTime.fromString(start, "yyyy-MM-dd hh:mm:ss")
				end_dt = QDateTime.fromString(end, "yyyy-MM-dd hh:mm:ss")
				
				start_dt_text = f"{start_dt.date().toString('yyyy, MMM d')} [{start_dt.time().toString('h:mm AP')}]"
				end_dt_text = f"{end_dt.date().toString('yyyy, MMM d')} [{end_dt.time().toString('h:mm AP')}]"
				duration_text = self.calculate_duration_per_log(start_dt, end_dt)
				
				# Store log ID in hidden column for database operations
				id_item = QTableWidgetItem(str(log_id))
				current_table.setItem(row, 0, id_item)
				current_table.setItem(row, 1, QTableWidgetItem(origin))
				current_table.setItem(row, 2, QTableWidgetItem(destination))
				current_table.setItem(row, 3, QTableWidgetItem(mode))
				
				# Set sortable data for proper table sorting
				start_item = QTableWidgetItem(start_dt_text)
				start_item.setData(Qt.ItemDataRole.UserRole, self.get_sortable_datetime(start_dt_text))
				end_item = QTableWidgetItem(end_dt_text)
				end_item.setData(Qt.ItemDataRole.UserRole, self.get_sortable_datetime(end_dt_text))
				duration_item = QTableWidgetItem(duration_text)
				duration_item.setData(Qt.ItemDataRole.UserRole, self.get_sortable_duration(duration_text))
				
				current_table.setItem(row, 4, start_item)
				current_table.setItem(row, 5, end_item)
				current_table.setItem(row, 6, duration_item)
				current_table.setItem(row, 7, QTableWidgetItem(description))
				
				# Make all cells non-editable for data integrity
				for col in range(current_table.columnCount()):
					item = current_table.item(row, col)

					if item:
						item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
			
			current_table.setSortingEnabled(True)
			
			# Update UI state based on data availability
			self.table_selector.setEnabled(True)
			self.rename_table_btn.setEnabled(True)
			self.delete_table_btn.setEnabled(True)
			self.add_log_btn.setEnabled(True)
			
			if len(logs) > 0:
				self.delete_log_btn.setEnabled(True)
				self.clear_all_logs_btn.setEnabled(True)
			
			# Calculate and display duration statistics
			total_duration, average_duration = self.calculate_total_and_average_duration()
			self.total_duration_display.setText(total_duration)
			self.average_duration_display.setText(average_duration)

	def create_default_table(self):
		# Create default table widget with predefined columns and settings
		new_table = QTableWidget(0, 8)
		new_table.setHorizontalHeaderLabels(["ID", "Origin", "Destination", "Mode", "Start Date/Time", "End Date/Time", "Duration", "Description"])
		new_table.setColumnHidden(0, True)  # Hide ID column for internal use
		new_table.setColumnWidth(1, 100)
		new_table.setColumnWidth(2, 100)
		new_table.setColumnWidth(3, 100)
		new_table.setColumnWidth(4, 139)
		new_table.setColumnWidth(5, 139)
		new_table.setColumnWidth(6, 160)
		new_table.setColumnWidth(7, 200)
		
		new_table.setWordWrap(True)
		new_table.resizeRowsToContents()
		new_table.setSortingEnabled(True)
		new_table.cellDoubleClicked.connect(self.open_child_edit_log)
		new_table.itemSelectionChanged.connect(self.activate_delete_log)
		
		self.tables.append(new_table)
		self.table_selector.addItem("Travel Logs")
		self.table_selector.setCurrentIndex(0)
		self.update_table(new_table)
		
	def switch_table(self):
		# Switch between different table views
		if self.tables:
			self.update_table(self.tables[self.table_selector.currentIndex()])

	def open_child_create_table(self):
		# Open dialog for creating new table
		self.open_child_create_table = ChildCreateTable(self)
		self.open_child_create_table.setModal(True)
		self.open_child_create_table.show()

	def open_child_rename_table(self):
		# Open dialog for renaming current table
		self.open_child_rename_table = ChildRenameTable(self)
		self.open_child_rename_table.setModal(True)
		self.open_child_rename_table.show()

	def update_table(self, new_table):
		# Update main display with new table widget
		self.table.setParent(None)
		self.table = new_table
		self.centralWidget().layout().itemAt(2).layout().insertWidget(0, self.table, 5)

		total_duration, average_duration = self.calculate_total_and_average_duration()
		self.total_duration_display.setText(total_duration)
		self.average_duration_display.setText(average_duration)
	
	def delete_table(self):
		# Delete current table after confirmation
		current_index = self.table_selector.currentIndex()

		confirm = QMessageBox.question(self, "Delete Table", f"Do you really want to continue deleting '{self.table_selector.currentText()}' table?\nAll of its logs cannot be recovered once deleted.")

		if confirm == QMessageBox.StandardButton.Yes:
			self.table_layout.removeWidget(self.table)
			self.tables.pop(current_index)
			self.table_selector.removeItem(current_index)

			if not self.tables:
				self.empty_table = QTableWidget()
				self.update_table(self.empty_table)

				total_duration, average_duration = self.calculate_total_and_average_duration()
				self.total_duration_display.setText(total_duration)
				self.average_duration_display.setText(average_duration)

				# Disable buttons when no tables exist
				self.table_selector.setEnabled(False)
				self.rename_table_btn.setEnabled(False)
				self.delete_table_btn.setEnabled(False)
				self.add_log_btn.setEnabled(False)
	
	def open_child_add_log(self):
		# Open dialog for adding new travel log
		self.open_child_add_log = ChildAddLog(self)
		self.open_child_add_log.setModal(True)
		self.open_child_add_log.show()

	def get_sortable_datetime(self, datetime_text):
		# Convert display datetime to sortable string format (yyyyMMddhhmm)
		datetime_parts = datetime_text.split("[")
		date_part = datetime_parts[0].strip()
		time_part = datetime_parts[1].rstrip("]").strip()
		
		date_object = QDate.fromString(date_part, "yyyy, MMM d")
		time_object = QTime.fromString(time_part, "h:mm AP")
		datetime_object = QDateTime(date_object, time_object)
		
		return datetime_object.toString("yyyyMMddhhmm")

	def get_sortable_duration(self, duration_text):
		# Convert duration text to sortable seconds format
		total_seconds = 0

		# Parse days component
		if 'day' in duration_text:
			days_part = duration_text.split('day')[0].strip()

			if '&' in days_part:
				days_part = days_part.split('&')[0].strip()

			if ',' in days_part:
				days_part = days_part.split(',')[0].strip()

			days = int(days_part)
			total_seconds += days * 86400
		
		# Parse hours component
		if 'hr' in duration_text:
			hours_part = duration_text.split('hr')[0]

			if '&' in hours_part:
				hours_part = hours_part.split('&')[-1].strip()
			elif ',' in hours_part:
				hours_part = hours_part.split(',')[-1].strip()
			else:
				parts = hours_part.split()
				hours = int(parts[-1]) if parts else 0
				total_seconds += hours * 3600

		# Parse minutes component
		if 'min' in duration_text:
			minutes_part = duration_text.split('min')[0]

			if '&' in minutes_part:
				minutes_part = minutes_part.split('&')[-1].strip()
			else:
				parts = minutes_part.split()
				minutes = int(parts[-1]) if parts else 0
				total_seconds += minutes * 60
				
		return str(total_seconds).zfill(10)  # Zero-pad for proper sorting

	def parse_datetime(self, datetime_text):
		# Parse display datetime text back to QDateTime object
		datetime_parts = datetime_text.split("[")
		date_part = datetime_parts[0].strip()
		time_part = datetime_parts[1].rstrip("]").strip()
		date_object = QDate.fromString(date_part, "yyyy, MMM d")
		time_object = QTime.fromString(time_part, "h:mm AP")
		return QDateTime(date_object, time_object)

	def calculate_duration_per_log(self, start_dt, end_dt):
		# Calculate duration between start and end datetime in human-readable format
		duration_seconds = start_dt.secsTo(end_dt)

		minutes = (duration_seconds // 60) % 60
		hours = (duration_seconds // 3600) % 24
		days = duration_seconds // 86400
		
		components = []
		
		if days > 0:
			components.append(f"{days} {'day' if days == 1 else 'days'}")
			
		if hours > 0:
			components.append(f"{hours} {'hr' if hours == 1 else 'hrs'}")
			
		if minutes > 0:
			components.append(f"{minutes} {'min' if minutes == 1 else 'mins'}")
		
		duration = self.format_duration_components(components)
		
		return duration
		
	def calculate_total_and_average_duration(self):
		# Calculate total and average duration across all logs in current table
		current_table_index = self.table_selector.currentIndex()

		if current_table_index < 0:
			return "Total Duration Time:", "Average Duration Time:"
			
		current_table = self.tables[current_table_index]
		log_count = current_table.rowCount()

		if log_count == 0:
			return "Total Duration Time:", "Average Duration Time:"
		
		total_seconds = 0
		
		# Sum durations from all logs
		for row in range(log_count):
			start_dt_text = current_table.item(row, 4).text()  # Start datetime column
			end_dt_text = current_table.item(row, 5).text()    # End datetime column
			
			start_dt = self.parse_datetime(start_dt_text)
			end_dt = self.parse_datetime(end_dt_text)
			
			total_seconds += start_dt.secsTo(end_dt)

		# Calculate time components for total duration
		total_minutes = (total_seconds // 60) % 60
		total_hours = (total_seconds // 3600) % 24
		total_days = total_seconds // 86400

		# Calculate time components for average duration
		average_seconds = total_seconds // log_count
		average_minutes = (average_seconds // 60) % 60
		average_hours = (average_seconds // 3600) % 24
		average_days = average_seconds // 86400

		total_components = []
		average_components = []

		# Build total duration components
		if total_days > 0:
			total_components.append(f"{total_days} {'day' if total_days == 1 else 'days'}")

		if total_hours > 0:
			total_components.append(f"{total_hours} {'hr' if total_hours == 1 else 'hrs'}")

		if total_minutes > 0:
			total_components.append(f"{total_minutes} {'min' if total_minutes == 1 else 'mins'}")

		# Build average duration components
		if average_days > 0:
			average_components.append(f"{average_days} {'day' if average_days == 1 else 'days'}")

		if average_hours > 0:
			average_components.append(f"{average_hours} {'hr' if average_hours == 1 else 'hrs'}")

		if average_minutes > 0:
			average_components.append(f"{average_minutes} {'min' if average_minutes == 1 else 'mins'}")
		
		total_duration = self.format_duration_components(total_components)
		average_duration = self.format_duration_components(average_components)

		# Format output based on log count
		if log_count == 1:
			return f"Total Duration Time:\n  {total_duration}", "Average Duration Time:"
		else:
			return f"Total Duration Time:\n  {total_duration}", f"Average Duration Time:\n  {average_duration}"

	def format_duration_components(self, components):
		# Format duration components with proper conjunction
		if len(components) == 1:
			return components[0]
		elif len(components) == 2:
			return f"{components[0]} & {components[1]}"
		else:
			return f"{components[0]}, {components[1]}, & {components[2]}"
	
	def open_child_edit_log(self, row, column):
		# Open dialog for editing existing log (double-click handler)
		if QApplication.activeModalWidget() is not None:
			return

		self.open_child_edit_log = ChildEditLog(self, row)
		self.open_child_edit_log.setModal(True)
		self.open_child_edit_log.show()
	
	def activate_delete_log(self):
		# Enable delete button when a log is selected
		selected_log = self.table.currentRow()
		self.delete_log_btn.setEnabled(selected_log >= 0)
	
	def delete_log(self):
		# Delete selected log after confirmation
		current_table = self.tables[self.table_selector.currentIndex()]
		current_log = current_table.currentRow()

		confirm = QMessageBox.question(self, "Delete Log", "Do you really want to delete this log?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

		if confirm == QMessageBox.StandardButton.Yes:
			# Get log ID from hidden column for database operation
			log_id = int(current_table.item(current_log, 0).text())
			
			# Delete from database
			db.delete_log(log_id)
			
			# Delete from UI
			current_table.removeRow(current_log)

			total_duration, average_duration = self.calculate_total_and_average_duration()
			self.total_duration_display.setText(total_duration)
			self.average_duration_display.setText(average_duration)

			# Disable buttons if no logs remain
			if current_table.rowCount() == 0:
				self.delete_log_btn.setEnabled(False)
				self.clear_all_logs_btn.setEnabled(False)

	def clear_all_logs(self):
		# Clear all logs in current table after confirmation
		confirm = QMessageBox.question(self, "Clear All Logs", f"Do you really want to clear all logs in '{self.table_selector.currentText()}' table?\nThey cannot be recovered once deleted.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

		if confirm == QMessageBox.StandardButton.Yes:
			current_table = self.tables[self.table_selector.currentIndex()]

			# Clear from database
			db.clear_all_logs()
			
			# Clear from UI
			current_table.setRowCount(0)

			total_duration, average_duration = self.calculate_total_and_average_duration()
			self.total_duration_display.setText(total_duration)
			self.average_duration_display.setText(average_duration)

			self.delete_log_btn.setEnabled(False)
			self.clear_all_logs_btn.setEnabled(False)

class ChildCreateTable(QDialog):
	def __init__(self, main_window):
		super().__init__(main_window)

		self.setWindowTitle("Create New Table")
		self.setFixedSize(200, 100)
		screen = main_window.screen
		self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

		self.main_window = main_window

		self.input = QLineEdit()
		self.error_prompt = QLabel()
		self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
		self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create")
		self.buttons.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

		layout = QFormLayout()
		layout.addRow("Table name:", self.input)
		
		main_layout = QVBoxLayout()
		main_layout.addLayout(layout)
		main_layout.addWidget(self.error_prompt, alignment=Qt.AlignmentFlag.AlignCenter)
		main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignCenter)
		self.setLayout(main_layout)

		self.buttons.rejected.connect(self.reject)
		self.buttons.accepted.connect(self.create)

	def create(self):
		# Validate and create new table
		if self.input.text():
			table_names = [self.main_window.table_selector.itemText(i) for i in range(len(self.main_window.tables))]
			
			if self.input.text() not in table_names:
				new_table = QTableWidget(0, 8)
				new_table.setHorizontalHeaderLabels(["ID", "Origin", "Destination", "Mode", "Start Date/Time", "End Date/Time", "Duration", "Description"])
				new_table.setColumnHidden(0, True)  # Hide ID column
				new_table.setColumnWidth(1, 100)
				new_table.setColumnWidth(2, 100)
				new_table.setColumnWidth(3, 100)
				new_table.setColumnWidth(4, 139)
				new_table.setColumnWidth(5, 139)
				new_table.setColumnWidth(6, 160)
				new_table.setColumnWidth(7, 200)
				
				new_table.setWordWrap(True)
				new_table.resizeRowsToContents()
				new_table.setSortingEnabled(True)
				new_table.cellDoubleClicked.connect(self.main_window.open_child_edit_log)
				new_table.itemSelectionChanged.connect(self.main_window.activate_delete_log)
				
				self.main_window.tables.append(new_table)
				self.main_window.table_selector.addItem(self.input.text())
				self.main_window.table_selector.setCurrentIndex(self.main_window.table_selector.count() - 1)
				self.main_window.update_table(new_table)
				
				# Enable table management buttons
				self.main_window.table_selector.setEnabled(True)
				self.main_window.rename_table_btn.setEnabled(True)
				self.main_window.delete_table_btn.setEnabled(True)
				self.main_window.add_log_btn.setEnabled(True)
				
				self.accept()
			else:
				self.error_prompt.setText(f"<font color='red'>* '{self.input.text()}' table already exists.</font>")
		else:
			self.error_prompt.setText("<font color='red'>* Table name is required.</font>")

class ChildRenameTable(QDialog):
	def __init__(self, main_window):
		super().__init__(main_window)

		self.setWindowTitle("Rename Table")
		self.setFixedSize(200, 100)
		screen = main_window.screen
		self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

		self.main_window = main_window

		self.input = QLineEdit()
		self.error_prompt = QLabel()
		self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
		self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Save")
		self.buttons.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

		layout = QFormLayout()
		layout.addRow("Table name:", self.input)

		main_layout = QVBoxLayout()
		main_layout.addLayout(layout)
		main_layout.addWidget(self.error_prompt, alignment=Qt.AlignmentFlag.AlignCenter)
		main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignCenter)
		self.setLayout(main_layout)

		self.buttons.rejected.connect(self.reject)
		self.buttons.accepted.connect(self.save)

	def save(self):
		# Validate and save table rename
		if not self.input.text():
			self.error_prompt.setText("<font color='red'>* Table name is required.</font>")
			return

		table_names = [self.main_window.table_selector.itemText(i) for i in range(len(self.main_window.tables))]
		current_table_name = self.main_window.table_selector.currentText()

		if self.input.text() in table_names and self.input.text() != current_table_name:
			self.error_prompt.setText(f"<font color='red'>* '{self.input.text()}' table already exists.</font>")
		else:
			self.main_window.table_selector.setItemText(self.main_window.table_selector.currentIndex(), self.input.text())
			self.accept()

class ChildAddLog(QDialog):
	def __init__(self, main_window):
		super().__init__(main_window)

		self.setWindowTitle("Add Log")
		self.setFixedWidth(325)
		self.setMinimumHeight(300)
		screen = main_window.screen
		self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

		self.main_window = main_window

		# Input fields with validation
		self.origin_input = QLineEdit()
		self.error_label1 = QLabel()
		self.error_label1.setVisible(False)
		self.destination_input = QLineEdit()
		self.error_label2 = QLabel()
		self.error_label2.setVisible(False)
		self.mode_input_cb = QComboBox()
		self.mode_input_cb.addItems(["Car", "Walk", "Bus", "Airplane", "Bicycle", "Other"])
		self.mode_input_le = QLineEdit()
		self.mode_input_le.setEnabled(False)
		self.mode_input_le.setVisible(False)
		self.error_label3 = QLabel()
		self.error_label3.setVisible(False)
		
		# DateTime inputs with current time defaults
		now = QDateTime.currentDateTime()
		self.start_date_input = QDateEdit()
		self.start_date_input.setDisplayFormat("yyyy/MM/d")
		self.start_date_input.setCalendarPopup(True)
		self.start_date_input.setDate(now.date())
		self.start_time_input = QTimeEdit()
		self.start_time_input.setTime(now.time())
		self.end_date_input = QDateEdit()
		self.end_date_input.setDisplayFormat("yyyy/MM/d")
		self.end_date_input.setCalendarPopup(True)
		self.end_date_input.setDate(now.addSecs(60).date())  # Default to 1 minute later
		self.end_time_input = QTimeEdit()
		self.end_time_input.setTime(now.addSecs(60).time())
		self.error_label4 = QLabel()
		self.error_label4.setVisible(False)
		self.description_input = QTextEdit()
		self.description_input.setFixedHeight(80)
		self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
		self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add")
		self.buttons.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
		
		# Layout organization
		start_input_layout = QHBoxLayout()
		start_input_layout.addWidget(self.start_date_input)
		start_input_layout.addWidget(self.start_time_input)
		
		end_input_layout = QHBoxLayout()
		end_input_layout.addWidget(self.end_date_input)
		end_input_layout.addWidget(self.end_time_input)

		fill_up_layout = QFormLayout()
		fill_up_layout.addRow("Origin:", self.origin_input)
		fill_up_layout.addRow("", self.error_label1)
		fill_up_layout.addRow("Destination:", self.destination_input)
		fill_up_layout.addRow("", self.error_label2)
		fill_up_layout.addRow("Mode:", self.mode_input_cb)
		fill_up_layout.addRow("", self.mode_input_le)
		fill_up_layout.addRow("", self.error_label3)
		fill_up_layout.addRow("Start Date/Time:", start_input_layout)
		fill_up_layout.addRow("End Date/Time:", end_input_layout)
		fill_up_layout.addRow("", self.error_label4)
		fill_up_layout.addRow("Description:\n(optional)", self.description_input)

		main_layout = QVBoxLayout()
		main_layout.addLayout(fill_up_layout)
		main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignLeft)
		self.setLayout(main_layout)

		# Signal connections
		self.mode_input_cb.currentIndexChanged.connect(self.combobox_other)
		self.start_time_input.timeChanged.connect(self.adjust_end_time)
		self.end_time_input.timeChanged.connect(self.adjust_start_time)
		self.buttons.rejected.connect(self.reject)
		self.buttons.accepted.connect(self.add)

	def combobox_other(self):
		# Show/hide custom mode input when "Other" is selected
		if self.mode_input_cb.currentIndex() != 5:
			self.mode_input_le.clear()
			self.mode_input_le.setEnabled(False)
			self.mode_input_le.setVisible(False)
		else:
			self.mode_input_le.setEnabled(True)
			self.mode_input_le.setVisible(True)
		
		self.update_dialog_height()

	def update_dialog_height(self):
		# Adjust dialog height based on content visibility
		self.setMinimumHeight(0)
		self.setMaximumHeight(450)
		self.adjustSize()

	def get_datetime_inputs(self):
		# Get combined datetime objects from date and time inputs
		start_dt = QDateTime(self.start_date_input.date(), self.start_time_input.time())
		end_dt = QDateTime(self.end_date_input.date(), self.end_time_input.time())
		return start_dt, end_dt

	def adjust_end_time(self):
		# Ensure end time is always after start time
		start_dt, end_dt = self.get_datetime_inputs()

		if start_dt >= end_dt:
			increment = start_dt.addSecs(60)
			self.end_date_input.setDate(increment.date())
			self.end_time_input.setTime(increment.time())
		
	def adjust_start_time(self):
		# Ensure start time is always before end time
		start_dt, end_dt = self.get_datetime_inputs()

		if end_dt <= start_dt:
			increment = end_dt.addSecs(-60)
			self.start_date_input.setDate(increment.date())
			self.start_time_input.setTime(increment.time())

	def add(self):
		# Validate inputs and add new log to database and UI

		# Origin validation
		if not self.origin_input.text():
			self.error_label1.setVisible(True)
			self.error_label1.setText("<font color='red'> * Origin is required.</font>")
		else:
			self.error_label1.setVisible(False)

		# Destination validation
		if not self.destination_input.text():
			self.error_label2.setVisible(True)
			self.error_label2.setText("<font color='red'> * Destination is required.</font>")
		else:
			self.error_label2.setVisible(False)

		# Mode validation for "Other" selection
		if self.mode_input_cb.currentText() == "Other" and not self.mode_input_le.text():
			self.error_label3.setVisible(True)
			self.error_label3.setText("<font color='red'> * Mode is required.</font>")
		else:
			self.error_label3.setVisible(False)

		# DateTime validation
		start_dt, end_dt = self.get_datetime_inputs()

		if start_dt >= end_dt:
			self.error_label4.setVisible(True)
			self.error_label4.setText("<font color='red'> * End date & time must be after start date & time.</font>")
			self.error_label4.setWordWrap(True)
		else:
			self.error_label4.setVisible(False)

		self.update_dialog_height()

		# Check if any validation errors exist
		errors = [self.error_label1.isVisible(), self.error_label2.isVisible(), 
				self.error_label3.isVisible(), self.error_label4.isVisible()]

		if any(errors):
			return

		# Prepare data for database insertion
		origin = self.origin_input.text()
		destination = self.destination_input.text()
		mode = self.mode_input_cb.currentText() if self.mode_input_cb.currentIndex() != 5 else self.mode_input_le.text()
		start = start_dt.toString("yyyy-MM-dd hh:mm:ss")
		end = end_dt.toString("yyyy-MM-dd hh:mm:ss")
		description = self.description_input.toPlainText()

		try:
			# Save to database and get generated log ID
			log_id = db.create_log(origin, destination, mode, start, end, description)
			
			# Update UI with new log
			current_table = self.main_window.tables[self.main_window.table_selector.currentIndex()]
			new_log = current_table.rowCount()
			current_table.setSortingEnabled(False)
			current_table.insertRow(new_log)

			current_table.blockSignals(True)

			# Store log data in table cells
			id_item = QTableWidgetItem(str(log_id))
			current_table.setItem(new_log, 0, id_item)
			current_table.setItem(new_log, 1, QTableWidgetItem(origin))
			current_table.setItem(new_log, 2, QTableWidgetItem(destination))
			current_table.setItem(new_log, 3, QTableWidgetItem(mode))
	
			# Format datetime for display
			start_dt_text = f"{self.start_date_input.date().toString('yyyy, MMM d')} [{self.start_time_input.time().toString('h:mm AP')}]"
			end_dt_text = f"{self.end_date_input.date().toString('yyyy, MMM d')} [{self.end_time_input.time().toString('h:mm AP')}]"
			duration_text = self.main_window.calculate_duration_per_log(start_dt, end_dt)

			# Create sortable table items
			start_item = QTableWidgetItem(start_dt_text)
			start_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_datetime(start_dt_text))
			end_item = QTableWidgetItem(end_dt_text)
			end_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_datetime(end_dt_text))
			duration_item = QTableWidgetItem(duration_text)
			duration_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_duration(duration_text))
			
			current_table.setItem(new_log, 4, start_item)
			current_table.setItem(new_log, 5, end_item)
			current_table.setItem(new_log, 6, duration_item)
			current_table.setItem(new_log, 7, QTableWidgetItem(description))

			current_table.setSortingEnabled(True)
			current_table.blockSignals(False)

			# Make all cells non-editable
			for col in range(current_table.columnCount()):
				item = current_table.item(new_log, col)

				if item:
					item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
			
			# Update duration statistics
			total_duration, average_duration = self.main_window.calculate_total_and_average_duration()
			self.main_window.total_duration_display.setText(total_duration)
			self.main_window.average_duration_display.setText(average_duration)

			self.main_window.delete_log_btn.setEnabled(False)
			self.main_window.clear_all_logs_btn.setEnabled(True)

			current_table.selectRow(new_log)
	
			self.accept()
			
		except ValueError as e:
			QMessageBox.warning(self, "Error", str(e))

class ChildEditLog(QDialog):
	def __init__(self, main_window, row):
		super().__init__(main_window)

		self.setWindowTitle("Edit Log")
		self.setFixedWidth(325)
		self.setMinimumHeight(300)
		screen = main_window.screen
		self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

		self.main_window = main_window
		self.current_log = row

		# Load existing log data for editing
		current_table = self.main_window.tables[self.main_window.table_selector.currentIndex()]
		log_id = int(current_table.item(self.current_log, 0).text())
		origin = current_table.item(self.current_log, 1).text()
		destination = current_table.item(self.current_log, 2).text()
		mode = current_table.item(self.current_log, 3).text()
		start_dt_text = current_table.item(self.current_log, 4).text()
		end_dt_text = current_table.item(self.current_log, 5).text()
		description = current_table.item(self.current_log, 7).text()

		start_dt = self.main_window.parse_datetime(start_dt_text)
		end_dt = self.main_window.parse_datetime(end_dt_text)

		self.log_id = log_id
		self.origin_input = QLineEdit(origin)
		self.error_label1 = QLabel()
		self.error_label1.setVisible(False)
		self.destination_input = QLineEdit(destination)
		self.error_label2 = QLabel()
		self.error_label2.setVisible(False)
		self.mode_input_cb = QComboBox()
		self.mode_input_cb.addItems(["Car", "Walk", "Bus", "Airplane", "Bicycle", "Other"])
		self.mode_input_le = QLineEdit()
		self.mode_input_le.setEnabled(False)
		self.mode_input_le.setVisible(False)
		self.error_label3 = QLabel()
		self.error_label3.setVisible(False)
		self.start_date_input = QDateEdit(start_dt.date())
		self.start_date_input.setDisplayFormat("yyyy/MM/d")
		self.start_date_input.setCalendarPopup(True)
		self.start_time_input = QTimeEdit(start_dt.time())
		self.start_time_input.setDisplayFormat("h:mm AP")
		self.end_date_input = QDateEdit(end_dt.date())
		self.end_date_input.setDisplayFormat("yyyy/MM/d")
		self.end_date_input.setCalendarPopup(True)
		self.end_time_input = QTimeEdit(end_dt.time())
		self.end_time_input.setDisplayFormat("h:mm AP")
		self.error_label4 = QLabel()
		self.error_label4.setVisible(False)
		self.description_input = QTextEdit(description)
		self.description_input.setFixedHeight(80)
		self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
		self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Save")
		self.buttons.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
		
		# Set current mode in combobox
		current_mode = self.mode_input_cb.findText(mode)

		if current_mode != -1:
			self.mode_input_cb.setCurrentIndex(current_mode)
		else:
			self.mode_input_cb.setCurrentIndex(5)
			self.mode_input_le.setEnabled(True)
			self.mode_input_le.setVisible(True)
			self.mode_input_le.setText(mode)
		
		# Layout organization
		start_input_layout = QHBoxLayout()
		start_input_layout.addWidget(self.start_date_input)
		start_input_layout.addWidget(self.start_time_input)
		
		end_input_layout = QHBoxLayout()
		end_input_layout.addWidget(self.end_date_input)
		end_input_layout.addWidget(self.end_time_input)

		fill_up_layout = QFormLayout()
		fill_up_layout.addRow("Origin:", self.origin_input)
		fill_up_layout.addRow("", self.error_label1)
		fill_up_layout.addRow("Destination:", self.destination_input)
		fill_up_layout.addRow("", self.error_label2)
		fill_up_layout.addRow("Mode:", self.mode_input_cb)
		fill_up_layout.addRow("", self.mode_input_le)
		fill_up_layout.addRow("", self.error_label3)
		fill_up_layout.addRow("Start Date/Time:", start_input_layout)
		fill_up_layout.addRow("End Date/Time:", end_input_layout)
		fill_up_layout.addRow("", self.error_label4)
		fill_up_layout.addRow("Description:\n(optional)", self.description_input)

		main_layout = QVBoxLayout()
		main_layout.addLayout(fill_up_layout)
		main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignLeft)
		self.setLayout(main_layout)

		# Signal connections
		self.mode_input_cb.currentIndexChanged.connect(self.combobox_other)
		self.start_time_input.timeChanged.connect(self.adjust_end_time)
		self.end_time_input.timeChanged.connect(self.adjust_start_time)
		self.buttons.rejected.connect(self.reject)
		self.buttons.accepted.connect(self.save)

	def combobox_other(self):
		# Show/hide custom mode input when "Other" is selected
		if self.mode_input_cb.currentIndex() != 5:
			self.mode_input_le.clear()
			self.mode_input_le.setEnabled(False)
			self.mode_input_le.setVisible(False)
		else:
			self.mode_input_le.setEnabled(True)
			self.mode_input_le.setVisible(True)
		
		self.update_dialog_height()

	def update_dialog_height(self):
		# Adjust dialog height based on content visibility
		self.setMinimumHeight(0)
		self.setMaximumHeight(450)
		self.adjustSize()

	def get_datetime_inputs(self):
		# Get combined datetime objects from date and time inputs
		start_dt = QDateTime(self.start_date_input.date(), self.start_time_input.time())
		end_dt = QDateTime(self.end_date_input.date(), self.end_time_input.time())
		return start_dt, end_dt

	def adjust_end_time(self):
		# Ensure end time is always after start time
		start_dt, end_dt = self.get_datetime_inputs()

		if start_dt >= end_dt:
			increment = start_dt.addSecs(60)
			self.end_date_input.setDate(increment.date())
			self.end_time_input.setTime(increment.time())
		
	def adjust_start_time(self):
		# Ensure start time is always before end time
		start_dt, end_dt = self.get_datetime_inputs()

		if end_dt <= start_dt:
			increment = end_dt.addSecs(-60)
			self.start_date_input.setDate(increment.date())
			self.start_time_input.setTime(increment.time())

	def save(self):
		# Validate inputs and save edited log to database and UI

		# Origin validation
		if not self.origin_input.text():
			self.error_label1.setVisible(True)
			self.error_label1.setText("<font color='red'> * Origin is required.</font>")
		else:
			self.error_label1.setVisible(False)

		# Destination validation
		if not self.destination_input.text():
			self.error_label2.setVisible(True)
			self.error_label2.setText("<font color='red'> * Destination is required.</font>")
		else:
			self.error_label2.setVisible(False)

		# Mode validation for "Other" selection
		if self.mode_input_cb.currentIndex() == 5 and not self.mode_input_le.text():
			self.error_label3.setVisible(True)
			self.error_label3.setText("<font color='red'> * Mode is required.</font>")
		else:
			self.error_label3.setVisible(False)

		# DateTime validation
		start_dt, end_dt = self.get_datetime_inputs()

		if start_dt >= end_dt:
			self.error_label4.setVisible(True)
			self.error_label4.setText("<font color='red'> * End date & time must be after start date & time.</font>")
			self.error_label4.setWordWrap(True)
		else:
			self.error_label4.setVisible(False)

		self.update_dialog_height()

		# Check if any validation errors exist
		errors = [self.error_label1.isVisible(), self.error_label2.isVisible(), 
				self.error_label3.isVisible(), self.error_label4.isVisible()]

		if any(errors):
			return

		# Prepare data for database update
		origin = self.origin_input.text()
		destination = self.destination_input.text()
		mode = self.mode_input_cb.currentText() if self.mode_input_cb.currentIndex() != 5 else self.mode_input_le.text()
		start = start_dt.toString("yyyy-MM-dd hh:mm:ss")
		end = end_dt.toString("yyyy-MM-dd hh:mm:ss")
		description = self.description_input.toPlainText()

		try:
			# Update database
			db.update_log(self.log_id, origin, destination, mode, start, end, description)
			
			# Update UI with edited log data
			current_table = self.main_window.tables[self.main_window.table_selector.currentIndex()]
			current_table.setSortingEnabled(False)
			current_table.blockSignals(True)

			current_table.setItem(self.current_log, 1, QTableWidgetItem(origin))
			current_table.setItem(self.current_log, 2, QTableWidgetItem(destination))
			current_table.setItem(self.current_log, 3, QTableWidgetItem(mode))
	
			# Format datetime for display
			start_dt_text = f"{self.start_date_input.date().toString('yyyy, MMM d')} [{self.start_time_input.time().toString('h:mm AP')}]"
			end_dt_text = f"{self.end_date_input.date().toString('yyyy, MMM d')} [{self.end_time_input.time().toString('h:mm AP')}]"
			duration_text = self.main_window.calculate_duration_per_log(start_dt, end_dt)

			# Create sortable table items
			start_item = QTableWidgetItem(start_dt_text)
			start_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_datetime(start_dt_text))
			end_item = QTableWidgetItem(end_dt_text)
			end_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_datetime(end_dt_text))
			duration_item = QTableWidgetItem(duration_text)
			duration_item.setData(Qt.ItemDataRole.UserRole, self.main_window.get_sortable_duration(duration_text))
			
			current_table.setItem(self.current_log, 4, start_item)
			current_table.setItem(self.current_log, 5, end_item)
			current_table.setItem(self.current_log, 6, duration_item)
			current_table.setItem(self.current_log, 7, QTableWidgetItem(description))

			current_table.setSortingEnabled(True)
			current_table.blockSignals(False)
			
			# Make all cells non-editable
			for col in range(current_table.columnCount()):
				item = current_table.item(self.current_log, col)

				if item:
					item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

			# Update duration statistics
			total_duration, average_duration = self.main_window.calculate_total_and_average_duration()
			self.main_window.total_duration_display.setText(total_duration)
			self.main_window.average_duration_display.setText(average_duration)

			current_table.selectRow(self.current_log)
	
			self.accept()
			
		except ValueError as e:
			QMessageBox.warning(self, "Error", str(e))
