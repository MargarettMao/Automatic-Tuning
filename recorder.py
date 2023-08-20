import pyaudio# folder spelt PyAudio
import wave
from tqdm import tqdm
import librosa 
import matplotlib.pyplot as plt
import numpy as np
import librosa.display



def record_audio(wave_out_path,record_second,spec_path,wav_im_path):
  CHUNK = 1024
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 22050
  p = pyaudio.PyAudio()
  stream = p.open(format=FORMAT,
          channels=CHANNELS,
          rate=RATE,
          input=True,
          frames_per_buffer=CHUNK)
  wf = wave.open(wave_out_path, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  print("* recording")
  for i in tqdm(range(0, int(RATE / CHUNK * record_second))):
    data = stream.read(CHUNK)
    wf.writeframes(data)
  print("* done recording")
  stream.stop_stream()
  stream.close()
  p.terminate()
  wf.close()
  create_spec(wave_out_path,spec_path)
  create_wav(wave_out_path,wav_im_path)


def create_spec(input,spec_path):
  y, sr = librosa.load(input)
  D = np.abs(librosa.stft(y))**2
  S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128,fmax=8000)
  fig, ax = plt.subplots()
  S_dB = librosa.power_to_db(S, ref=np.max)
  img = librosa.display.specshow(S_dB, x_axis='time',y_axis='mel', sr=sr,fmax=8000, ax=ax)
  fig.colorbar(img, ax=ax, format='%+2.0f dB')
  ax.set(title='Mel-frequency spectrogram')
  plt.savefig(spec_path)



  # 
def create_wav(input,wav_im_path):
  y, sr = librosa.load(input)
  fig, ax = plt.subplots()
  librosa.display.waveshow(y, sr=sr, ax=ax)
  ax.set(title="wav")
  plt.savefig(wav_im_path)
 
def main():
  time = 3
  name = "test629_non_click"
  wav_name = name +".wav"
  spec_name = name + "_spec"
  wav_im_name = name + "_wav"
  record_audio(wav_name,record_second = time,spec_path=spec_name,wav_im_path=wav_im_name)


if __name__ == '__main__':
  main()