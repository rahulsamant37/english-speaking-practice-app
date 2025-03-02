from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os
from dotenv import load_dotenv
import wavio
import uuid
import pyttsx3
import threading
from datetime import datetime, timedelta
from pathlib import Path
import pyaudio
import numpy as np
from faster_whisper import WhisperModel
import notion_api as api
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Add Groq API key environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY') 

load_dotenv()

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')

URL_SEG1 = 'https://api.notion.com/v1/blocks/'
URL_SEG2 = '/children'

PARTS = {
  'Part 1': os.getenv('PAGE_ID_PART1'),
  'Part 2': os.getenv('PAGE_ID_PART2'),
  'Part 3': os.getenv('PAGE_ID_PART3'),
}

COLNUM = 12

MODES = {
    'Local Whisper': 'local',
}

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recordings = []
        self.is_recording = False
        self.chunk = 1024
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.samplerate = 16000

    def start_recording(self):
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.is_recording = True
        self.recordings = []

    def stop_recording(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.is_recording = False
            return np.concatenate(self.recordings) if self.recordings else None
        return None

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
        else:
            self.is_recording = True
            
    def record(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk)
                self.recordings.append(np.frombuffer(data, dtype=np.float32))
            except Exception as e:
                print(f"Error recording audio: {e}")
                break

class AudioTranscriber:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.texts = []

    def transcribe(self):
        segments, _ = self.model.transcribe(self.audio_path)
        self.texts = [segment.text for segment in segments]
        return self.texts

class SpeakingPracticeApp(Frame):
  def __init__(self, root, **kwargs):
    super().__init__(root, **kwargs)

    self.kwargs = kwargs
    self.speech_engine = pyttsx3.init()
    self.speech_engine.setProperty('rate', 150)
    self.speech_thread = None
    self.is_loop_running = False

    self.root = root
    self.root.title('Speaking Practice App')

    style = Style()
    style.theme_use('clam')
    style.configure('timer.TLabel', foreground='red', font=('Helvetica', 24))

    self.my_text = ''
    self.ai_text = ''
    self.chat_history = [
      {
        'role': 'system',
        'content': f'You are a native English teacher. From now on, please help me practise English speaking for IELTS speaking test. You should ask me 4 to 5 questions in total on a topic about me or things that are closely related to me. You should ask only one question per time and should end our conversation after the specified number of questions by saying it is the end for the practice. If relevant, please correct my mistakes on grammars, choice of words, etc. Please choose questions as close to real test as possible and please use UK English instead of US English. After final question, please give me a score based on IELTS 9.0 scale.'
      },
    ]
    self.chat_history_to_save = []

    self.num_chat_history = IntVar(value=len(self.chat_history))
    self.num_chat_history_to_save = IntVar(value=len(self.chat_history_to_save))

    self.recorder = AudioRecorder()
    self.audio_thread = None

    self.isTicking = False
    self.start_time = None
    self.elapsed_time = timedelta()

    # main frame
    self.main_frame = Frame(self.root)
    self.main_frame.grid(row=0, column=0)

    # utility buttons frame
    self.utility_btns_frame = Frame(self.main_frame)
    self.utility_btns_frame.grid(row=0, column=0, sticky=E, padx=20, pady=[20, 10])

    self.save_btn = Button(self.utility_btns_frame, text='Save Chat', command=self.save_chat_to_file, state=DISABLED)
    self.save_btn.grid(row=0, column=0, padx=[0, 5])

    self.reset_history_btn = Button(self.utility_btns_frame, text='Reset Chat', command=self.reset_chat_history, state=DISABLED)
    self.reset_history_btn.grid(row=0, column=1, padx=5)

    self.num_chat_history.trace_add('write', self._toggle_state_of_reset_btn)
    self.num_chat_history_to_save.trace_add('write', self._toggle_state_of_save_btn)

    self.quit_btn = Button(self.utility_btns_frame, text='Quit', command=self.quit)
    self.quit_btn.grid(row=0, column=2, padx=[5, 0])

    # chat box frame
    self.chatbox_frame = Frame(self.main_frame)
    self.chatbox_frame.grid(row=1, column=0, padx=20, pady=10)
    for i in range(COLNUM):
      self.chatbox_frame.columnconfigure(i, minsize=50, weight=1)

    Label(self.chatbox_frame, text='Me').grid(row=0, column=0, sticky=W, pady=[0, 10])

    self.my_box = Text(self.chatbox_frame, height=10)
    self.my_box.grid(row=1, column=0, columnspan=COLNUM, sticky='we')
    self.my_box.bind("<KeyRelease>", self._on_my_text_change)
    self.my_box.bind("<ButtonRelease>", self._on_my_text_change)

    Label(self.chatbox_frame, text='AI English Expert').grid(row=2, column=0, sticky=W, pady=10)

    self.ai_box = Text(self.chatbox_frame, height=10)
    self.ai_box.grid(row=3, column=0, columnspan=COLNUM, sticky='we')
    self.ai_box.bind("<KeyRelease>", self._on_ai_text_change)
    self.ai_box.bind("<ButtonRelease>", self._on_ai_text_change)

    # combobox frame
    self.mode_select_frame = Frame(self.main_frame)
    self.mode_select_frame.grid(row=2, column=0, sticky='we', padx=20, pady=10)
    for i in range(COLNUM):
      self.mode_select_frame.columnconfigure(i, minsize=50, weight=1)

    self.mode_select = Combobox(
        self.mode_select_frame, values=list(MODES.keys()))
    self.mode_select.bind('<<ComboboxSelected>>', self._on_select_mode)
    self.mode_select.grid(
        row=1, column=0, columnspan=COLNUM, sticky='we')
    self.mode_select.current(0)

    self.mode = MODES[self.mode_select.get().strip()]

    # timer frame
    self.timer_frame = Frame(self.main_frame)
    self.timer_frame.grid(row=3, column=0, sticky='we', padx=20, pady=10)
    for i in range(COLNUM):
      self.timer_frame.columnconfigure(i, minsize=50, weight=1)

    self.timer = Label(self.timer_frame, text='00:00', style='timer.TLabel')
    self.timer.grid(row=0, column=0, columnspan=COLNUM)

    # buttons frame
    self.btns_frame = Frame(self.main_frame)
    self.btns_frame.grid(row=4, column=0, sticky='we', padx=20, pady=[10, 20])
    for i in range(COLNUM):
      self.btns_frame.columnconfigure(i, minsize=50, weight=1)

    self.start_btn = Button(self.btns_frame, text='Start', command=self.start)
    self.start_btn.grid(row=1, column=0, columnspan=3, sticky='we', padx=[0, 5])

    self.toggle_btn = Button(
        self.btns_frame, text='Pause', command=self.toggle, state=DISABLED)
    self.toggle_btn.grid(row=1, column=3, columnspan=3, sticky='we', padx=5)

    self.stop_btn = Button(self.btns_frame, text='Stop',
                           command=self.stop, state=DISABLED)
    self.stop_btn.grid(row=1, column=6, columnspan=3, sticky='we', padx=5)

    self.restart_btn = Button(
        self.btns_frame, text='Restart', command=self.restart, state=DISABLED)
    self.restart_btn.grid(row=1, column=9, columnspan=3, sticky='we', padx=[5, 0])

    self.send_btn = Button(self.btns_frame, text='Send',
                           command=self.send, state=DISABLED)
    self.send_btn.grid(row=2, column=0, columnspan=COLNUM, sticky='we', pady=20)

  def _on_select_mode(self, event):
    self.mode = MODES[self.mode_select.get().strip()]

  def _on_my_text_change(self, event):
    pass

  def _on_ai_text_change(self, event):
    pass

  def _toggle_state_of_save_btn(self, *args):
    if self.num_chat_history_to_save.get() > 0:
      self.save_btn.configure(state=NORMAL)
    else:
      self.save_btn.configure(state=DISABLED)

  def _toggle_state_of_reset_btn(self, *args):
    if self.num_chat_history.get() > 1:
      self.reset_history_btn.configure(state=NORMAL)
    else:
      self.reset_history_btn.configure(state=DISABLED)

  def start_timer(self):
    if not self.isTicking:
      self.isTicking = True
      if not self.start_time:
        self.start_time = datetime.now() - self.elapsed_time
      self.update_timer()

  def stop_timer(self):
    if self.isTicking:
      self.isTicking = False
      self.start_time = datetime.now()
      self.elapsed_time = datetime.now() - self.start_time

  def reset_timer(self):
    self.isTicking = False
    self.start_time = None
    self.elapsed_time = timedelta()
    self.timer.config(text='00:00')

  def update_timer(self):
    if self.isTicking:
      elapsed_time = datetime.now() - self.start_time
      mins, secs = divmod(elapsed_time.seconds, 60)
      self.timer.config(text=f'{mins:02}:{secs:02}')
      self.root.after(1000, self.update_timer)

  def start(self):
    self.reset_timer()
    self.start_timer()
    self.recorder.start_recording()
    self.audio_thread = threading.Thread(target=self.recorder.record)
    self.audio_thread.start()
    self.start_btn.configure(state=DISABLED)
    self.toggle_btn.configure(state=NORMAL)
    self.stop_btn.configure(state=NORMAL)
    self.restart_btn.configure(state=NORMAL)

  def toggle(self):
    if self.isTicking:
      self.stop_timer()
    else:
      self.start_timer()
    self.recorder.toggle_recording()
    if self.toggle_btn.cget('text') == 'Pause':
      self.toggle_btn.configure(text='Resume', state=NORMAL)
    else:
      self.toggle_btn.configure(text='Pause', state=NORMAL)
    self.stop_btn.configure(state=NORMAL)

  def stop(self):
    self.stop_timer()
    self.start_btn.configure(state=NORMAL)
    self.toggle_btn.configure(text='Pause', state=DISABLED)
    self.stop_btn.configure(state=DISABLED)
    self.restart_btn.configure(state=DISABLED)
    self.send_btn.configure(state=NORMAL)

    self.audio_data = self.recorder.stop_recording()
    if self.audio_data is not None:
      should_save = messagebox.askyesno(
          "Save Recording", "Do you want to save the recording?")
      if should_save:
        self.my_text = self.transcribe().strip()
        # display my recording text in chat box
        self.my_box.delete("1.0", END)
        self.my_box.insert(END, self.my_text)
      else:
        self.restart()
    else:
      self.restart()

  def transcribe(self):
    path = Path('./_recordings')
    if not path.exists():
      path.mkdir(parents=True, exist_ok=True)
    filepath = path / f'{str(uuid.uuid4())}.wav'

    try:
      wavio.write(filepath.as_posix(), self.audio_data,
                  self.recorder.samplerate, sampwidth=3)

      transcriber = AudioTranscriber(filepath)
      texts = transcriber.transcribe()
      return texts[0] if texts else ""
    except Exception as e:
      messagebox.showerror(title='Error', message=f'{e}')
      return ""
    finally:
      if filepath.exists():
        filepath.unlink()  # Delete the temporary file
      self.restart()

  def restart(self):
    self.reset_timer()
    self.start_btn.configure(state=NORMAL)
    self.toggle_btn.configure(text='Pause', state=DISABLED)
    self.stop_btn.configure(state=DISABLED)
    self.restart_btn.configure(state=DISABLED)
    self.recorder.recordings = []
    self.audio_data = None

  def update_message(self, mode='both'):
    if mode == 'both':
      self.my_text = self.my_box.get("1.0", END)
      self.ai_text = self.ai_box.get("1.0", END)
    elif mode == 'my_text':
      self.my_text = self.my_box.get("1.0", END)
    elif mode == 'ai_text':
      self.ai_text = self.ai_box.get("1.0", END)

  def send(self):
    self.update_message(mode='my_text')
    
    try:
        # Initialize Groq chat
        chat = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name="gemma2-9b-it"  # Free model
        )
        
        # Convert chat history to messages
        messages = []
        for msg in self.chat_history:
            if msg['role'] == 'system':
                messages.append(SystemMessage(content=msg['content']))
            elif msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
                
        # Get response
        response = chat.invoke(messages)
        self.ai_text = response.content
        
        # Update chat history
        self.chat_history.append({
            'role': 'assistant',
            'content': self.ai_text
        })
        self.num_chat_history.set(self.num_chat_history.get()+1)
        
        self.chat_history_to_save.append({
            'role': 'assistant',
            'content': self.ai_text
        })
        self.num_chat_history_to_save.set(self.num_chat_history_to_save.get()+1)

        # Display response
        self.ai_box.delete("1.0", END)
        self.ai_box.insert(END, self.ai_text)
        self.speech_thread = threading.Thread(target=self._speech)
        self.speech_thread.start()
    except Exception as e:
        messagebox.showerror(title='Error', message=f'{e}')

  def _speech(self):
    self.speech_engine.say(self.ai_text)
    if not self.is_loop_running:
      self.is_loop_running = True
      self.speech_engine.startLoop()

  def save_chat_to_file(self):
    try:
        # Create _chats directory if it doesn't exist
        path = Path('./_chats')
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            
        # Generate filename with timestamp
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = path / filename
        
        # Write chat history to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for message in self.chat_history_to_save:
                f.write(f"=== {message['role'].upper()} ===\n")
                f.write(f"{message['content']}\n\n")
                
        messagebox.showinfo(title="Done", message=f"Chat saved to {filename}")
        self.save_btn.configure(state=DISABLED)
        self.chat_history_to_save = []
        self.num_chat_history_to_save.set(0)
    except Exception as e:
        messagebox.showerror(title='Error', message=f'{e}')

  def reset_chat_history(self):
    self.chat_history = [
      {
        'role': 'system',
        'content': f'You are a native English teacher. From now on, please help me practise English speaking for IELTS speaking test. You should ask me 4 to 5 questions in total on a topic about me or things that are closely related to me. You should ask only one question per time and should end our conversation after the specified number of questions by saying it is the end for the practice. If relevant, please correct my mistakes on grammars, choice of words, etc. Please choose questions as close to real test as possible and please use UK English instead of US English. After final question, please give me a score based on IELTS 9.0 scale.'
      },
    ]
    self.num_chat_history.set(1)
    self.chat_history_to_save = []
    self.num_chat_history_to_save.set(0)
    self.my_box.delete("1.0", END)
    self.ai_box.delete("1.0", END)
    self.reset_history_btn.configure(state=DISABLED)

  def quit(self):
    self.stop()
    self.reset_timer()
    if self.recorder.audio_thread:
      self.recorder.audio_thread.join()
    if self.speech_thread:
      self.speech_thread.join()

    # only save to file when there was conversation
    if self.num_chat_history_to_save.get() > 0:
      should_save = messagebox.askyesno(
          "Save Chat", "Do you want to save the chat?")
      if should_save:
        self.save_chat_to_file()

    if self.is_loop_running:
      self.speech_engine.endLoop()
      self.is_loop_running = False

    self.speech_engine = None

    self.root.destroy()

if __name__ == "__main__":
  root = Tk()
  app = SpeakingPracticeApp(root)
  app.mainloop()

