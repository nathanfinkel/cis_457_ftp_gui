import tkinter as tk
from tkinter import ttk, simpledialog, scrolledtext
from ftp_client import ftp_open, ftp_close, ftp_dir

class FTPgui:
    def __init__(self,root):
        self.root = root
        self.root.title("FTP client")
        self.root.geometry("600x300")

        self.host_label = ttk.Label(root, text="Host:")
        self.host_label.pack(pady=(20,5))
        self.host_entry = ttk.Entry(root, width=30)
        self.host_entry.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=70, height=10,state='disabled')
        self.log_area.pack(pady=10)

        self.remote_files_frame = ttk.LabelFrame(root,text='Remote Files')
        self.remote_files_frame.pack(fill='both',expand=True,padx=10,pady=10)

        self.remote_files_scrollbar = ttk.Scrollbar(self.remote_files_frame,orient=tk.VERTICAL)
        self.remote_files_listbox = tk.Listbox(self.remote_files_frame,yscrollcommand=self.remote_files_scrollbar.set)
        self.remote_files_scrollbar.config(command=self.remote_files_listbox.yview)
        self.remote_files_scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.remote_files_listbox.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)

        

        self.place_buttons()

        self.ftp_socket = None

    def place_buttons(self):
        self.connect_button = ttk.Button(self.root, text="Connect", command=self.connect_button_pressed)
        self.connect_button.pack(pady=10)

        self.disconnect_button = ttk.Button(self.root, text="Disconnect", command=self.disconnect_button_pressed)
        self.disconnect_button.pack(pady=10)

        self.quit_button = ttk.Button(self.root, text="Quit", command=self.root.destroy)
        self.quit_button.pack(pady=20)
    
    def connect_button_pressed(self):

        host = self.host_entry.get()

        user = simpledialog.askstring("Input", "Enter Username:",parent=self.root)
        if user is None:
            return
        password = simpledialog.askstring("Input", "Enter Password:",parent=self.root, show='*')
        if password is None:
            return

        try:
            self.ftp_socket = ftp_open(host,user,password)
            self.log(f"Connected to FTP server at {host} as {user}")

            self.remote_ip,self.port = self.ftp_socket.getsockname()
            self.update_remote_files()

        except Exception as e:
            self.log(f"Error connecting to host: {e}")

    def disconnect_button_pressed(self):
        if self.ftp_socket:
            try:
                ftp_close(self.ftp_socket)
                self.log("Disconnected from FTP server.")
                self.remote_files_listbox.delete(0,tk.END)
            except Exception as e:
                self.log(f"Error disconnecting: {e}")
            finally:
                self.ftp_socket = None 
        else:
            self.log("Currently not connected to any FTP server.")
        
    def log(self,message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        
    def update_remote_files(self):
        if not self.ftp_socket:
            self.log(f"Not connected. no files to list.")
            return
        try:
            data = ftp_dir(self.ftp_socket,self.remote_ip)
            self.remote_files_listbox.delete(0,tk.END)
            lines = data.splitlines()
            for line in lines:
                self.remote_files_listbox.insert(tk.END,line)
            self.log("Remote files updated.")
        except Exception as e:
            self.log(f"Error listing remote files: {e}")
    




    
def main ():
    root = tk.Tk()
    app = FTPgui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
