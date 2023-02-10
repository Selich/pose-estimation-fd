import argparse
import cv2
import numpy as np
import os
import time
from tqdm import trange

from typing import Optional


from openpose.native import PyOpenPoseNative
from openpose.native.op_py.utils import get_rs_sensor_dir
from openpose.native.op_py.utils import read_calib_file
from openpose.native.op_py.utils import read_color_file
from openpose.native.op_py.utils import read_depth_file


def str2bool(v) -> bool:
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Extract 3D skeleton using OPENPOSE')
    # MAIN
    parser.add_argument('--op-model-folder',
                        type=str,
                        default="/usr/local/src/openpose/models/",
                        help='folder with trained openpose models.')
    parser.add_argument('--op-model-pose',
                        type=str,
                        default="BODY_25",
                        help='pose model name')
    parser.add_argument('--op-net-resolution',
                        type=str,
                        default="-1x368",
                        help='resolution of input to openpose.')
    parser.add_argument('--op-skel-thres',
                        type=float,
                        default=0.5,
                        help='threshold for valid skeleton.')
    parser.add_argument('--op-max-true-body',
                        type=int,
                        default=2,
                        help='max number of skeletons to save.')
    parser.add_argument('--op-patch-offset',
                        type=int,
                        default=2,
                        help='offset of patch used to determine depth')
    parser.add_argument('--op-ntu-format',
                        type=str2bool,
                        default=False,
                        help='whether to use coordinate system of NTU')
    parser.add_argument('--op-save-skel',
                        type=str2bool,
                        default=True,
                        help='if true, save 3d skeletons.')
    parser.add_argument('--op-display',
                        type=int,
                        default=0,
                        help='scale for displaying skel images.')
    parser.add_argument('--op-display-depth',
                        type=int,
                        default=0,
                        help='scale for displaying skel images with depth.')
    # RUN OPTIONS
    parser.add_argument('--op-test-runtime',
                        type=str2bool,
                        default=False,
                        help='if true, test runtime of openpose.')
    parser.add_argument('--op-rs-offline-inference',
                        type=str2bool,
                        default=False,
                        help='if true, run openpose on saved images from rs.')
    parser.add_argument('--op-rs-delete-image',
                        type=str2bool,
                        default=False,
                        help='if true, deletes the rs image used in inference.')
    parser.add_argument('--op-rs-dir',
                        type=str,
                        default='-1',
                        help='path to folder with saved rs data.')
    parser.add_argument('--op-rs-image-width',
                        type=int,
                        default=848,
                        help='image width in px')
    parser.add_argument('--op-rs-image-height',
                        type=int,
                        default=480,
                        help='image height in px')
    parser.add_argument('--op-rs-3d-skel',
                        type=str2bool,
                        default=False,
                        help='if true, tries to extract 3d skeleton.')
    parser.add_argument('--op-rs-save-skel-image',
                        type=str2bool,
                        # default=False,
                        default=True,
                        help='if true, saves the 2d skeleton image.')
    return parser


def test_op_runtime(args: argparse.Namespace):
    image_path = "openpose/pexels-photo-4384679.jpeg"
    target_path = "openpose/output/inference_native"
    os.makedirs(target_path, exist_ok=True)
    params = dict(
        model_folder=args.op_model_folder,
        model_pose=args.op_model_pose,
        net_resolution=args.op_net_resolution,
    )
    pyop = PyOpenPoseNative(params,
                            args.op_skel_thres,
                            args.op_max_true_body,
                            args.op_patch_offset,
                            args.op_ntu_format)
    pyop.initialize()
    t_total = 0
    N = 1000
    image = cv2.imread(image_path)
    image = cv2.resize(image, (384, 384))
    for _ in trange(N):
        t_start = time.time()
        pyop.predict(image)
        pyop.filter_prediction()
        # pyop.display(1, 'dummy')
        pyop.save_pose_keypoints(f'{target_path}/predictions.txt')
        t_total += time.time() - t_start
    print(f"Average inference time over {N} trials : {t_total/N}s")


