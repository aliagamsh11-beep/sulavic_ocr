"""
محرك OCR لتحليل مخرجات YOLOv8 TFLite
"""
import json
import os
import numpy as np
from PIL import Image


class OCREngine:
    def __init__(self, model_path, classes_path=None, conf_threshold=0.25):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.classes = self._load_classes(classes_path)
        self.loaded = False

    def _load_classes(self, path):
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return [chr(i) for i in range(ord('А'), ord('А') + 43)]

    def load(self):
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            try:
                import tensorflow.lite as tflite
            except ImportError:
                return False

        if not os.path.exists(self.model_path):
            return False

        try:
            self.interpreter = tflite.Interpreter(
                model_path=self.model_path, num_threads=4
            )
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.loaded = True
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False

    def preprocess(self, image_path, size=(640, 640)):
        img = Image.open(image_path).convert("RGB")
        self.original_size = img.size
        img = img.resize(size)
        arr = np.array(img, dtype=np.uint8)
        return np.expand_dims(arr, axis=0)

    def predict(self, image_path):
        if not self.loaded:
            return []
        try:
            inp = self.preprocess(image_path)
            self.interpreter.set_tensor(
                self.input_details[0]['index'], inp
            )
            self.interpreter.invoke()
            out = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )
            return self._parse(out)
        except Exception as e:
            print(f"Predict error: {e}")
            return []

    def _parse(self, output):
        results = []
        try:
            preds = output[0]
            n = preds.shape[0] - 4
            boxes = preds[:4, :]
            scores = preds[4:, :]
            cls_ids = np.argmax(scores, axis=0)
            confs = np.max(scores, axis=0)

            mask = confs > self.conf_threshold
            for i in np.where(mask)[0]:
                cid = int(cls_ids[i])
                if cid < len(self.classes):
                    results.append({
                        'letter': self.classes[cid],
                        'class_id': cid,
                        'confidence': float(confs[i]),
                        'bbox': boxes[:, i].tolist()
                    })
            # ترتيب من اليسار لليمين (محور x لمركز المربع)
            results.sort(key=lambda r: r['bbox'][0])
            return results
        except Exception as e:
            print(f"Parse error: {e}")
            return []
