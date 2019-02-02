
# coding: utf-8

# # MNIST digits classification with TensorFlow

# <img src="images/mnist_sample.png" style="width:30%">

# In[ ]:


import numpy as np
from sklearn.metrics import accuracy_score
from matplotlib import pyplot as plt
get_ipython().magic('matplotlib inline')
import tensorflow as tf
print("We're using TF", tf.__version__)


# In[ ]:


import sys
sys.path.append("../..")
import grading

import matplotlib_utils
from importlib import reload
reload(matplotlib_utils)

import grading_utils
reload(grading_utils)

import keras_utils
from keras_utils import reset_tf_session


# # Fill in your Coursera token and email
# To successfully submit your answers to our grader, please fill in your Coursera submission token and email

# In[ ]:


grader = grading.Grader(assignment_key="XtD7ho3TEeiHQBLWejjYAA", 
                        all_parts=["9XaAS", "vmogZ", "RMv95", "i8bgs", "rE763"])


# In[ ]:


# token expires every 30 min
COURSERA_TOKEN = "### YOUR TOKEN HERE ###"
COURSERA_EMAIL = "### YOUR EMAIL HERE ###"


# # Look at the data
# 
# In this task we have 50000 28x28 images of digits from 0 to 9.
# We will train a classifier on this data.

# In[ ]:


import preprocessed_mnist
X_train, y_train, X_val, y_val, X_test, y_test = preprocessed_mnist.load_dataset_from_file()


# In[ ]:


# X contains rgb values divided by 255
print("X_train [shape %s] sample patch:\n" % (str(X_train.shape)), X_train[1, 15:20, 5:10])
print("A closeup of a sample patch:")
plt.imshow(X_train[1, 15:20, 5:10], cmap="Greys")
plt.show()
print("And the whole sample:")
plt.imshow(X_train[1], cmap="Greys")
plt.show()
print("y_train [shape %s] 10 samples:\n" % (str(y_train.shape)), y_train[:10])


# # Linear model
# 
# Your task is to train a linear classifier $\vec{x} \rightarrow y$ with SGD using TensorFlow.
# 
# You will need to calculate a logit (a linear transformation) $z_k$ for each class: 
# $$z_k = \vec{x} \cdot \vec{w_k} + b_k \quad k = 0..9$$
# 
# And transform logits $z_k$ to valid probabilities $p_k$ with softmax: 
# $$p_k = \frac{e^{z_k}}{\sum_{i=0}^{9}{e^{z_i}}} \quad k = 0..9$$
# 
# We will use a cross-entropy loss to train our multi-class classifier:
# $$\text{cross-entropy}(y, p) = -\sum_{k=0}^{9}{\log(p_k)[y = k]}$$ 
# 
# where 
# $$
# [x]=\begin{cases}
#        1, \quad \text{if $x$ is true} \\
#        0, \quad \text{otherwise}
#     \end{cases}
# $$
# 
# Cross-entropy minimization pushes $p_k$ close to 1 when $y = k$, which is what we want.
# 
# Here's the plan:
# * Flatten the images (28x28 -> 784) with `X_train.reshape((X_train.shape[0], -1))` to simplify our linear model implementation
# * Use a matrix placeholder for flattened `X_train`
# * Convert `y_train` to one-hot encoded vectors that are needed for cross-entropy
# * Use a shared variable `W` for all weights (a column $\vec{w_k}$ per class) and `b` for all biases.
# * Aim for ~0.93 validation accuracy

# In[ ]:


X_train_flat = X_train.reshape((X_train.shape[0], -1))
print(X_train_flat.shape)

X_val_flat = X_val.reshape((X_val.shape[0], -1))
print(X_val_flat.shape)


# In[ ]:


import keras

y_train_oh = keras.utils.to_categorical(y_train, 10)
y_val_oh = keras.utils.to_categorical(y_val, 10)

print(y_train_oh.shape)
print(y_train_oh[:3], y_train[:3])


# In[ ]:


# run this again if you remake your graph
s = reset_tf_session()


# In[ ]:


# Model parameters: W and b
W = ### YOUR CODE HERE ### tf.get_variable(...) with shape[0] = 784
b = ### YOUR CODE HERE ### tf.get_variable(...)


# In[ ]:


# Placeholders for the input data
input_X = ### YOUR CODE HERE ### tf.placeholder(...) for flat X with shape[0] = None for any batch size
input_y = ### YOUR CODE HERE ### tf.placeholder(...) for one-hot encoded true labels


