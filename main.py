import os
import random
import tkinter as tk
from copy import deepcopy
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class ImageLabel(tk.Label):
    def __init__(self, cur_pos, init_pos, master=None, image_path=None, **kwargs):
        super().__init__(master, **kwargs)
        self.load_image(image_path)
        self.cur_pos = cur_pos
        self.init_pos = init_pos

    def load_image(self, image_path):
        if image_path:
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            self.configure(image=photo)
            self.image = photo


class BlockImagesWindow(tk.Toplevel):
    def __init__(self, parent, image_paths, rows, columns):
        super().__init__(parent)
        self.title("Generated Block Images")
        self.image_paths = image_paths
        self.rows = rows
        self.columns = columns
        self.selected_label = None
        self.labels = []
        self.nb_coup = 0

        self.image_frame = tk.Frame(self)
        self.image_frame.pack(fill='both', expand=True)
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side='bottom', fill='x')
        self.rand_button = tk.Button(self.control_frame, text="mélanger", command=self.randomize_images)
        self.rand_button.pack()
        self.coup_label = tk.Label(self.control_frame, text=f"Nombre de coup : {self.nb_coup}")
        self.coup_label.pack()

        self.rotation_frame = tk.Frame(self)
        self.rotation_frame.pack(side='bottom', fill='x')
        self.plus90_button = tk.Button(self.rotation_frame, text="+90", command=self.rotate_plus_90)
        self.plus90_button.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.moin90_button = tk.Button(self.rotation_frame, text="-90", command=self.rotate_moin_90)
        self.moin90_button.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.r180_button = tk.Button(self.rotation_frame, text="180", command=self.rotate_180)
        self.r180_button.pack(side=tk.LEFT, anchor=tk.CENTER)

        self.setup_window()

    def copy_labels(self):
        labels_copy = []
        for label in self.labels:
            new_label = ImageLabel(cur_pos=label.cur_pos, init_pos=label.init_pos)
            new_label['image'] = label['image']
            labels_copy.append(new_label)
        return labels_copy

    def convert_1d_to_2d(self, list, size):
        matrix = []
        for i in range(0, len(list), size):
            row = []
            for j in range(size):
                row.append(list[i + j])
            matrix.append(row)
        return matrix

    def convert_2d_to_1d_list(self, list):
        flattened_list = []
        for sublist in list:
            for item in sublist:
                flattened_list.append(item)
        return flattened_list

    def rotate_plus_90(self):
        labels_copy = self.copy_labels()

        matrix = self.convert_1d_to_2d(labels_copy, self.rows)

        transposed_matrix = []
        for i in range(self.rows):
            row = []
            for j in range(self.rows):
                row.append(matrix[self.rows-j-1][i])
            transposed_matrix.append(row)

        flattened_list = self.convert_2d_to_1d_list(transposed_matrix)

        for i in range(len(flattened_list)):
            self.labels[i]['image'] = flattened_list[i]['image']
            self.labels[i].cur_pos = flattened_list[i].cur_pos

    def rotate_moin_90(self):
        labels_copy = self.copy_labels()

        matrix = self.convert_1d_to_2d(labels_copy, self.rows)

        transposed_matrix = []
        for i in range(self.rows):
            row = []
            for j in range(self.rows):
                row.append(matrix[j][self.rows-i-1])
            transposed_matrix.append(row)

        flattened_list = self.convert_2d_to_1d_list(transposed_matrix)

        for i in range(len(flattened_list)):
            self.labels[i]['image'] = flattened_list[i]['image']
            self.labels[i].cur_pos = flattened_list[i].cur_pos

    def rotate_180(self):
        labels_copy = self.copy_labels()

        matrix = self.convert_1d_to_2d(labels_copy, self.rows)

        transposed_matrix = []
        for i in range(self.rows):
            row = []
            for j in range(self.rows):
                row.append(matrix[self.rows-i-1][self.rows-j-1])
            transposed_matrix.append(row)

        flattened_list = self.convert_2d_to_1d_list(transposed_matrix)

        for i in range(len(flattened_list)):
            self.labels[i]['image'] = flattened_list[i]['image']
            self.labels[i].cur_pos = flattened_list[i].cur_pos

    def check_all_pos(self):
        for label in self.labels:
            if label.init_pos != label.cur_pos:
                return False
        return True

    def randomize_images(self):
        # manao copy anle original de io no aparitako
        labels_copy = self.copy_labels()
        random.shuffle(labels_copy)

        for i in range(len(self.labels)):
            self.labels[i]['image'] = labels_copy[i]['image']
            self.labels[i].cur_pos = labels_copy[i].cur_pos


    def swap_images(self, event):
        print(f"init:{event.widget.init_pos}")
        print(f"cur:{event.widget.cur_pos}")
        print("-----------")
        event.widget.config(borderwidth=2, relief="solid")

        if self.selected_label is None:
            self.selected_label = event.widget
        else:
            # Swap the images
            temp_image = self.selected_label['image']
            self.selected_label['image'] = event.widget['image']
            event.widget['image'] = temp_image

            # Swap pos
            temp_pos = self.selected_label.cur_pos
            self.selected_label.cur_pos = event.widget.cur_pos
            event.widget.cur_pos = temp_pos

            self.selected_label.config(borderwidth=0)
            event.widget.config(borderwidth=0)
            # Clear the selection

            if self.selected_label.cur_pos != event.widget.cur_pos:
                self.nb_coup += 1
                self.coup_label['text'] = f"Nombre de coup : {self.nb_coup}"

            self.selected_label = None


        if self.check_all_pos():
            messagebox.showinfo("Succes", f"Vous avez terminer avec {self.nb_coup} coups!!")

    def setup_window(self):
        for index, image_path in enumerate(self.image_paths):
            init_row = index // self.columns
            init_col = index % self.columns
            label = ImageLabel((init_row, init_col), (init_row, init_col), self.image_frame, image_path)
            label.bind("<Button-1>", self.swap_images)
            label.grid(row=init_row, column=init_col)
            self.labels.append(label)


