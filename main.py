import sys
import numpy as np
import matplotlib.pyplot as plt
import base64
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QInputDialog, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class Process:
    def __init__(self, name, burst_time, arrival_time=0):
        self.name = name
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.start_time = None
        self.end_time = None

class CPU_Scheduler(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CPU Scheduler')
        self.setGeometry(100, 100, 600, 400)

        self.label_processes = QLabel('Number of processes:')
        self.input_processes = QLineEdit()

        self.label_algorithm = QLabel('Select Scheduling Algorithm:')
        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems(['FCFS', 'SJF', 'RR'])

        self.label_quantum = QLabel('Quantum (for RR):')
        self.input_quantum = QLineEdit()
        self.input_quantum.setEnabled(False)

        self.btn_add_processes = QPushButton('Add Processes')
        self.btn_add_processes.clicked.connect(self.addProcesses)

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)

        self.gantt_chart_label = QLabel()
        self.gantt_chart_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_processes)
        self.layout.addWidget(self.input_processes)
        self.layout.addWidget(self.label_algorithm)
        self.layout.addWidget(self.combo_algorithm)
        self.layout.addWidget(self.label_quantum)
        self.layout.addWidget(self.input_quantum)
        self.layout.addWidget(self.btn_add_processes)
        self.layout.addWidget(self.output_console)
        self.layout.addWidget(self.gantt_chart_label)
        self.setLayout(self.layout)

    def addProcesses(self):
        num_processes = int(self.input_processes.text())
        self.processes = []
        burst_times = []

        self.output_console.clear()
        self.output_console.append("Enter the Burst Time of the processes:")
        for i in range(1, num_processes + 1):
            burst_time, ok = QInputDialog.getInt(self, f'Burst Time for Process {i}', f'Enter burst time for Process {i}:')
            if ok:
                self.processes.append(Process(f'P{i}', burst_time))
                burst_times.append(burst_time)

        selected_algorithm = self.combo_algorithm.currentText()
        if selected_algorithm == 'FCFS':
            self.fcfs()
        elif selected_algorithm == 'SJF':
            self.sjf()
        elif selected_algorithm == 'RR':
            quantum, ok = QInputDialog.getInt(self, 'Quantum for RR', 'Enter quantum for Round Robin:')
            if ok:
                self.rr(quantum)

    def fcfs(self):
        current_time = 0
        for process in self.processes:
            if process.burst_time > 0:
                if process.start_time is None:
                    process.start_time = current_time
                process.end_time = current_time + process.burst_time
                current_time = process.end_time

        self.displayResults()

    def sjf(self):
        current_time = 0
        sorted_processes = sorted(self.processes, key=lambda x: x.burst_time)
        for process in sorted_processes:
            if process.burst_time > 0:
                if process.start_time is None:
                    process.start_time = current_time
                process.end_time = current_time + process.burst_time
                current_time = process.end_time

        self.displayResults()

    def rr(self, quantum):
        current_time = 0
        while any(process.burst_time > 0 for process in self.processes):
            for process in self.processes:
                if process.burst_time > 0:
                    if process.start_time is None:
                        process.start_time = current_time
                    if process.burst_time <= quantum:
                        current_time += process.burst_time
                        process.end_time = current_time
                        process.burst_time = 0
                    else:
                        current_time += quantum
                        process.burst_time -= quantum

        self.displayResults()

    def displayResults(self):
        waiting_times = []
        for process in self.processes:
            if process.start_time is not None and process.arrival_time is not None:
                waiting_times.append(process.start_time - process.arrival_time)
            else:
                waiting_times.append(None)

        turnaround_times = []
        for process in self.processes:
            if process.end_time is not None and process.arrival_time is not None:
                turnaround_times.append(process.end_time - process.arrival_time)
            else:
                turnaround_times.append(None)

        self.output_console.append("\nP\tB_T\tW_T\tTA_T")
        for i, process in enumerate(self.processes):
            self.output_console.append(f"{process.name}\t{process.burst_time}\t{waiting_times[i]}\t{turnaround_times[i]}")

        avg_waiting_time = np.nanmean(waiting_times)
        avg_turnaround_time = np.nanmean(turnaround_times)

        self.output_console.append(f"\nThe average Waiting Time for the whole sequence of processes is = {avg_waiting_time}")
        self.output_console.append(f"The average Turn Around Time of the processes is = {avg_turnaround_time}")

        # Set minimum width to 100% and adjust height dynamically based on content
        self.output_console.setMinimumWidth(self.width())
        self.output_console.setFixedHeight(self.output_console.sizeHint().height())

        self.plotGanttChart()


    def plotGanttChart(self):
        fig, ax = plt.subplots()
        for i, process in enumerate(self.processes):
            ax.barh(y=process.name, width=process.end_time - process.start_time, left=process.start_time, label=process.name)
        ax.set_xlabel('Time')
        ax.set_ylabel('Processes')
        ax.set_title('Gantt Chart')
        ax.legend()
        ax.invert_yaxis()
        plt.tight_layout()

        # Save the figure to a temporary file
        temp_file = 'gantt_chart.png'
        plt.savefig(temp_file)
        plt.close()

        # Display the image in the GUI
        pixmap = QPixmap(temp_file)
        self.gantt_chart_label.setPixmap(pixmap)
        self.gantt_chart_label.adjustSize()

def main():
    app = QApplication(sys.argv)
    window = CPU_Scheduler()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
