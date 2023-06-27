import cv2
import numpy as np
import json

class StitchProcess:
    def set_stit(self):
        self.img = cv2.imread(f'{self.cam_path}/lanes.jpg')
        self.K = np.array(self.params['K'])
        self.D = np.array(self.params['D'])
        self.theta = self.params['theta']
        self.cross_point_left = self.params['left_point']
        self.cross_point_right = self.params['right_point']
        self.h, self.w = self.img.shape[:2]
        self.transform()
        self.draw_img = self.transform_img.copy()
        self.actions = {
            81: self.update_line_right, # 방향키
            83: self.update_line_left, # 방향키
            82: self.update_line_up, # 방향키
            84: self.update_line_down, # 방향키

            ord('n'): self.change_line, 
            ord('1'): self.get_cross_points,
            225: self.change_step, # shift
            ord('s'): self.line_save,

            ord('='): self.show_draw_points,

            ord('2'): self.save_stitch_config,
            ord('3'): self.transform_stit,
            
            27: self.allclean
        }
        self.theta_deg = 90
        self.x_offset = int(self.draw_img.shape[1] / 2)
        self.y_offset = int(self.draw_img.shape[0] / 2)
        self.line_info_list1 = []
        self.line_info_list2 = []

        self.state=0
        self.key = 0 
        self.x_unit = 1
        self.x_unit1 = 1
        self.x_unit2 = 10

        self.theta_unit = 0.1
        self.theta_unit1 = 0.1
        self.theta_unit2 = 1.0

    def save_stitch_config(self):
        save_dict = self.params
        save_dict['left_point'] = self.cross_point_left
        save_dict['right_point'] = self.cross_point_right
        with open(self.param_path, "w") as write_file:
            json.dump(save_dict, write_file, indent=3)
        cv2.imwrite(f'{self.cam_path}/transform_img.jpg', self.transform_img)

    def get_keypoint(self):
        trigger = 0
        self.draw_img = self.transform_img
        if self.state==0:
            self.draw_img = self.draw_line([np.deg2rad(self.theta_deg), self.x_offset])
        if self.state==1:
            self.draw_img = self.draw_h_line(self.y_offset)
        
        for line_ in self.line_info_list1:
            self.draw_img = self.draw_line(line_)
        for line_ in self.line_info_list2:
            self.draw_img = self.draw_h_line(line_)

        

        cv2.imshow(self.winname_d, self.draw_img)
        key = cv2.waitKey(1) & 0xFF
        action = self.actions.get(key)
        if action: action()

        if key == ord ('q'):
            self.get_cross_points()
            cv2.destroyWindow(self.winname_d)

            trigger=1
        
        return trigger

    def update_line_up(self):
        if self.state==0:
            self.theta_deg += self.theta_unit
        elif self.state==1:
            self.y_offset -= self.x_unit

    def update_line_down(self):
        if self.state==0:
            self.theta_deg -= self.theta_unit
        elif self.state==1:
            self.y_offset += self.x_unit

    def update_line_right(self):
        self.x_offset -= self.x_unit
        
    def update_line_left(self):
        self.x_offset += self.x_unit
    
    def change_line(self):
        if self.state==0:
            self.state=1
        elif self.state==1:
            self.state=0

    def change_step(self):
        if(self.x_unit == self.x_unit1):
            self.x_unit = self.x_unit2
        else:
            self.x_unit = self.x_unit1

        if(self.theta_unit > 0.99):
            self.theta_unit = self.theta_unit1
        else:
            self.theta_unit = self.theta_unit2
    
    def line_save(self):
        if self.state==0:
            self.line_info_list1.append([np.deg2rad(self.theta_deg), self.x_offset])
        elif self.state==1:
            self.line_info_list2.append(self.y_offset)
    
    def get_cross_points(self):
        self.line_info_list1 = sorted(self.line_info_list1, key=lambda line_info: line_info[0],reverse=True)
        self.line_info_list2 = sorted(self.line_info_list2, key=lambda line_info: line_info)

        result, points = self.get_cross_point()
        points_length = len(points)
        
        self.cross_point_left, self.cross_point_right = points[:int(points_length/2)], points[int(points_length/2):]
        print(self.cross_point_left, self.cross_point_right)

    def draw_line(self, line_info, color = [0,0,255]):
        theta_angle, x_offset = line_info
        x_dir,y_dir = np.cos(theta_angle),np.sin(theta_angle)
        img_H,img_W = self.draw_img.shape[:2]
        temp_img = self.draw_img.copy()
        unit_dir = np.array([x_dir,y_dir])
        offset = np.array([x_offset,0])

        points_ = np.array([np.int32(offset+ (unit_dir*float(scale_)) ) for scale_ in range( 0, img_W ) ])

        for point_ in points_:
            x_,y_ = point_
            if((x_  >= img_W) or (x_  < 0)):
                break
            if((y_  >= img_H) or (y_  < 0)):
                break
            temp_img[y_,x_] = color
        
        return temp_img

    def draw_h_line(self, line_info, color = [255,0,0]):
        y_offset = line_info;
        temp_img = self.draw_img.copy()
        temp_img[y_offset,:] = color
        return temp_img

    def get_cross_point(self):
        # reference : https://gaussian37.github.io/math-algorithm-intersection_point/
        point_list = [];
# self.line_info_list1, self.line_info_list2
        for h_line_info in self.line_info_list1:
            theta_angle, x_offset = h_line_info
            x_dir,y_dir = np.cos(theta_angle), np.sin(theta_angle)
            
            
            if(x_dir>0.0001 or x_dir<-0.0001):
                a1 = 1.0 / x_dir
                b1 = -1.0 / y_dir
                c1 = -x_offset / x_dir
            else:
                a1 = 1
                b1 = 0
                c1 = -x_offset


            for w_line_info in self.line_info_list2:
                y_offset = w_line_info
                a2 = 0
                b2 = 1
                c2 = -y_offset

                return_condition = (b1 == 0.0) or ((a1*b2-a2*b1) == 0.0)

                if(return_condition):
                    point_list.append([x_offset,y_offset])
                    continue
            
                px,py = [(b1*c2-b2*c1)/(a1*b2-a2*b1), ((-a1/b1)*((b1*c2-b2*c1)/(a1*b2-a2*b1))) - (c1/b1) ]
                point_list.append([int(px), int(py)])
        
        return True, point_list
    
    def show_draw_points(self):
        for point1, point2 in zip(self.cross_point_left, self.cross_point_right): 
            print(point1[0], point1[1])
            cv2.circle(self.transform_img, (point1[0], point1[1]), 4, (255, 255, 255), -1)
            cv2.circle(self.transform_img, (point2[0], point2[1]), 4, (0, 0, 0), -1)


    def transform_stit(self, offset = 100):
        left_len = len(self.cross_point_left);
        right_len = len(self.cross_point_right);
        img_h, img_w = self.transform_img.shape[:2];
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

            unvanishing_imaga_dst = cv2.warpPerspective(self.transform_img, M, (img_w+int(offset*2),tranfom_img_h));
            tranfom_img_list.append(unvanishing_imaga_dst);

        self.stitch_img = np.concatenate(tranfom_img_list,axis=0)
        print(self.stitch_img.shape)