import argparse
import numpy as np
import tritonclient.http as httpclient
import sys
import wave
import io
from scipy.io import wavfile
from scipy.signal import resample_poly
import os


def wav_to_triton_audio_bytes(wav_path, target_sr=16000):
    """
    讀 wav 檔，自動：
    - 轉 mono
    - resample 到 target_sr
    - 轉 16-bit PCM
    最後回傳完整 WAV bytes（含 RIFF header），可直接丟給 transcribe_with_triton
    """
    sr, x = wavfile.read(wav_path)  # x: np.ndarray, shape (n,) or (n, ch)

    # 1) 轉成 float32 in [-1, 1]
    if np.issubdtype(x.dtype, np.integer):
        # 依 dtype 最大值正規化（int16/int32/uint8 都可）
        info = np.iinfo(x.dtype)
        if x.dtype == np.uint8:
            # uint8 wav 常見 128 為 0
            x_f = (x.astype(np.float32) - 128.0) / 128.0
        else:
            x_f = x.astype(np.float32) / max(abs(info.min), info.max)
    else:
        # float wav（通常已是 -1~1）
        x_f = x.astype(np.float32)

    # 2) stereo/multi-channel → mono
    if x_f.ndim == 2:
        x_f = np.mean(x_f, axis=1)

    # 3) resample 到 target_sr
    if sr != target_sr:
        # resample_poly 需要整數 up/down
        g = np.gcd(sr, target_sr)
        up = target_sr // g
        down = sr // g
        x_f = resample_poly(x_f, up, down).astype(np.float32)

    # 4) clip + 轉 int16 PCM
    x_f = np.clip(x_f, -1.0, 1.0)
    x_i16 = (x_f * 32767.0).astype(np.int16)

    return prepare_audio_bytes( x_i16.tobytes() , sr=target_sr, channels = 1, sampwidth = 2 )

def prepare_audio_bytes( audio_bytes , sr=16000, channels = 1, sampwidth = 2 ):
    """_summary_
    適用在當聲音都來自多段錄音片段的 list 時，將其轉成符合 Triton Whisper 模型輸入格式的 bytes
    
    Args:
        audio_bytes (_type_): _description_
        sr (int, optional): _description_. Defaults to 16000.
        channels (int, optional): _description_. Defaults to 1.
        sampwidth (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        wf.writeframes(audio_bytes)
    audio_data = buf.getvalue()  # 這時候就會有 RIFF...WAVE
    return audio_data

def transcribe_with_triton(audio_bytes_with_riff_wave, model_name="whisper_l_v2", language=None):
    # 讀取音訊基本資訊，決定是否需要分段
    with wave.open(io.BytesIO(audio_bytes_with_riff_wave), "rb") as wf:
        framerate = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        nframes = wf.getnframes()
        audio_frames = wf.readframes(nframes)

    duration_sec = nframes / float(framerate) if framerate else 0
    max_chunk_sec = 29

    def _infer(segment_bytes):
        input_data = np.array([segment_bytes], dtype=np.object_)
        inputs = []
        inputs.append(httpclient.InferInput("AUDIO_DATA", [1], "BYTES"))
        inputs[0].set_data_from_numpy(input_data)
        if language:
            lang_input = httpclient.InferInput("LANGUAGE", [1], "BYTES")
            lang_input.set_data_from_numpy(np.array([language.encode("utf-8")], dtype=np.object_))
            inputs.append(lang_input)
        response = asr_service_client.infer(model_name=model_name, inputs=inputs)
        return response.as_numpy("TRANSCRIPT")[0].decode("utf-8")

    if duration_sec > max_chunk_sec:
        # 分段處理，避免一次送太長造成辨識錯誤
        frames_per_chunk = int(max_chunk_sec * framerate)
        frame_size_bytes = n_channels * sampwidth
        transcripts = []
        for start_frame in range(0, nframes, frames_per_chunk):
            end_frame = min(start_frame + frames_per_chunk, nframes)
            start_byte = start_frame * frame_size_bytes
            end_byte = end_frame * frame_size_bytes
            chunk_frames = audio_frames[start_byte:end_byte]
            chunk_wav_bytes = prepare_audio_bytes(
                chunk_frames,
                sr=framerate,
                channels=n_channels,
                sampwidth=sampwidth,
            )
            transcripts.append(_infer(chunk_wav_bytes))
        return " ".join(transcripts)

    input_data = np.array([audio_bytes_with_riff_wave ], dtype=np.object_)
    inputs = []
    # print("input_data", input_data)
    inputs.append(httpclient.InferInput("AUDIO_DATA", [1], "BYTES"))
    inputs[0].set_data_from_numpy(input_data)
    if language:
        lang_input = httpclient.InferInput("LANGUAGE", [1], "BYTES")
        lang_input.set_data_from_numpy(np.array([language.encode("utf-8")], dtype=np.object_))
        inputs.append(lang_input)
    # 發送請求
    response = triton_client.infer(model_name=model_name, inputs=inputs)
    # 獲取結果
    asr_text = response.as_numpy("TRANSCRIPT")[0].decode("utf-8")
    return asr_text

def main(model_name, audio_path, language=None):
    # Create dummy audio data if file doesn't exist or not provided
    # In a real test, load actual audio bytes
    if not audio_path:
        print("No audio file provided, creating dummy 1-second silence (16kHz)...")
        # 16000 samples of zeros (silence), 16-bit PCM
        audio_data = np.zeros(16000, dtype=np.int16).tobytes()
    else:
        audio_data = wav_to_triton_audio_bytes(audio_path)

    asr_text = transcribe_with_triton(audio_data, model_name, language)
    print("Triton ASR warm up result:", asr_text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False, default='localhost:8000')
    parser.add_argument('--model', type=str, required=False, default='whisper_template')
    parser.add_argument('--audio', type=str, required=False, help='Path to audio file')
    parser.add_argument('--lang', type=str, required=False, help='Language code')
    args = parser.parse_args()
    
    try:
        triton_client = httpclient.InferenceServerClient(url=args.url)
    except Exception as e:
        print("channel creation failed: " + str(e))
        sys.exit(1)

    if not triton_client.is_server_live():
        print("FAILED : is_server_live")
        sys.exit(1)

    main(args.model, args.audio, args.lang)
