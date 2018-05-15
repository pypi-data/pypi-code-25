import os
import re
import sys
import tkinter as tk
import traceback
import unicodedata
import urllib.request
import webbrowser
from multiprocessing import Process, Pipe
from tkinter import font, ttk, filedialog, messagebox
from urllib.parse import urljoin
from urllib.request import pathname2url

from lxml import html


class Window(ttk.Frame):
    pad = 10

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        parent.report_callback_exception = self.report_callback_exception
        self.parent = parent
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=Window.pad, pady=Window.pad)
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        parent.title('The Magic Comic Reader')
        parent.resizable(False, False)
        font_size = 13
        font.nametofont('TkDefaultFont').configure(size=font_size)
        font.nametofont('TkTextFont').configure(size=font_size)
        font.nametofont('TkFixedFont').configure(size=font_size)
        entry_width = 50

        self.label1 = ttk.Label(self, text='First Page URL:')
        self.entry1 = ttk.Entry(self, width=entry_width)
        self.label2 = ttk.Label(self, text='First Image URL:')
        self.entry2 = ttk.Entry(self, width=entry_width)
        self.label3 = ttk.Label(self, text='Second Page URL:')
        self.entry3 = ttk.Entry(self, width=entry_width)
        self.button = ttk.Button(self, text='Begin', command=self.begin)

        self.label1.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry1.grid(row=0, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.label2.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry2.grid(row=1, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.label3.grid(row=2, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry3.grid(row=2, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.button.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E, padx=Window.pad, pady=Window.pad)

    def begin(self):
        self.parent.geometry(f'{self.parent.winfo_width()}x{self.parent.winfo_height()}')
        url1 = self.entry1.get()
        url2 = self.entry2.get()
        url3 = self.entry3.get()
        for widget in self.winfo_children():
            widget.grid_forget()
            widget.destroy()
        self.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        label = ttk.Label(self, text='Downloading...')
        label.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.stringVar = tk.StringVar()
        label = ttk.Label(self, textvariable=self.stringVar)
        label.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        progressbar = ttk.Progressbar(self, mode='indeterminate')
        progressbar.grid(row=2, column=0, sticky=tk.W + tk.E, padx=Window.pad, pady=Window.pad)
        progressbar.start()
        self.conn, child_conn = Pipe()
        self.process = Process(target=build_webpage, args=(child_conn, url1, url2, url3))
        self.process.start()
        self.page_count = 0
        self.show_progress()

    def show_progress(self):
        message = None
        while self.conn.poll() and message != 'DONE' and message != 'ERROR':
            message = self.conn.recv()
            self.page_count += 1
        self.check_for_subprocess_error(message)
        if message == 'DONE':
            self.show_end_page()
        else:
            if message is not None:
                self.stringVar.set(f'Page {self.page_count}: {message}')
            self.after(30, self.show_progress)

    def show_end_page(self):
        for widget in self.winfo_children():
            widget.grid_forget()
            widget.destroy()
        label = ttk.Label(self, text='Done.')
        label.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        label = ttk.Label(self, text=f'Found {self.page_count - 1} pages.')
        label.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        button = ttk.Button(self, text='Save', command=self.save)
        button.grid(row=2, column=0, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E, padx=Window.pad, pady=Window.pad)

    def save(self):
        suggested_filename = self.conn.recv()
        self.check_for_subprocess_error(suggested_filename)
        output_file = filedialog.asksaveasfile(defaultextension='.html', filetypes=[('Webpage', '*.html')],
                                               initialfile=suggested_filename, parent=self.parent)
        if output_file is None:
            return
        output_filename = os.path.realpath(output_file.name)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reader.html')) as file:
            html_str = file.read()
        image_urls = self.conn.recv()
        self.check_for_subprocess_error(image_urls)
        html_str = html_str.replace('{{imageUrls}}', repr(image_urls))
        output_file.write(html_str)
        output_file.close()
        webbrowser.open('file:' + pathname2url(output_filename), new=2, autoraise=True)
        self.parent.destroy()

    def check_for_subprocess_error(self, message):
        if message == 'ERROR':
            self.show_error(self.conn.recv())
            self.parent.destroy()

    def report_callback_exception(self, *args):
        self.show_error(''.join(traceback.format_exception(*args)))

    def show_error(self, error_str):
        messagebox.showerror('Error', error_str)


# Must be a top-level module function (?)
def build_webpage(conn, first_page_url, first_image_url, second_page_url):
    try:
        first_page = get_document(conn, first_page_url)
        image_urls = get_all_image_urls(conn, first_page, first_page_url, first_image_url, second_page_url)
        conn.send('DONE')
        conn.send(get_filename(first_page))
        conn.send(image_urls)
        conn.close()
    except:
        conn.send('ERROR')
        conn.send(''.join(traceback.format_exception(*sys.exc_info())))
        conn.close()


def get_all_image_urls(conn, first_page, first_page_url, first_image_url, second_page_url):
    image_path = get_path_to_url(first_page, first_page_url, first_image_url)
    next_page_path = get_path_to_url(first_page, first_page_url, second_page_url)
    page_urls = {first_page_url}
    image_urls = [urljoin(first_page_url, first_page.xpath(image_path, smart_strings=False)[0])]
    url = urljoin(first_page_url, first_page.xpath(next_page_path, smart_strings=False)[0])
    try:
        while url not in page_urls:  # The last page may link to itself or a previous page.
            page_urls.add(url)
            document = get_document(conn, url)
            image_urls.append(urljoin(url, document.xpath(image_path, smart_strings=False)[0]))
            url = urljoin(url, document.xpath(next_page_path, smart_strings=False)[0])
    except:
        pass  # The last page will probably cause an exception.
    return image_urls


def get_document(conn, url):
    conn.send(url)
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    html_str = urllib.request.urlopen(request).read()
    return html.document_fromstring(html_str)


def get_path_to_url(document, base_url, target_url):
    """
    Searches the document for target_url and returns an xpath to it. Raises ValueError if target_url is not found. Uses
    base_url to resolve relative urls.
    """
    attributes = ('action background cite classid code codebase data formaction href icon itemscope itemtype longdesc '
                  'manifest poster profile src usemap')
    for result in document.xpath('|'.join('//@' + attribute for attribute in attributes.split())):
        if urljoin(base_url, result) == target_url:
            element = result.getparent()
            for key, value in element.attrib.items():
                if value == result:
                    return document.getroottree().getpath(element) + '/@' + key
    raise ValueError(f"Link to '{target_url}' not found.")


def get_filename(document):
    value = document.find('.//title').text
    value = unicodedata.normalize('NFKD', value)
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)[:30]
    return value or 'The Magic Comic Reader'


def main():
    root = tk.Tk()
    Window(root)
    root.mainloop()


if __name__ == '__main__':
    main()
