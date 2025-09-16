#!/usr/bin/env python

import sys,os,csv
import base64
import json
import requests
import urllib.error
import msvcrt
import time
import shutil

# 将图片文件转为base64编码
def get_img_base64(img_file):
    with open(img_file, 'rb') as infile:
        s = infile.read()
        b64code = base64.b64encode(s)
        b64code = b64code.decode('utf-8')
        return b64code

# 向服务器发送请求，返回数据
def predict(url, appcode, img_base64, kv_config, old_format):
        if not old_format:
            param = {}
            param['image'] = img_base64
            if kv_config is not None:
                param['configure'] = kv_config
            body = param
        else:
            param = {}
            pic = {}
            pic['dataType'] = 50
            pic['dataValue'] = img_base64
            param['image'] = pic
    
            if kv_config is not None:
                conf = {}
                conf['dataType'] = 50
                conf['dataValue'] = kv_config
                param['configure'] = conf

    
            inputs = { "inputs" : [param]}
            body = inputs


        headers = {'Authorization' : 'APPCODE %s' % appcode}
        body = {"image":img_base64,"configure":{"side":"face"}}
        body = json.dumps(body)

        try:
            response = requests.post(url = url, headers = headers, data = body, timeout = 10)
            return response.status_code, response.headers, response.content
        except urllib.error.HTTPError as e:
            return e.status_code, e.headers, e.content

# 主程序，输入文件，返回信息列表
def demo(img_file):
    appcode = 'your_appcode'
    url = 'http://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json'
    #如果输入带有inputs, 设置为True，否则设为False
    is_old_format = False
    config = {'side':'face'}

    img_base64data = get_img_base64(img_file)
    stat, header, content = predict( url, appcode, img_base64data, config, is_old_format)
    if stat != 200:
        print ('Http status code: ', stat)
        print ('Error msg in header: ', header['x-ca-error-message'] if 'x-ca-error-message' in header else '')
        print ('Error msg in body: ', content)
        print ('按Esc键退出')
        while True:
            if ord(msvcrt.getch()) in [27]:
                exit()
    if is_old_format:
        result = json.loads(content)['outputs'][0]['outputValue']['dataValue']
    else:
        result = content

    # 将返回结果json转换为字典
    result = json.loads(result)
    # 将unicode转化为utf-8编码的字符串
    name = result['name']       
    num = "\'" + result['num']     # 在文字前面加上’ 禁止excel打开csv文件时科学计数法的方式显示数字
    address = result['address']
    # 在返回的字典里提取姓名，身份证号码，住址信息并生成列表
    result_list = []
    result_list.append(name)
    result_list.append(num)
    result_list.append(address)
    return result_list;

# 获取images目录下的所有图片文件名，返回列表
def get_image_filelist():
    if not os.path.isdir('images/identified'):     # 判断identified文件夹是否存在，否则创建之
        os.makedirs('images/identified')
    file = []
    file_path="images/"
    for filenames in os.walk(file_path):
            file.append(filenames)
    filename = file[0]
    filename = filename[2]
    return filename

if __name__ == '__main__':
    with open("idcard.csv","a") as csvfile:
        writer = csv.writer(csvfile,lineterminator='\n')
        # 先写入表字段
        writer.writerow(["name","num","address","写入时间："+str(time.strftime("%Y-%m-%d %H:%M", time.localtime()))])
        serialnum = 1

        files = get_image_filelist()
        # 遍历images文件下的每个图片文件，依次检测并逐行写入csv文件
        for i in files:
            print ('检测完毕，处理中：%d / %s ，开始写入csv文件……' % (serialnum,len(files)))
            s = demo('images/'+i)
            serialnum += 1
            writer.writerow(s)
            try:
                shutil.move('images/'+i,"images/identified/")      # 将已识别的图片移动到identified文件夹
            except:
                pass
        csvfile.close()
        print ('写入csv文件完毕！按Esc键退出')
        while True:
            if ord(msvcrt.getch()) in [27]:
                exit()


