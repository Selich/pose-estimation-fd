import argparse
from openpose.native.op_py.utils import str2bool


def get_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Extract skeleton using OPENPOSE')

    # OPEN POSE OPTIONS --------------------------------------------------------
    p.add_argument('--op-model-folder',
                   type=str,
                   default="/usr/local/src/openpose/models/",
                   help='folder with trained openpose models.')
    p.add_argument('--op-model-pose',
                   type=str,
                   default="BODY_25",
                   help='pose model name')
    p.add_argument('--op-net-resolution',
                   type=str,
                   default="-1x368",
                   help='resolution of input to openpose.')
    p.add_argument('--op-skel-thres',
                   type=float,
                   default=0.3,
                   help='threshold for valid skeleton.')
    p.add_argument('--op-max-true-body',
                   type=int,
                   default=12,
                   help='max number of skeletons to save.')
    p.add_argument('--op-heatmaps-add-parts',
                   type=str2bool,
                   default=False,
                   help='')
    p.add_argument('--op-heatmaps-add-bkg',
                   type=str2bool,
                   default=False,
                   help='')
    p.add_argument('--op-heatmaps-add-PAFs',
                   type=str2bool,
                   default=False,
                   help='')
    p.add_argument('--op-heatmaps-scale',
                   type=int,
                   default=1,
                   help='')

    # DEPTH OPTIONS ------------------------------------------------------------
    p.add_argument('--op-patch-offset',
                   type=int,
                   default=2,
                   help='offset of patch used to determine depth')
    p.add_argument('--op-ntu-format',
                   type=str2bool,
                   default=False,
                   help='whether to use coordinate system of NTU')

    # DISPLAY OPTIONS ----------------------------------------------------------
    p.add_argument('--op-display',
                   type=int,
                   default=0,
                   help='scale for displaying skel images.')
    p.add_argument('--op-display-depth',
                   type=int,
                   default=0,
                   help='scale for displaying skel images with depth.')

    # REALSENSE OPTIONS --------------------------------------------------------
    p.add_argument('--op-rs-dir',
                   type=str,
                   default='openpose/data/mot17',
                   help='path to folder with saved rs data.')
    p.add_argument('--op-rs-image-width',
                   type=int,
                   default=1920,
                   help='image width in px')
    p.add_argument('--op-rs-image-height',
                   type=int,
                   default=1080,
                   help='image height in px')
    p.add_argument('--op-rs-save-skel',
                   type=str2bool,
                   default=True,
                   help='if true, saves the 2d skeleton.')
    p.add_argument('--op-rs-save-skel-image',
                   type=str2bool,
                   default=False,
                   help='if true, saves the 2d skeleton image.')
    p.add_argument('--op-rs-extract-3d-skel',
                   type=str2bool,
                   default=False,
                   help='if true, tries to extract 3d skeleton.')
    p.add_argument('--op-rs-save-3d-skel',
                   type=str2bool,
                   default=False,
                   help='if true, saves the 3d skeleton.')
    p.add_argument('--op-rs-delete-image',
                   type=str2bool,
                   default=False,
                   help='if true, deletes the rs image used in inference.')
    return p