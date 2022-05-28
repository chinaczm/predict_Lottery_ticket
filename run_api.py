# -*- coding:utf-8 -*-
"""
Author: BigCat
"""
import json
import time
import datetime
import numpy as np
import tensorflow as tf
from config import *
from flask import Flask
from get_train_data import get_current_number, spider, pd
from get_train_data_new import spider_predict, aim_dict, get_latest_issue

# 关闭eager模式
tf.compat.v1.disable_eager_execution()

red_graph = tf.compat.v1.Graph()
with red_graph.as_default():
    red_saver = tf.compat.v1.train.import_meta_graph("{}red_ball_model.ckpt.meta".format(red_ball_model_path))
red_sess = tf.compat.v1.Session(graph=red_graph)
red_saver.restore(red_sess, "{}red_ball_model.ckpt".format(red_ball_model_path))
print("[INFO] 已加载红球模型！")

# 加载关键节点名
with open("{}{}".format(model_path, pred_key_name)) as f:
    pred_key_d = json.load(f)

app = Flask(__name__)


def get_year():
    """ 截取年份
    eg：2020-->20, 2021-->21
    :return:
    """
    return int(str(datetime.datetime.now().year)[-2:])


@app.route('/')
def main():
    return "Welcome to use!"


@app.route('/predict_api', methods=['GET'])
def get_predict_result():
    diff_number = windows_size - 1
    total_data = spider_predict('predict')
    print(total_data)
    first_issue = get_latest_issue() + 1
    #red_name_list = [(BOLL_NAME[0], i + 1) for i in range(sequence_len)]
    #red_data = total_data[["{}号码_{}".format(name[0], i) for name, i in red_name_list]].values.astype(int) - 1
    final_result = {}
    for i in range(0, len(total_data) - 3):
        data = []
        issue_number = first_issue - i
        print(issue_number)
        data.append(total_data[i])
        data.append(total_data[i + 1])
        data.append(total_data[i + 2])
        print(data)
        # 预测红球
        with red_graph.as_default():
            reverse_sequence = tf.compat.v1.get_default_graph().get_tensor_by_name(pred_key_d[BOLL_NAME[0][0]])
        red_pred = red_sess.run(reverse_sequence, feed_dict={
            "red_inputs:0": np.array(data).reshape(1,3,13),
            "sequence_length:0": np.array([sequence_len] * 1)
        })
        result = red_pred[0]
        final_result[issue_number] = aim_dict[str(result[12])]
    return json.dumps(
        final_result
    ).encode('utf-8').decode('unicode_escape')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
