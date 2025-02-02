import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt




def create_model(hidden_units, learning_rate):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(784, activation='sigmoid', input_shape=(784,)),
        tf.keras.layers.Dense(hidden_units, activation='sigmoid'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    optimizer = tf.keras.optimizers.SGD(learning_rate = learning_rate)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model

def gradient(_model, _x, _y, _epochs, _batch):
    historico_de_perdas = []  # Lista para armazenar o histórico de perdas
    for epoch in range(_epochs):
        for i in range(0, _x.shape[0], _batch):
            with tf.GradientTape() as tape:
                prediction = _model(_x[i:i + _batch])
                loss = _model.compiled_loss(_y[i:i + _batch], prediction)
            gradients = tape.gradient(loss, _model.trainable_variables)
            _model.optimizer.apply_gradients(zip(gradients, _model.trainable_variables))
        predictions = _model(_x)
        loss = _model.compiled_loss(_y, predictions)
        historico_de_perdas.append(loss.numpy())  # Armazena a perda da época atual
        #print(f"Epoch {epoch+1} loss {loss:.4f}")
    return historico_de_perdas

def graphic(x, y, hidden_layer, r, epochs, batch):
    plt.plot(gradient(create_model(hidden_layer, r), x, y, epochs, batch), label=f"hiddens layer: {hidden_layer}, r: {r}, Batch: {batch}")
    plt.title('Convergência do Erro Empírico')
    plt.xlabel('Época')
    plt.ylabel('Erro Empírico')
    plt.legend()
    plt.savefig(f'grafico_{hidden_layer}_{r}_{batch}.png')
    plt.close()
    print( f'grafico_{hidden_layer}_{r}_{batch}.png')

data_path = 'data_tp1.csv'
data = np.loadtxt(data_path, delimiter=',')
x = data[:, 1:]
y = data[:, 0]  
y = tf.keras.utils.to_categorical(y, num_classes=10)

    #graphic(x, y, 25,  10.0, 10, 5000)
    #graphic(x, y, 25,  10.0, 10, 1)
    #graphic(x, y, 25,  10.0, 10, 50)

    #graphic(x, y, 50,  10.0, 10, 5000)
#graphic(x, y, 50,  10.0, 10, 1)
    #graphic(x, y, 50,  10.0, 10, 50)
    
    #graphic(x, y, 100, 10.0, 10, 5000)
#graphic(x, y, 100, 10.0, 10, 1)
    #graphic(x, y, 100, 10.0, 10, 50)

    #graphic(x, y, 25,  1.0, 10, 5000)
#graphic(x, y, 25,  1.0, 10, 1)
    #graphic(x, y, 25,  1.0, 10, 5000)

    #graphic(x, y, 25,  1.0, 10, 50)
    
    #graphic(x, y, 50,  1.0, 10, 5000)
#
# graphic(x, y, 50,  1.0, 10, 1)
    #graphic(x, y, 50,  1.0, 10, 50)
    
    #graphic(x, y, 100, 0.01, 10, 5000)
#
# graphic(x, y, 100, 0.01, 10, 1)
    #graphic(x, y, 100, 0.01, 10, 50)

    #graphic(x, y, 25,  0.01, 10, 5000)
#
# graphic(x, y, 25,  0.01, 10, 1)
    #graphic(x, y, 25,  0.01, 10, 50)
    
    #graphic(x, y, 50,  0.01, 10, 5000)
#
# graphic(x, y, 50,  0.01, 10, 1)
    #graphic(x, y, 50,  0.01, 10, 50)
    
    #graphic(x, y, 100, 0.01, 10, 5000)
g
raphic(x, y, 100, 0.01, 10, 1)
    #graphic(x, y, 100, 0.01, 10, 50)



'''
você deverá variar o número de unidades na camada oculta (25, 50, 100). 
Por fim, você também deverá variar a taxa de aprendizado: 0.5, 1, 10.
'''


