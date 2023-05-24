import numpy as np
import cv2

class EventProcess:
    def set_event(self):
        self.img = cv2.imread(f'{self.cam_path}/transform_img.jpg')
        self.h, self.w = self.img.shape[:2]
        self.actions = {
            ord('e'): self.end_draw,
            ord('s'): self.save_current_mask,
            ord('b'): self.undo_mask,
            27: self.allclean
        }


    def reset(self):
        self.x1, self.y1 = -1, -1
        self.lane = 1
        self.num = 1
        self.points = []
        self.pre = np.array([[0, 0], [self.w, 0]])
        self.origin = self.img.copy()
    
    def event_image(self):
        self.reset()
        cv2.imshow(self.winname_o, self.img)
        cv2.setMouseCallback(self.winname_o, self.find_pixel)
        flag = 0
        while True:
            cv2.imshow(self.winname_o, self.img)
            key = cv2.waitKey(1) & 0xFF

            if key == ord ('q'):
                cv2.destroyWindow(self.winname_o)
                break

            action = self.actions.get(key)
            if action: 
                flag =  action()
            if flag:
                break
        
    def end_draw(self):
        self.points = np.array([[0, self.h], [self.w, self.h]])
        self.draw_space()
        self.action_save()
        self.points = []
        cv2.waitKey(0)
        cv2.destroyWindow(self.winname_o)
        cv2.destroyWindow(self.winmask)
        return 1
    
    def save_current_mask(self):
        self.img = self.origin.copy()
        
        # adjusting space
        self.points[0][0] = 0
        self.points[-1][0] = self.w
        
        self.draw_space()
        self.action_save()
        
        self.lane += 1
        self.pre = self.points.copy()
        self.points = []
        return 0
    
    def undo_mask(self):
        self.img = self.origin.copy()

        if len(self.points) !=0:
            self.points.pop()
        if self.points:
            self.draw_space()

        return 0

    def draw_space(self):
        cv2.fillPoly(self.img, [np.concatenate((self.points, self.pre[::-1]),axis=0)], (0,255/self.lane,0))
        cv2.imshow(self.winname_o, self.img)

    def action_save(self):
        mask = cv2.inRange(self.img, (0,255/self.lane,0), (0,255/self.lane,0))
        cv2.imshow(self.winmask, mask)
        cv2.imwrite(f"{self.cam_path}/lane{self.lane}.jpg", mask)

    def find_pixel(self, event, x, y, flags, param):
        global x1,y1

        if event == cv2.EVENT_LBUTTONDOWN:                      # 마우스를 누른 상태
            self.x1, self.y1 = x,y
            cv2.imshow(self.winname_o, self.img)
            self.points.append([x,y])
            self.draw_space()