import io
class ImageGridApp:
    def __init__(self, root):
        self.output_directory = None
        self.root = root
        self.root.title("Image Grid Generator")

        self.image = None
        self.photo_image = None
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.rows_label = tk.Label(root, text="Number of Rows:")
        self.rows_label.pack()
        self.rows_entry = tk.Entry(root)
        self.rows_entry.pack()

        self.columns_label = tk.Label(root, text="Number of Columns:")
        self.columns_label.pack()
        self.columns_entry = tk.Entry(root)
        self.columns_entry.pack()

        self.generate_button = tk.Button(root, text="Generate Grid", command=self.generate_grid)
        self.generate_button.pack(pady=10)

        # -------------

        self.saved_image_paths = []
        self.saved_images = []

    def load_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.image = Image.open(file_path)
            self.photo_image = ImageTk.PhotoImage(self.image)
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

    def generate_grid(self):
        if not self.image:
            return

        try:
            rows = int(self.rows_entry.get())
            columns = int(self.columns_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numbers for rows and columns.")
            return

        # output path
        script_directory = os.path.dirname(os.path.abspath(__file__))
        script_directory += "\\images"
        current_datetime = datetime.now()
        date_time_string = current_datetime.strftime("%Y%m%d%H%M%S")
        self.output_directory = os.path.join(script_directory, f"{date_time_string}")
        os.makedirs(self.output_directory)

        self.saved_image_paths = []

        block_width = self.image.width // columns
        block_height = self.image.height // rows

        for row in range(rows):
            for col in range(columns):
                x0 = col * block_width
                y0 = row * block_height
                x1 = x0 + block_width
                y1 = y0 + block_height

                block_image = self.image.crop((x0, y0, x1, y1))
                output_path = f"{self.output_directory}\\block_{row}_{col}.png"
                block_image.save(output_path)
                self.saved_image_paths.append(output_path)

                block_photo = ImageTk.PhotoImage(block_image)
                self.saved_images.append(block_photo)

        BlockImagesWindow(self.root, self.saved_image_paths, rows, columns)



if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGridApp(root)
    root.mainloop()
#   2142
