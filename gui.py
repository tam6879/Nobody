import tkinter as tk
import tkinter.scrolledtext as st
root = tk.Tk()

name: str = "Nobody: Secure Messaging"
tagline: str = "\"Nobody - that's my name.\" -Odysseus"
new_message = tk.StringVar()
canvas_bg: str = "bisque"
textbox_bg: str = "cornflower blue"
label_fg: str = "brown4"
label_font: str = "Times New Roman"
label_size: int = 20
label_size_small: int = 15
label_size_smaller: int = 10

root.title(name)
root.geometry("800x600")
root.configure(bg = canvas_bg)

top_lbl = tk.Label(root, text = name, font = (label_font, label_size), bg = canvas_bg, fg = label_fg)
bottom_lbl = tk.Label(root, text = tagline, font = (label_font, label_size), bg = canvas_bg, fg = label_fg)


past_messages = st.ScrolledText(root, width = 100, height = 15, font = (label_font, label_size_small), bg = textbox_bg)

def message_submit():
    if new_message.get() != "":
        update_past_messages(new_message.get())
    new_message.set("")
def update_past_messages(new_message: str) -> ():
    past_messages.configure(state = "normal")
    past_messages.insert(tk.END, new_message + '\n')
    past_messages.configure(state = "disabled")

new_m_frame = tk.Frame(root, bg = canvas_bg)

message_lbl = tk.Label(new_m_frame, text = "New message", font = (label_font, label_size_small), bg = canvas_bg, fg = label_fg)
message_entry = tk.Entry(new_m_frame, textvariable = new_message, bg = textbox_bg, fg = "white", width = 70, font = (label_font, label_size_smaller))
message_btn = tk.Button(new_m_frame, text = "Send", command = message_submit, font = (label_font, label_size_smaller))

top_lbl.pack()
past_messages.pack()
new_m_frame.pack()
message_lbl.pack(side="left")
message_entry.pack(side="left")
message_btn.pack(side="left")
bottom_lbl.pack()


update_past_messages("COMMUNISM")

root.mainloop()
