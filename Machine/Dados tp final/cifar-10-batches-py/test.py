def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

data = unpickle("Machine\Dados tp final\cifar-10-batches-py\data_batch_1")#teste dados 1
print(data[b'data'])
'''
Loaded in this way, each of the batch files contains a dictionary with the following elements:

- data -- a 10000x3072 numpy array of uint8s. Each row of the array stores a 32x32 colour image. 
The first 1024 entries contain the red channel values, the next 1024 the green, and the final 1024 the blue. 
The image is stored in row-major order, so that the first 32 entries of the array are the red channel 
values of the first row of the image.
- labels -- a list of 10000 numbers in the range 0-9. The number at index i indicates the label of the ith image in the array data.

The dataset contains another file, called batches.meta. It too contains a Python dictionary object. It has the following entries:

label_names -- a 10-element list which gives meaningful names to the numeric labels in the labels array described above. 
For example, label_names[0] == "airplane", label_names[1] == "automobile", etc.
'''
import tensorflow as tf
from tensorflow.keras.datasets import cifar10

# Carregando o conjunto de dados
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Pré-processamento dos dados
x_train, x_test = x_train / 255.0, x_test / 255.0

# Definindo a arquitetura da rede neural
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')  # 10 classes de saída
])

# Compilando o modelo
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Treinando o modelo
model.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test))

# Avaliando o desempenho
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f"Acurácia no teste: {test_acc}")

# Fazendo previsões em novas imagens
predictions = model.predict(x_test[:5])
print(predictions)

