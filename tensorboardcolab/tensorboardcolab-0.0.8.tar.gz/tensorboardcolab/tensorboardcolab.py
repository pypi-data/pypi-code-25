import tensorflow as tf
from keras.callbacks import TensorBoard
import time
import os
import io

class TensorBoardColab:
    def __init__(self, port=6006, graph_path='./Graph', startup_waiting_time=5):
        self.port = port
        self.graph_path = graph_path
        self.writer = None
        self.deep_writers = {}
        get_ipython().system_raw('npm i -s -q -g ngrok')

        setup_passed = False
        retry_count = 0
        sleep_time = startup_waiting_time / 3.0
        while not setup_passed:
            get_ipython().system_raw('kill -9 $(sudo lsof -t -i:%d)' % port)
            get_ipython().system_raw('rm -Rf ' + graph_path)
            print('Wait for %d seconds...' % startup_waiting_time)
            time.sleep(sleep_time)
            get_ipython().system_raw('tensorboard --logdir %s --host 0.0.0.0 --port %d &' % (graph_path, port))
            time.sleep(sleep_time)
            get_ipython().system_raw('ngrok http %d &' % port)
            time.sleep(sleep_time)
            try:
                tensorboard_link = get_ipython().getoutput(
                    'curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin))"')[
                    0]
                tensorboard_link = eval(tensorboard_link)['tunnels'][0]['public_url']
                setup_passed = True
            except:
                setup_passed = False
                retry_count += 1
                print('Setup not passed, retry again (%d)' % retry_count)
                print('\n')

        print("TensorBoard link:")
        print(tensorboard_link)

    def get_graph_path(self):
        return self.graph_path

    def get_writer(self):
        if self.writer is None:
            self.writer = tf.summary.FileWriter(self.graph_path)

        return self.writer

    def get_deep_writers(self, name):
        if not (name in self.deep_writers):
            log_path = os.path.join(self.graph_path, name)
            self.deep_writers[name] = tf.summary.FileWriter(log_path)
        return self.deep_writers[name]

    def save_image(self, title, image):
        image_path = os.path.join(self.graph_path, 'images')
        summary_op = tf.summary.image(title, image)
        with tf.Session() as sess:
            summary = sess.run(summary_op)
            writer = tf.summary.FileWriter(image_path)
            writer.add_summary(summary)
            writer.close()

    def save_value(self, graph_name, line_name, epoch, value):
        summary = tf.Summary()
        summary_value = summary.value.add()
        summary_value.simple_value = value
        summary_value.tag = graph_name
        self.get_deep_writers(line_name).add_summary(summary, epoch)

    def flush_line(self, line_name):
        self.get_deep_writers(line_name).flush()

    def close(self):
        if self.writer is not None:
            self.writer.close()
            self.writer = None

        for key in self.deep_writers:
            self.deep_writers[key].close()
        self.deep_writers = {}

class TensorBoardColabCallback(TensorBoard):
    def __init__(self, tbc=None, write_graph=True, **kwargs):
        # Make the original `TensorBoard` log to a subdirectory 'training'

        if tbc is None:
            return

        log_dir = tbc.get_graph_path()

        training_log_dir = os.path.join(log_dir, 'training')
        super(TensorBoardColabCallback, self).__init__(training_log_dir, **kwargs)

        # Log the validation metrics to a separate subdirectory
        self.val_log_dir = os.path.join(log_dir, 'validation')

    def set_model(self, model):
        # Setup writer for validation metrics
        self.val_writer = tf.summary.FileWriter(self.val_log_dir)
        super(TensorBoardColabCallback, self).set_model(model)

    def on_epoch_end(self, epoch, logs=None):
        # Pop the validation logs and handle them separately with
        # `self.val_writer`. Also rename the keys so that they can
        # be plotted on the same figure with the training metrics
        logs = logs or {}
        val_logs = {k.replace('val_', ''): v for k, v in logs.items() if k.startswith('val_')}

        for name, value in val_logs.items():
            # print('val_logs:',epoch, name, value)
            summary = tf.Summary()
            summary_value = summary.value.add()
            summary_value.simple_value = value.item()
            summary_value.tag = name
            self.val_writer.add_summary(summary, epoch)
        self.val_writer.flush()

        # Pass the remaining logs to `TensorBoard.on_epoch_end`
        logs = {k: v for k, v in logs.items() if not k.startswith('val_')}
        super(TensorBoardColabCallback, self).on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None):
        super(TensorBoardColabCallback, self).on_train_end(logs)
        self.val_writer.close()