# -*- coding: utf-8 -*-
"""NN2 packet_bitdecode.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O_21qFvJ9GwOm_5w7R0afU3OUSZl3RpA
"""

from google.colab import drive
drive.mount('/content/drive')

!cp -r '/content/drive/MyDrive/NN2_bit_decoder' '/content'

"""# Load NumPy data"""

import numpy as np
import tensorflow as tf
import os

"""Extract .npz files with array from each category:"""

!7z x /content/ones1.7z

"""### Load from `.npz` file"""

train_examples = []
train_labels = []
test_examples = []
test_labels = []
for npz_file_number in range(23):
    data = np.load('/content/ones/1_packets'+str(npz_file_number)+'.npz')
    for j in range(42):
      train_examples.append(data['arr_'+str(j)])
      train_labels.append(1)
for npz_file_number in range(23,25):
    data = np.load('/content/ones/1_packets'+str(npz_file_number)+'.npz')
    for j in range(42):
      test_examples.append(data['arr_'+str(j)])
      test_labels.append(1)
for npz_file_number in range(23):
    data = np.load('/content/zeroes/0_packets'+str(npz_file_number)+'.npz')
    for j in range(42):
      train_examples.append(data['arr_'+str(j)])
      train_labels.append(0)
for npz_file_number in range(23,25):
    data = np.load('/content/zeroes/0_packets'+str(npz_file_number)+'.npz')
    for j in range(42):
      test_examples.append(data['arr_'+str(j)])
      test_labels.append(0)

print(np.shape(train_examples),np.shape(train_labels))
print(np.shape(test_examples),test_labels)

"""## Load NumPy arrays with `tf.data.Dataset`

Assuming you have an array of examples and a corresponding array of labels, pass the two arrays as a tuple into `tf.data.Dataset.from_tensor_slices` to create a `tf.data.Dataset`.
"""

train_dataset = tf.data.Dataset.from_tensor_slices((train_examples, train_labels))
test_dataset = tf.data.Dataset.from_tensor_slices((test_examples, test_labels))

BATCH_SIZE = 32
SHUFFLE_BUFFER_SIZE = 1932

train_dataset = train_dataset.shuffle(SHUFFLE_BUFFER_SIZE).batch(BATCH_SIZE)
test_dataset = test_dataset.batch(BATCH_SIZE)

"""### Build and train a model"""

model = tf.keras.Sequential([
    tf.keras.layers.LayerNormalization(axis=1 , center=True , scale=False),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(2)
])

model.compile(optimizer=tf.keras.optimizers.Adam(),
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=False),
              metrics=['accuracy'])

history=model.fit(train_dataset, epochs=20)

import matplotlib.pyplot as plt

acc = history.history['accuracy']
#val_acc = history.history['val_acc']

loss = history.history['loss']
#val_loss = history.history['val_loss']

epochs_range = range(20)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.legend(loc='lower right')
plt.title('Training Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.legend(loc='upper right')
plt.title('Training Loss')
plt.show()

!7z x /content/stream.7z

results = model.evaluate(test_dataset)
print("test loss, test acc:", results)

data = np.load('/content/pack_bit1'+'.npz') #receive start position of the packet from the 1st neural network (another file) + 40 samples - data(!!!) begins 
print(data.files)
stream = data['arr_0']
slicey=[]
for i in range(32,256,4):# short - 280 samples msg = 56 bit, ext - 560 samples msg = 112 bit, preamble = 40 samps
    slicey.append(stream[i:i+4])
print(np.shape(slicey))
sliceyy=np.array(slicey)
classes = model.predict_classes(sliceyy)
print(len(classes))
np.set_printoptions(threshold=np.inf)
print(classes)

from tensorflow import keras
#model.save("my_modeldecode2") - MAIN SAVING MODEL FUNCTION (USE ONLY WITH CORRECT/IMPROVED MODELS)

# It can be used to reconstruct the model identically.
reconstructed_model = keras.models.load_model("my_modeldecode2")

# Let's check:
'''np.testing.assert_allclose(
    model.predict(test_dataset), reconstructed_model.predict(test_dataset)
)'''

# The reconstructed model is already compiled and has retained the optimizer
# state, so training can resume:
reconstructed_model.fit(test_dataset)

data = np.load('/content/resamp_packets.bitdecode'+'.npz')
print(data.files)
bit_stream = data['arr_25']
bits=[]
for i in range(32,480,4):# short - 280 samples msg = 56 bit, ext - 560 samples msg = 112 bit, preamble = 40 samps
    bits.append(bit_stream[i:i+4])
print(np.shape(bits))
bit_arr=np.array(bits)
classes1 = (reconstructed_model.predict(bit_arr) > 0.5).astype("int32")# gives the duplicated array with shape (112,2) TensorGod knows why (deprecated model.predict_classes worked well)
print(len(classes1))
np.set_printoptions(threshold=np.inf)
bit_string = classes1.flatten('F')
print(bit_string)
print(len(bit_string))

#just bit check comparing to real data (automated testing would be great - I'll upload more data samples to check the network if you know how to automate prediction)
stringbit='''1000110101001100101000110101000101011000101110010111001011111101010111010011111100011111001000001101001100001011

'''
stringbit.count('0')

!rsync -r --progress "/content/my_modeldecode2" "/content/drive/MyDrive"