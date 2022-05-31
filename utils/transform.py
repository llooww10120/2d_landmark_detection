import torch
from torchvision.transforms import transforms
import torchvision.transforms.functional as F
import random
import math

class RandomRoation(object):
    def __init__(self, model_type:str, img_shape:tuple=(384,384,3), prob=0.5, angle=(-30, 30)):
        """Random roation
        Args:
            img_shape: the shape of input image, must be (h,w,c)
        """
        self.prob = prob
        self.angle = angle

        self.angle_list = [self.angle[0] + i for i in range(self.angle[1] - self.angle[0])]
        self.img_shape = img_shape
        self.model_type = model_type
        if self.model_type == "classifier":
            self.scale_ratio = 0.25
        else:
            self.scale_ratio = 1.0

        self._generate_rotation_matrix()

    def _generate_rotation_matrix(self):
        h, w, c = self.img_shape
        self.rot_matrices = []

        for angle in self.angle_list:
            degree = angle / (180 / math.pi)
            cos , sin = math.cos(degree), math.sin(degree) 
            rot_matrix = torch.tensor([[cos, sin],[-sin, cos]])
            self.rot_matrices.append(rot_matrix.float())

    @staticmethod
    def _rotate_points(points, w, h, rot_matrix):
        center = torch.tensor([[w / 2, h / 2]])
        points -= center
        points = torch.matmul(rot_matrix, points.T)
        points = points.T + center
        return points

    def __call__(self, img, label:torch.Tensor, gt_label:torch.Tensor):
        if random.random() < self.prob:
            h, w, c = self.img_shape
            
            angle_i = random.randint(0, len(self.angle_list)-1)
            angle = self.angle_list[angle_i]
            img = F.rotate(img, angle)

            rot_matrix = self.rot_matrices[angle_i]

            # Rotate groud truth label
            r_gt_label = self._rotate_points(gt_label, w, h, rot_matrix)

            if (r_gt_label < 0).any() or (r_gt_label >= h).any():
                return img, label, gt_label

            # Rotate label
            r_label = self._rotate_points(label.float(), w * self.scale_ratio, h * self.scale_ratio, rot_matrix)
            if (r_label < 0).any() or (r_label >= h * self.scale_ratio).any():
                return img, label, gt_label

            # Convert to integer
            if self.model_type == "classifier":
                r_label = r_label.long()

            return img, r_label, r_gt_label

        return img, label, gt_label

class RandomHorizontalFlip(object):
    def __init__(self, model_type:str, flip_x=0.5):
        self.flip_x = flip_x
        self.model_type =model_type
        self.mapping = [[0, 1, 2, 3, 4, 5, 6, 7, 17, 18, 19, 20, 21, 36, 37, 38, 39, 41, 40, 31, 32, 50, 49, 48, 61, 60, 67, 59, 58], 
                        [16, 15, 14, 13, 12, 11, 10, 9, 26, 25, 24, 23, 22, 45, 44, 43, 42, 46, 47, 35, 34, 52, 53, 54, 63, 64, 65, 55, 56]]
        self.do_mapping = True
    def __call__(self, img, label:torch.Tensor, gt_label:torch.Tensor):
        """
        Args:
            img: the PIL image
        """
        h, w = img.size
        if self.model_type == "classifier":
            max_size_on_label = int(h / 4)
        else:
            max_size_on_label = h
        max_size = h
        if random.random() < self.flip_x:
            img = F.hflip(img) #transforms.RandomHorizontalFlip(1.0)(img)

            # Flip x coordinate
            label[:, 0] = (max_size_on_label - 1) - label[:, 0]
            gt_label[:, 0] = (max_size - 1) - gt_label[:, 0]
            if self.do_mapping:
                tmp = label[self.mapping[1], ...].clone()
                label[self.mapping[1], ...] = label[self.mapping[0], ...]
                label[self.mapping[0], ...] = tmp

                tmp = gt_label[self.mapping[1], ...].clone()
                gt_label[self.mapping[1], ...] = gt_label[self.mapping[0], ...]
                gt_label[self.mapping[0], ...] = tmp
        return img, label, gt_label

class RandomNoise(object):
    def __init__(self, prob=0.5, ratio=0.1):
        self.prob = prob
        self.ratio = ratio
    def __call__(self, img):
        c, h, w = img.shape
        if random.random() < self.prob:
            noise_num = int(random.random() * self.ratio * h * w)
            for _ in range(noise_num):
                prob = random.random()
                pos_x = int((w - 1) * random.random())
                pos_y = int((h - 1) * random.random())
                if prob > 0.5:
                    img[:,pos_y, pos_x] = 0.0
                else:
                    img[:,pos_y, pos_x] = 1.0 
        return img

class Transform(object):
    def __init__(self, model_type:str, is_train=True):
        self.is_train = is_train
        self.model_type = model_type
        means = [0.485, 0.456, 0.406]
        stds = [0.229, 0.224, 0.225]
        self.normalize = transforms.Normalize(means, stds)
        
        if self.is_train:
            self.random_flip = RandomHorizontalFlip(model_type=self.model_type)
            self.random_noise = RandomNoise()
            self.random_rotation = RandomRoation(model_type=self.model_type)
    def __call__(self, img, label, gt_label):
        label = label.clone()
        gt_label = gt_label.clone()
        if self.is_train:
            # # Random flip
            # img, label, gt_label = self.random_flip(img, label, gt_label)
            # Random rotation
            img, label, gt_label = self.random_rotation(img, label, gt_label)

        img = transforms.ToTensor()(img)

        # Random noise
        if self.is_train:
            img = self.random_noise(img)

        img = self.normalize(img)
        return img, label, gt_label


def get_transform(model_type:str="classifier", data_type="train"):
    if data_type == "train":
        transform = Transform(is_train=True, model_type=model_type)
    elif data_type == "test" or data_type == "val":
        transform = Transform(is_train=False, model_type=model_type)
    return transform
