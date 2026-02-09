import argparse
import numpy as np
import tritonclient.http as httpclient
import sys

def main(url, model_name, audio_path, language=None):
    try:
        triton_client = httpclient.InferenceServerClient(url=url)
    except Exception as e:
        print("channel creation failed: " + str(e))
        sys.exit(1)

    if not triton_client.is_server_live():
        print("FAILED : is_server_live")
        sys.exit(1)

    # Create dummy audio data if file doesn't exist or not provided
    # In a real test, load actual audio bytes
    if not audio_path:
        print("No audio file provided, creating dummy 1-second silence (16kHz)...")
        # 16000 samples of zeros (silence), 16-bit PCM
        audio_data = np.zeros(16000, dtype=np.int16).tobytes()
    else:
        with open(audio_path, "rb") as f:
            audio_data = f.read()

    inputs = []
    
    # Input 1: AUDIO_DATA
    inputs.append(httpclient.InferInput("AUDIO_DATA", [1], "BYTES"))
    inputs[0].set_data_from_numpy(np.array([audio_data], dtype=np.object_))

    # Input 2: LANGUAGE (Optional)
    if language:
        inputs.append(httpclient.InferInput("LANGUAGE", [1], "BYTES"))
        inputs[1].set_data_from_numpy(np.array([language.encode('utf-8')], dtype=np.object_))

    outputs = []
    outputs.append(httpclient.InferRequestedOutput("TRANSCRIPT"))

    print(f"Sending request to model '{model_name}'...")
    results = triton_client.infer(model_name=model_name, inputs=inputs, outputs=outputs)
    
    transcript = results.as_numpy("TRANSCRIPT")[0].decode('utf-8')
    print(f"Response: {transcript}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False, default='localhost:8000')
    parser.add_argument('--model', type=str, required=False, default='whisper_template')
    parser.add_argument('--audio', type=str, required=False, help='Path to audio file')
    parser.add_argument('--lang', type=str, required=False, help='Language code')
    args = parser.parse_args()
    
    main(args.url, args.model, args.audio, args.lang)
