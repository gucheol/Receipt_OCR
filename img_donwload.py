import numpy as np
import cv2, json, requests, csv, os, argparse
from tqdm import tqdm
from requests.structures import CaseInsensitiveDict

class Receipt(object):
    def __init__(self, args, img_info):
        self.root_path = args.root_path
        self.token = 'Bearer '+ args.token
        self.info = img_info
        self.image = self.get_image()
        # self.show_img() # 디버그용

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
        save_folder_path = os.path.join(self.root_path, 'images')
        if not os.path.exists(save_folder_path):
            os.makedirs(save_folder_path)
        save_path = os.path.join(save_folder_path, file_name)
        cv2.imwrite(save_path, self.image)

    def save_csv(self):
        file_name = 'receipts_info.csv'
        file_path = os.path.join(self.root_path, file_name)
        with open(file_path, 'a') as csv_f:
            fieldnames= self.info.keys()
            writer = csv.DictWriter(csv_f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(self.info)

class Utils(object):
    def open_info_file(self, file_path):
        with open(file_path, 'r', encoding='utf8') as f:
            data = f.readlines()
            img_info = data[-1]
            img_infos = json.loads(img_info)
        return img_infos

    def del_old_csv(self, root_path):
        file_name = 'receipts_info.csv'
        file_path = os.path.join(root_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def main(args):
    # info 파일 읽고 이미 있는 csv 파일 지움
    utils = Utils()
    img_infos = utils.open_info_file(args.info_file)
    utils.del_old_csv(args.root_path)

    # 이미지 하나씩 저장 및 csv에 기록
    for img_info in tqdm(img_infos):
        receipt = Receipt(args, img_info)
        receipt.save_image()
        receipt.save_csv()

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
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_path', default=root_path)
    parser.add_argument('--image_folder', default=f'{root_path}/images')
    parser.add_argument('--info_file', default=f'{root_path}/nuli_data/SSEM BOOK IMAGES_20210609.ssem')
    parser.add_argument('--token')

    args = parser.parse_args()

    main(args)
    