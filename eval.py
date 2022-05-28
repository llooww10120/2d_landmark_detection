import torch
from torch.utils.data import DataLoader
import argparse
from utils.evaluation import *
from utils.model import FAN
from utils.dataset import get_transform, process_annot, FaceSynthetics
from utils.tool import load_parameters, val
from cfg import cfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_HG', type=int, default=4)
    parser.add_argument('--model_path', type=str)
    parser.add_argument('--annot_path', type=str, default="./data/val_annot.pkl")
    parser.add_argument('--data_path', type=str, default="./data/val")
    args = parser.parse_args()

    annot_path = args.annot_path
    data_path = args.data_path
    batch_size = cfg['batch_size']

    images, labels, gt_labels = process_annot(annot_path)
    test_set = FaceSynthetics(data_path, images, labels, gt_labels, "test")
    test_loader = DataLoader(test_set, batch_size=batch_size, num_workers= 2, pin_memory=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = FAN(num_HG=args.num_HG)
    load_parameters(model, args.model_path)
    val(model, test_loader, device)


if __name__ == "__main__":
    main()