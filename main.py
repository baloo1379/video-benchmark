import glob
import os
import pickle
import re
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import matplotlib.pyplot as plt
import numpy as np

DEFAULT_FILENAME = "test.mkv"


class GUI:
    filename = ''
    saved_files = []
    for file in glob.glob("*.pkl"):
        saved_files.append(file)
    window = tk.Tk()
    window.title('Benchmark')
    window.geometry("600x600")
    read_file = tk.StringVar(window)
    window.resizable(False, False)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=2)
    window.columnconfigure(2, weight=1)
    window.rowconfigure(0, weight=2)
    window.rowconfigure(1, weight=1)
    window.rowconfigure(2, weight=2)
    passes_number = tk.Entry(window)
    passes_number.configure(width=10)
    passes_number.insert(0, '10')
    results_x = []
    results_y = []
    f4 = tk.Frame(window)
    f4.grid(column=1, row=1, sticky="N")
    f5 = tk.Frame(window)
    f5.grid(column=0, row=1, sticky="N")
    table = ttk.Treeview(f4)
    avg = tk.StringVar()
    tot = tk.StringVar()

    table['columns'] = ('Nr próby', 'Czas wykonania')
    table.configure(height=20)
    table.column("#0", width=0, stretch=tk.NO)
    table.column("Nr próby", width=120, anchor=tk.CENTER)
    table.column('Czas wykonania', width=120, anchor=tk.CENTER)
    table.heading("#0", text="", anchor=tk.CENTER)
    table.heading("Nr próby", text="Nr próby", anchor=tk.CENTER)
    table.heading("Czas wykonania", text="Czas wykonania [s]", anchor=tk.CENTER)
    f3 = tk.Frame(window)
    f3.grid(column=1, row=2)
    avg_label = tk.Label(f3, text='Średni czas: ')
    avg_label.grid(row=0, column=0, sticky='n')
    result_label = tk.Label(f3, textvariable=avg)
    total_label = tk.Label(f3, text='Całkowity czas: ')
    total_label.grid(row=1, column=0)
    tot_label = tk.Label(f3, textvariable=tot)

    def openfile(self):
        self.filename = askopenfilename()

    def _run_cmd(self, cmd):
        output_b = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        output = str(output_b)
        rtime = re.search(r"rtime=\d+.\d+s", output).group()
        result = float(re.search(r"\d+.\d+", rtime).group())
        return result

    def generate_test_file(self, filename=DEFAULT_FILENAME):
        return self._run_cmd(
            f"ffmpeg -f lavfi -i nullsrc=s=1920x1080 -filter_complex \"geq=random(1)*255:128:128;aevalsrc=-2+random(0)\" -t 10 -benchmark {filename}")

    def run_encoding(self, filename=DEFAULT_FILENAME):
        return self._run_cmd(
            f"ffmpeg -i {filename} -c:v libx264 -preset veryfast -profile:v high -level:v 4.2 -crf 28 -benchmark -f null -")

    def benchmark(self, filename=DEFAULT_FILENAME):

        for item in self.table.get_children():
            self.table.delete(item)
        passes = int(self.passes_number.get())
        file_exists = os.path.isfile(self.filename)
        if not file_exists:
            print("Given test file not found. Checking default...")
            filename = DEFAULT_FILENAME
            if not os.path.isfile(DEFAULT_FILENAME):
                print("Test file not found. Generating new file...")
                time = self.generate_test_file()
                print(f"File generated in {time:.2f}s.")

        avg_sum = 0.0
        self.results_y = []
        self.results_x = []

        print(f"Running benchmark with {passes} passes...")
        for ip in range(passes):
            print(f"pass {ip + 1}", end='')
            time = self.run_encoding(filename)
            avg_sum += time
            self.results_x.append((ip + 1))
            self.results_y.append(time)
            self.table.insert(parent='', index=ip + 1, iid=ip + 1, text='', values=(str(ip + 1), str(time)))
            self.table.grid(row=1, column=1)
            print(f"\t{time:.2f}")

        avg_time = avg_sum / passes
        print("Avg", f"{avg_time:.2f}")
        print("Total", f"{avg_sum:.2f}")
        self.avg.set(f"{avg_time:.2f}s")
        self.tot.set(f"{avg_sum:.2f}s")
        plt.figure(figsize=(10, 5))
        y_pos = np.arange(len(self.results_y))
        plt.bar(y_pos, self.results_y, color='#34728C')
        plt.xticks(y_pos, self.results_x)
        plt.xlabel('Numer proby', fontsize=12, color='#323232')
        plt.ylabel('Czas wykonania [s]', fontsize=12, color='#323232')
        plt.show()
        self.result_label.grid(row=0, column=1)
        self.tot_label.grid(row=1, column=1)
        now = datetime.now()
        date_time = now.strftime("%m%d%Y%H%M")
        to_save = np.array([[self.results_x], [self.results_y]])
        with open('zapis' + date_time + ".pkl", 'wb') as fp:
            pickle.dump(to_save, fp)
            self.saved_files.append('zapis' + date_time)
        return avg_sum / passes

    def openfile(self):
        self.filename = askopenfilename()

    def show_archive(self):
        for item in self.table.get_children():
            self.table.delete(item)
        print(self.read_file.get())
        infile = open(self.read_file.get(), 'rb')
        new_dict = pickle.load(infile)
        new_dict = new_dict.tolist()
        flat_list = [item for sublist in new_dict for item in sublist]
        print(flat_list)
        for i in range(len(flat_list[0])):
            self.table.insert(parent='', index=int(flat_list[0][i]), iid=int(flat_list[0][i]), text='',
                              values=(str(flat_list[0][i]), str(flat_list[1][i])))
            self.table.grid(row=1, column=1)
        self.avg.set(str(sum(flat_list[1]) / len(flat_list[1])))
        self.tot.set(str(sum(flat_list[1])))
        self.result_label.grid(row=0, column=1)
        self.tot_label.grid(row=1, column=1)

    def run(self):
        f1 = tk.Frame(self.window)
        f1.grid(row=0, column=0)
        l1 = tk.Label(f1, text="Załącz plik")
        l1.grid(row=0, column=0)
        file_button = tk.Button(f1, background='#E1F974', text="Browse", command=self.openfile)
        file_button.grid(row=1, column=0)
        f2 = tk.Frame(self.window)
        f2.grid(row=0, column=1)
        l2 = tk.Label(f2, text="Podaj liczbę prób i kliknij by zacząć pracę programu")
        l2.grid(row=0, column=0)
        start_button = tk.Button(f2, background='#479B63', text="Start test",
                                 command=lambda: self.benchmark(self.filename))
        start_button.grid(row=1, column=0)
        w = tk.OptionMenu(self.f5, self.read_file, '', *self.saved_files)
        w.configure(width=20)
        w.grid(column=0, row=0, sticky=tk.W)
        archive_button = tk.Button(self.f5, background='#479B63', text="Show", command=lambda: self.show_archive())
        archive_button.grid(row=1, column=1)
        print(self.saved_files)
        self.passes_number.grid(row=0, column=2)
        self.table.grid(row=1, column=1)
        self.result_label.grid(row=2, column=1)
        self.window.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.run()