def rs_offline_inference(args: argparse.Namespace):
    """Runs openpose offline by looking at images found in the image_path arg.

    Args:
        args (argparse.Namespace): CLI arguments
    """

    assert args.op_rs_offline_inference, f'op_rs_offline_inference is False...'
    assert os.path.isdir(args.op_rs_dir), f'{args.op_rs_dir} does not exist...'

    params = dict(
        model_folder=args.op_model_folder,
        model_pose=args.op_model_pose,
        net_resolution=args.op_net_resolution,
        # heatmaps_add_parts=True,
        # heatmaps_add_bkg=True,
        # heatmaps_add_PAFs=True,
        # heatmaps_scale=1,
    )
    pyop = PyOpenPoseNative(params,
                            args.op_skel_thres,
                            args.op_max_true_body,
                            args.op_patch_offset,
                            args.op_ntu_format)
    pyop.initialize()

    base_path = args.op_rs_dir
    dev_trial_color_dir = get_rs_sensor_dir(base_path, 'color')
    dev_list = list(dev_trial_color_dir.keys())

    error_counter = 0
    error_state = False
    empty_counter = 0
    empty_state = False

    # 1. If no error
    while not error_state and not empty_state:

        # 2. loop through devices
        for dev, trial_color_dir in dev_trial_color_dir.items():

            # 3. loop through trials
            for trial, color_dir in trial_color_dir.items():

                color_files = sorted(os.listdir(color_dir))

                if len(color_files) == 0:
                    print(f"[INFO] : {color_dir} is empty...")
                    continue

                # 4. get the file that has not been inferred on.
                for i, color_file in enumerate(color_files):
                    color_filepath = os.path.join(color_dir, color_file)
                    skel_file = color_file.replace(color_file.split('.')[-1], 'csv')  # noqa
                    skel_dir = color_dir.replace('color', 'skeleton')
                    skel_filepath = os.path.join(skel_dir, skel_file)
                    if not os.path.exists(skel_filepath):
                        i = i - 1
                        break

                if i + 1 == len(color_files):
                    print(f"[INFO] : {color_dir} is fully evaluated...")
                    empty_counter += 1
                    if empty_counter > 300:
                        print("[INFO] Retried 300 times and no new files...")
                        empty_state = True
                    continue

                print(f"[INFO] : {len(color_files)-  max(i, 0)} files left...")

                # 5. get the color image
                try:
                    image = read_color_file(color_filepath)

                except Exception as e:
                    print(e)
                    print("[WARN] : Error in loading data, will retry...")
                    error_counter += 1
                    if error_counter > 300:
                        print("[ERRO] Retried 300 times and failed...")
                        error_state = True
                    continue

                # 5b. get the depth image
                depth = None
                if args.op_rs_3d_skel:

                    try:
                        depth = read_depth_file(color_filepath.replace('color', 'depth'))  # noqa

                    except Exception as e:
                        print(e)
                        print("[WARN] : Error in loading data, will retry...")
                        error_counter += 1
                        if error_counter > 300:
                            print("[ERRO] Retried 300 times and failed...")
                            error_state = True
                        continue

                # 6. reshape images
                try:
                    image = image.reshape(args.op_rs_image_height,
                                          args.op_rs_image_width, 3)
                    data_tuples = [(image, skel_filepath)]

                except Exception as e:
                    print(e)
                    print("Stacked data detected")
                    print(f"Current image shape : {image.shape}")

                    try:
                        image = image.reshape(args.op_rs_image_height,
                                              args.op_rs_image_width*3, 3)
                    except Exception as e:
                        print(e)
                        continue

                    data_tuples = []
                    for i in range(3):
                        _dir = skel_dir.replace(dev_list[0], dev_list[i])
                        _path = skel_file.split('.')[0]
                        _path = _path.split('_')[i]
                        _path = os.path.join(_dir, _path + '.csv')
                        j = args.op_rs_image_width * i
                        k = args.op_rs_image_width * (i+1)
                        data_tuples.append((image[:, j:k, :], _path))

                # 7. infer images
                try:
                    for image, save_path in data_tuples:
                        pyop.predict(image)
                        pyop.filter_prediction()
                        pyop.save_pose_keypoints(save_path)
                        if args.op_rs_save_skel_image:
                            pyop.save_skeleton_image(save_path)
                        print(f"[INFO] : OP output saved in {save_path}")
                        if depth is not None:
                            main_dir = os.path.dirname(os.path.dirname(save_path))  # noqa
                            intr_mat = read_calib_file(main_dir + "/calib/calib.csv")  # noqa
                            joints = pyop.pose_keypoints.shape[1]
                            empty_skeleton_3d = np.zeros((joints, 3))
                            pyop.convert_to_3d(
                                intr_mat=intr_mat,
                                depth_image=depth,
                                empty_pose_keypoints_3d=empty_skeleton_3d,
                                save_path=save_path.replace('skeleton', 'skeleton3d')  # noqa
                            )

                except Exception as e:
                    print(e)
                    continue

                if args.op_rs_delete_image:
                    os.remove(color_filepath)


if __name__ == "__main__":

    [arg_op, _] = get_parser().parse_known_args()
    if arg_op.op_test_runtime:
        test_op_runtime(arg_op)
    elif arg_op.op_rs_offline_inference:
        rs_offline_inference(arg_op)

    print(f"[INFO] : FINISHED")