# In[ ]:


# Compute predictions
logits = ### YOUR CODE HERE ### logits for input_X, resulting shape should be [input_X.shape[0], 10]
probas = ### YOUR CODE HERE ### apply tf.nn.softmax to logits
classes = ### YOUR CODE HERE ### apply tf.argmax to find a class index with highest probability

# Loss should be a scalar number: average loss over all the objects with tf.reduce_mean().
# Use tf.nn.softmax_cross_entropy_with_logits on top of one-hot encoded input_y and logits.
# It is identical to calculating cross-entropy on top of probas, but is more numerically friendly (read the docs).
loss = ### YOUR CODE HERE ### cross-entropy loss

# Use a default tf.train.AdamOptimizer to get an SGD step
step = ### YOUR CODE HERE ### optimizer step that minimizes the loss


# In[ ]:


s.run(tf.global_variables_initializer())

BATCH_SIZE = 512
EPOCHS = 40

# for logging the progress right here in Jupyter (for those who don't have TensorBoard)
simpleTrainingCurves = matplotlib_utils.SimpleTrainingCurves("cross-entropy", "accuracy")

for epoch in range(EPOCHS):  # we finish an epoch when we've looked at all training samples
    
    batch_losses = []
    for batch_start in range(0, X_train_flat.shape[0], BATCH_SIZE):  # data is already shuffled
        _, batch_loss = s.run([step, loss], {input_X: X_train_flat[batch_start:batch_start+BATCH_SIZE], 
                                             input_y: y_train_oh[batch_start:batch_start+BATCH_SIZE]})
        # collect batch losses, this is almost free as we need a forward pass for backprop anyway
        batch_losses.append(batch_loss)

    train_loss = np.mean(batch_losses)
    val_loss = s.run(loss, {input_X: X_val_flat, input_y: y_val_oh})  # this part is usually small
    train_accuracy = accuracy_score(y_train, s.run(classes, {input_X: X_train_flat}))  # this is slow and usually skipped
    valid_accuracy = accuracy_score(y_val, s.run(classes, {input_X: X_val_flat}))  
    simpleTrainingCurves.add(train_loss, val_loss, train_accuracy, valid_accuracy)


# # Submit a linear model

# In[ ]:


## GRADED PART, DO NOT CHANGE!
# Testing shapes 
grader.set_answer("9XaAS", grading_utils.get_tensors_shapes_string([W, b, input_X, input_y, logits, probas, classes]))
# Validation loss
grader.set_answer("vmogZ", s.run(loss, {input_X: X_val_flat, input_y: y_val_oh}))
# Validation accuracy
grader.set_answer("RMv95", accuracy_score(y_val, s.run(classes, {input_X: X_val_flat})))


# In[ ]:


# you can make submission with answers so far to check yourself at this stage
grader.submit(COURSERA_EMAIL, COURSERA_TOKEN)


# # MLP with hidden layers

# Previously we've coded a dense layer with matrix multiplication by hand. 
# But this is not convenient, you have to create a lot of variables and your code becomes a mess. 
# In TensorFlow there's an easier way to make a dense layer:
# ```python
# hidden1 = tf.layers.dense(inputs, 256, activation=tf.nn.sigmoid)
# ```
# 
# That will create all the necessary variables automatically.
# Here you can also choose an activation function (remember that we need it for a hidden layer!).
# 
# Now define the MLP with 2 hidden layers and restart training with the cell above.
# 
# You're aiming for ~0.97 validation accuracy here.

# In[ ]:


# write the code here to get a new `step` operation and then run the cell with training loop above.
# name your variables in the same way (e.g. logits, probas, classes, etc) for safety.
### YOUR CODE HERE ###


# # Submit the MLP with 2 hidden layers
# Run these cells after training the MLP with 2 hidden layers

# In[ ]:


## GRADED PART, DO NOT CHANGE!
# Validation loss for MLP
grader.set_answer("i8bgs", s.run(loss, {input_X: X_val_flat, input_y: y_val_oh}))
# Validation accuracy for MLP
grader.set_answer("rE763", accuracy_score(y_val, s.run(classes, {input_X: X_val_flat})))


# In[ ]:


# you can make submission with answers so far to check yourself at this stage
grader.submit(COURSERA_EMAIL, COURSERA_TOKEN)


# In[ ]:




