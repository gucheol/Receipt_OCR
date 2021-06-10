import numpy as np
import cv2, json, requests, csv
from requests.structures import CaseInsensitiveDict

##########  이미지   #######################################

############ image info 파일 ###############################
def open_info_file(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        data = f.readlines()
        img_info = data[-1]
    img_infos = json.loads(img_info)
    return img_infos



class Receipt(object):
    def __init__(self, img_info):
        self.token = 'Bearer '+'6H6A0dEoX4asw2Kg83BDrg=='
        self.info = self.get_info(img_info)
        self.image = self.get_image()
        self.show_img() # 디버그용

    def get_info(self, img_info):
        info = {
            'FILE_UUID' : img_info['FILE_UUID'],
            'IO_TP' : img_info['IO_TP'],
            'TRX_DV' : img_info['TRX_DV'],
            'CLNT_ID' : img_info['CLNT_ID'],
            'CLNT_NM' : img_info['CLNT_NM'],
            'TOT_AMT' : img_info['TOT_AMT'],
            'SPL_AMT' : img_info['SPL_AMT'],
            'TAX_AMT' : img_info['TAX_AMT'],
            'IMAGE_URL' : img_info['IMAGE_URL']
        }
        return info

    def get_image(self):
        byte_str_image = self.request_image()
        img = self.convert_np_image(byte_str_image)
        return img

    def request_image(self):
        headers = CaseInsensitiveDict()
        headers["Authorization"] = self.token

        response = requests.get(self.info['IMAGE_URL'], headers=headers)
        byte_str_image = response.content
        return byte_str_image

    def convert_np_image(self, byte_str_image):
        nparr = np.frombuffer(byte_str_image, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
        return img_np

    def show_img(self, resize_ratio=0.5):
        image = self.image
        img_h, img_w, _ = image.shape
        img_resize = cv2.resize(image, (int(img_w*resize_ratio), int(img_h*resize_ratio)))
        cv2.imshow('',img_resize)
        cv2.waitKey(0)

    def save_image(self):
        file_name = f"{self.info['FILE_UUID']}.jpg"
        cv2.imwrite(file_name, self.image)

    def save_csv(self):
        file_name = 'receipts_info.csv'
        # with open(file_name, 'w') as csv_f:
        #     writer = csv.DictWriter(csv_f)
        #     writer.writeheader()
        #     for data in dict_data:
        #         writer.writerow(data)

if __name__ == '__main__':
    
    # key_meaning = {
    #     'FILE_UUID' : '파일일련번호', 
    #     'IO_TP' : '매입매출구분',
    #     'TRX_DV' : '거래유형',
    #     'CLNT_ID' : '거래처사업자번호',
    #     'CLNT_NM' : '거래처명',
    #     'TOT_AMT' : '총거래금액',
    #     'SPL_AMT' : '공급가액',
    #     'TAX_AMT' : '부가세액'
    # }


    file_path = '/home/gucheol/다운로드/SSEM BOOK IMAGES_20210609.ssem'
    img_infos = open_info_file(file_path)

    for img_info in img_infos:
        receipt = Receipt(img_info)
        receipt.save_image()

