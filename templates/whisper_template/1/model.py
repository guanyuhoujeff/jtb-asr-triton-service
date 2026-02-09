import io
import json
import os
import time

import numpy as np
import triton_python_backend_utils as pb_utils
from faster_whisper import WhisperModel


class TritonPythonModel:
    def initialize(self, args):
        self.model_config = json.loads(args["model_config"])
        base_path = args["model_repository"]
        model_name = args["model_name"]
        
        # Determine model path
        # If the model name matches the directory name, use base_path directly
        if os.path.basename(base_path) == model_name:
            model_dir = base_path
        else:
            model_dir = os.path.join(base_path, model_name)
            
        # Expecting weights in 'faster-whisper-model' subdirectory
        model_path = os.path.join(model_dir, "faster-whisper-model")

        if not os.path.exists(model_path):
             raise pb_utils.TritonModelException(f"Model path not found: {model_path}")

        print(f"Loading Whisper model from {model_path}...")

        self.model = WhisperModel(
            model_path,
            device="cuda",
            compute_type="float16",
            cpu_threads=4,
        )
        print("Whisper model loaded successfully.")

    def execute(self, requests):
        responses = []

        for request in requests:
            t0 = time.time()

            in_audio = pb_utils.get_input_tensor_by_name(request, "AUDIO_DATA")
            # Triton sends bytes as numpy array of objects/bytes
            audio_bytes = in_audio.as_numpy()[0]

            lang_code = None
            in_lang = pb_utils.get_input_tensor_by_name(request, "LANGUAGE")
            if in_lang is not None:
                lang_code = in_lang.as_numpy()[0].decode("utf-8")

            t1 = time.time()
            binary_stream = io.BytesIO(audio_bytes)

            try:
                segments, _info = self.model.transcribe(
                    binary_stream,
                    beam_size=1,
                    language=lang_code,
                    temperature=0,
                )
                full_text = "".join([segment.text for segment in segments])
            except Exception as exc:
                full_text = f"Error: {str(exc)}"

            t2 = time.time()
            print(
                "[Timing] Input Prep: {:.2f}ms | Inference: {:.2f}ms | Total: {:.2f}ms".format(
                    (t1 - t0) * 1000,
                    (t2 - t1) * 1000,
                    (t2 - t0) * 1000,
                )
            )

            out_tensor = pb_utils.Tensor(
                "TRANSCRIPT",
                np.array([full_text.encode("utf-8")], dtype=np.object_),
            )
            inference_response = pb_utils.InferenceResponse(output_tensors=[out_tensor])
            responses.append(inference_response)

        return responses
