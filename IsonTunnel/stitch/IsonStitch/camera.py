import cv2
import numpy as np
import json

from IsonTunnel.configure import CONFIG_ROOT

class Camera:
    def __init__(self, cam_id, image):
        self.cam_id = cam_id
        self.cam_path = f'{CONFIG_ROOT}/field/cam{cam_id}'
        self.params = json.load(open(f"{self.cam_path}/params.json"))
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta_deg = self.params['theta']
        self.cross_point_left = self.params['left_point']
        self.cross_point_right = self.params['right_point']

        h, w = image.shape[:2]

        self.get_fisheye_map([h, w], self.K, self.D, raw_view=0)
        self.matrix = cv2.getRotationMatrix2D((int(w/2),int(h/2)), float(self.theta_deg), 1.0)

    def get_fisheye_map(self, image_shape:list,K_coff,D_coff,raw_view=False):
        img_height,img_width = image_shape
        DIM = [img_width,img_height]
        balance_value = 0
        if(raw_view):
            balance_value = 1

        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K_coff, D_coff, DIM, np.eye(3), balance=balance_value)
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(K_coff, D_coff, np.eye(3), new_K, DIM, cv2.CV_16SC2)

    def transform_calib(self, image):
        h, w = image.shape[:2]
        undistorted_img = cv2.remap(image, self.map1, self.map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        transform_img = cv2.warpAffine(undistorted_img, self.matrix, (w, h))
        return transform_img

    def transform_stit(self, image, offset = 100):
        left_len = len(self.cross_point_left);
        right_len = len(self.cross_point_right);
        img_h, img_w = image.shape[:2];
        img_h = 800
        if(left_len!=right_len):
            print("problem left_len != right_len");
            return None;

        tranfom_img_w = img_w+offset;
        tranfom_img_h = int(img_h/(left_len-1));

        tranfom_img_list = [];

        for idx_,(l_bottom_pos,r_bottom_pos) in enumerate(zip(self.cross_point_left, self.cross_point_right)):
            if(idx_==0):
                continue;#skip first work
            l_top_pos,r_top_pos = self.cross_point_left[idx_-1], self.cross_point_right[idx_-1];

            l_t_x,l_t_y=l_top_pos;
            r_t_x,r_t_y=r_top_pos;

            l_b_x,l_b_y=l_bottom_pos;
            r_b_x,r_b_y=r_bottom_pos;

            point1=[    [l_t_x,l_t_y],
                        [l_b_x,l_b_y],
                        [r_t_x,r_t_y],
                        [r_b_x,r_b_y]];
            
            point2=[    [offset,0],
                        [offset,tranfom_img_h],
                        [tranfom_img_w,0],
                        [tranfom_img_w,tranfom_img_h]];
            
            M = cv2.getPerspectiveTransform(np.float32(point1), np.float32(point2))

            unvanishing_imaga_dst = cv2.warpPerspective(image, M, (img_w+int(offset*2),tranfom_img_h));
            tranfom_img_list.append(unvanishing_imaga_dst);

        return np.concatenate(tranfom_img_list,axis=0)


def create_outline_mask(image_size=(0, 0),offset = 0):
    # 이미지 사이즈 얻기
    width,hight = image_size
    
    # 이미지 양끝으로부터 offset 크기에 맞춘 mask 생성
    mask = np.full_like(np.ones((hight,int(2*offset),3)), 255)

    # linear 세팅 : 왼쪽부터 1 ~ 0 사이 값을 가짐;
    for i in range(int(2*offset)):
        mask[:,i] = 1.0 - (1.0*(i/(2*offset)))
    
    return mask

def stitch_blending(img_array,mask=None,inv_mask=None):
    blending_img = []
    _, mask_w = mask.shape[:2]
    x_offset = int(mask_w/2)
    if (mask_w>0):
        for idx_ in range(len(img_array)-1):
                # 오른쪽 사이드 이미지 blending
                img_array[idx_][:,-mask_w:] =  mask*img_array[idx_][:,-mask_w:] + inv_mask*img_array[idx_+1][:,:mask_w]
                # 왼쪽 사이드 이미지 blending
                img_array[idx_+1][:,:mask_w] =  inv_mask*img_array[idx_][:,-mask_w:] + mask*img_array[idx_+1][:,:mask_w]
                
                # 양(왼쪽,오른쪽) 사이드 blending 처리된 이미지 보관
                blending_img.append(img_array[idx_][:,x_offset:-x_offset])
        # blending 처리된 마지막 이미지 보관
        blending_img.append(img_array[len(img_array)-1][:,x_offset:-x_offset])
    else:
        blending_img = img_array;
    # 가로 stitch 적업
    return np.concatenate(blending_img,axis=1)

