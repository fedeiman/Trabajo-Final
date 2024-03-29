import tensorflow as tf
import pandas as pd
import os
import shutil
from transformers import BertTokenizer, TFBertForSequenceClassification, AutoModel, AutoTokenizer
from transformers import InputExample, InputFeatures

model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

train = tf.keras.preprocessing.text_dataset_from_directory(
    'data', batch_size=30000, validation_split=0.2,
    subset='training', seed=123)

test = tf.keras.preprocessing.text_dataset_from_directory(
    'data', batch_size=30000, validation_split=0.2,
    subset='validation', seed=123)

# todo change test data to dev partition

# Todo create a new partition called holdout (semeval/test)

for i in train.take(1):
    train_feat = i[0].numpy()
    train_lab = i[1].numpy()

train = pd.DataFrame([train_feat, train_lab]).T
train.columns = ['DATA_COLUMN', 'LABEL_COLUMN']
train['DATA_COLUMN'] = train['DATA_COLUMN'].str.decode("utf-8")
train.head()


for j in test.take(1):
    test_feat = j[0].numpy()
    test_lab = j[1].numpy()

test = pd.DataFrame([test_feat, test_lab]).T
test.columns = ['DATA_COLUMN', 'LABEL_COLUMN']
test['DATA_COLUMN'] = test['DATA_COLUMN'].str.decode("utf-8")
test.head()

InputExample(guid=None,
             text_a="Hello, world",
             text_b=None,
             label=1)


def convert_data_to_examples(train, test, DATA_COLUMN, LABEL_COLUMN):
    train_InputExamples = train.apply(lambda x: InputExample(guid=None,  # Globally unique ID for bookkeeping, unused in this case
                                                             text_a=x[DATA_COLUMN],
                                                             text_b=None,
                                                             label=x[LABEL_COLUMN]), axis=1)

    validation_InputExamples = test.apply(lambda x: InputExample(guid=None,  # Globally unique ID for bookkeeping, unused in this case
                                                                 text_a=x[DATA_COLUMN],
                                                                 text_b=None,
                                                                 label=x[LABEL_COLUMN]), axis=1)

    return train_InputExamples, validation_InputExamples

    train_InputExamples, validation_InputExamples = convert_data_to_examples(train,
                                                                             test,
                                                                             'DATA_COLUMN',
                                                                             'LABEL_COLUMN')


def convert_examples_to_tf_dataset(examples, tokenizer, max_length=128):
    features = []  # -> will hold InputFeatures to be converted later

    for e in examples:
        input_dict = tokenizer.encode_plus(
            e.text_a,
            add_special_tokens=True,
            max_length=max_length,  # truncates if len(s) > max_length
            return_token_type_ids=True,
            return_attention_mask=True,
            # pads to the right by default # CHECK THIS for pad_to_max_length
            pad_to_max_length=True,
            truncation=True
        )

        input_ids, token_type_ids, attention_mask = (input_dict["input_ids"],
                                                     input_dict["token_type_ids"], input_dict['attention_mask'])

        features.append(
            InputFeatures(
                input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, label=e.label
            )
        )

    def gen():
        for f in features:
            yield (
                {
                    "input_ids": f.input_ids,
                    "attention_mask": f.attention_mask,
                    "token_type_ids": f.token_type_ids,
                },
                f.label,
            )

    return tf.data.Dataset.from_generator(
        gen,
        ({"input_ids": tf.int32, "attention_mask": tf.int32,
         "token_type_ids": tf.int32}, tf.int64),
        (
            {
                "input_ids": tf.TensorShape([None]),
                "attention_mask": tf.TensorShape([None]),
                "token_type_ids": tf.TensorShape([None]),
            },
            tf.TensorShape([]),
        ),
    )


DATA_COLUMN = 'DATA_COLUMN'
LABEL_COLUMN = 'LABEL_COLUMN'

train_InputExamples, validation_InputExamples = convert_data_to_examples(
    train, test, DATA_COLUMN, LABEL_COLUMN)

train_data = convert_examples_to_tf_dataset(
    list(train_InputExamples), tokenizer)
train_data = train_data.shuffle(100).batch(32).repeat(2)

validation_data = convert_examples_to_tf_dataset(
    list(validation_InputExamples), tokenizer)
validation_data = validation_data.batch(32)

# check if it is using early stop // use it if not

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(
                  from_logits=True),
              metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')])

model.fit(train_data, epochs=2, validation_data=validation_data)

# Todo use the requested metrics

# Todo save the model to avoid retrain

pred_sentences = ["You are a good person", "You are a stupid person"]

# Todo change pred_sentences to test tweets set

tf_batch = tokenizer(pred_sentences, max_length=128,
                     padding=True, truncation=True, return_tensors='tf')
tf_outputs = model(tf_batch)
tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
labels = ['Hate', 'No Hate']
label = tf.argmax(tf_predictions, axis=1)
label = label.numpy()
for i in range(len(pred_sentences)):
    print(pred_sentences[i], ": \n", labels[label[i]])

# Todo get metrics from test set
