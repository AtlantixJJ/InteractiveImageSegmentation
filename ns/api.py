# coding: utf-8
from __future__ import print_function
import sys
sys.path.insert(0, "/mnt/share/atlantix/AP/ns")
sys.path.insert(0, "/mnt/share/atlantix/AP/ns/preprocessing")
import tensorflow as tf
from preprocessing.vgg_preprocessing import normal_process
import model
import time
import os

tf.app.flags.DEFINE_string('loss_model', 'vgg_16', 'The name of the architecture to evaluate. '
                           'You can view all the support models in nets/nets_factory.py')
tf.app.flags.DEFINE_integer('image_size', 256, 'Image size to train.')
tf.app.flags.DEFINE_string("model_file", "models.ckpt", "")
tf.app.flags.DEFINE_string("image_file", "a.jpg", "")

FLAGS = tf.app.flags.FLAGS

class NeuralStyle(object):
    def __init__(self, model_file="models/feathers.ckpt-done"):
        self.model_file = model_file
        tf.logging.info("Loading model.")
        self.__load_model()
        tf.logging.info("Ready.")
    
    def __load_model(self):
        self.image_t = tf.placeholder(tf.float32, [None, None, 3], "image")
        # Get image's height and width.
        self.height = tf.shape(self.image_t)[0]
        self.width = tf.shape(self.image_t)[1]

        self.G = tf.Graph()
        self.sess = tf.Session()

        image = normal_process(self.image_t)

        # Add batch dimension
        image = tf.expand_dims(image, 0)

        generated = model.net(image, training=False)
        generated = tf.cast(generated, tf.uint8)

        # Remove batch dimension
        self.generated = tf.squeeze(generated, [0])

        # Restore model variables.
        saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V1)
        self.sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
        # Use absolute path
        self.model_file = os.path.abspath(self.model_file)
        saver.restore(self.sess, self.model_file)

    def stylize_single(self, img):
        return self.sess.run([self.generated], {self.image_t: img})[0]

def main(model_file, image_file):

    # Get image's height and width.
    height = 0
    width = 0
    with open(FLAGS.image_file, 'rb') as img:
        with tf.Session().as_default() as sess:
            if FLAGS.image_file.lower().endswith('png'):
                image = sess.run(tf.image.decode_png(img.read()))
            else:
                image = sess.run(tf.image.decode_jpeg(img.read()))
            height = image.shape[0]
            width = image.shape[1]
    tf.logging.info('Image size: %dx%d' % (width, height))

    with tf.Graph().as_default():
        config = tf.ConfigProto();config.gpu_options.allow_growth = True
        with tf.Session(config=config).as_default() as sess:

            # Read image data.
            image_preprocessing_fn, _ = preprocessing_factory.get_preprocessing(
                FLAGS.loss_model,
                is_training=False)
            image = reader.get_image(FLAGS.image_file, height, width, image_preprocessing_fn)

            # Add batch dimension
            image = tf.expand_dims(image, 0)

            generated = model.net(image, training=False)
            generated = tf.cast(generated, tf.uint8)

            # Remove batch dimension
            generated = tf.squeeze(generated, [0])

            # Restore model variables.
            saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V1)
            sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
            # Use absolute path
            FLAGS.model_file = os.path.abspath(FLAGS.model_file)
            saver.restore(sess, FLAGS.model_file)

            # Make sure 'generated' directory exists.
            generated_file = 'generated/res.jpg'
            if os.path.exists('generated') is False:
                os.makedirs('generated')

            # Generate and write image data to file.
            with open(generated_file, 'wb') as img:
                start_time = time.time()
                img.write(sess.run(tf.image.encode_jpeg(generated)))
                end_time = time.time()
                tf.logging.info('Elapsed time: %fs' % (end_time - start_time))

                tf.logging.info('Done. Please check %s.' % generated_file)


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run()
