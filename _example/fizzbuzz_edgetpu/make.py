from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import tensorflow as tf
from tensorflow.compat.v1.keras.models import Sequential, model_from_json
from tensorflow.compat.v1.keras.layers import Dense, Dropout, Activation
from tensorflow.compat.v1.keras.optimizers import SGD, Adam
import tensorflow.compat.v1.lite as lite

def fizzbuzz(i):
    if   i % 15 == 0: return np.array([0, 0, 0, 1], dtype=np.float32)
    elif i % 5  == 0: return np.array([0, 0, 1, 0], dtype=np.float32)
    elif i % 3  == 0: return np.array([0, 1, 0, 0], dtype=np.float32)
    else:             return np.array([1, 0, 0, 0], dtype=np.float32)

def bin(i, num_digits):
    return np.array([i >> d & 1 for d in range(num_digits)], dtype=np.float32)

NUM_DIGITS = 7
trX = np.array([bin(i, NUM_DIGITS) for i in range(1, 101)])
trY = np.array([fizzbuzz(i) for i in range(1, 101)])
model = Sequential()
model.add(Dense(64, input_dim = 7))
model.add(Activation('tanh'))
model.add(Dense(4, input_dim = 64))
model.add(Activation('softmax'))
model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
model.fit(trX, trY, epochs = 3600, batch_size = 64)
model.save('fizzbuzz_model.h5')

def representative_dataset_gen():
    for i in range(100):
        yield [trX[i: i + 1]]

converter = lite.TFLiteConverter.from_keras_model_file('fizzbuzz_model.h5')
converter.representative_dataset = representative_dataset_gen
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()
with open('fizzbuzz_model_quant.tflite', 'wb') as o_:
    o_.write(tflite_model)
