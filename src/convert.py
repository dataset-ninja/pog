import csv
import os
import shutil
from collections import defaultdict
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import get_file_name, get_file_name_with_ext
from supervisely.io.json import load_json_file
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    dataset_path = "/home/alex/DATASETS/TODO/POG/PeopleOnGrass/images"
    batch_size = 10

    train_anns = "/home/alex/DATASETS/TODO/POG/PeopleOnGrass/instances_train.json"
    val_anns = "/home/alex/DATASETS/TODO/POG/PeopleOnGrass/instances_val.json"
    meta_path = "/home/alex/DATASETS/TODO/POG/PeopleOnGrass/meta.csv"

    ds_name_to_anns = {"train": train_anns, "val": val_anns}

    def create_ann(image_path):
        labels = []
        tags = []

        image_name = get_file_name_with_ext(image_path)
        img_height = image_name_to_shape[image_name][0]
        img_wight = image_name_to_shape[image_name][1]

        tags_vals = name_to_meta.get(get_file_name_with_ext(image_path))
        if tags_vals is not None:
            time = sly.Tag(time_meta, value=int(tags_vals[0]))
            datetime = sly.Tag(datetime_meta, value=tags_vals[1])
            latitude = sly.Tag(latitude_meta, value=float(tags_vals[2]))
            longitude = sly.Tag(longitude_meta, value=float(tags_vals[3]))
            speed = sly.Tag(speed_meta, value=float(tags_vals[4]))
            distance = sly.Tag(distance_meta, value=float(tags_vals[5]))

            tags.extend([time, datetime, latitude, longitude, speed, distance])

        # image_np = sly.imaging.image.read(image_path)[:, :, 0]
        # img_height = image_np.shape[0]
        # img_wight = image_np.shape[1]

        ann_data = image_id_to_ann_data[get_file_name_with_ext(image_path)]
        for bbox_coord in ann_data:
            rectangle = sly.Rectangle(
                top=int(bbox_coord[1]),
                left=int(bbox_coord[0]),
                bottom=int(bbox_coord[1] + bbox_coord[3]),
                right=int(bbox_coord[0] + bbox_coord[2]),
            )
            label_rectangle = sly.Label(rectangle, obj_class)
            labels.append(label_rectangle)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    obj_class = sly.ObjClass("pedestrain", sly.Rectangle)

    time_meta = sly.TagMeta("time", sly.TagValueType.ANY_NUMBER)
    datetime_meta = sly.TagMeta("datetime", sly.TagValueType.ANY_STRING)
    latitude_meta = sly.TagMeta("latitude", sly.TagValueType.ANY_NUMBER)
    longitude_meta = sly.TagMeta("longitude", sly.TagValueType.ANY_NUMBER)
    speed_meta = sly.TagMeta("speed", sly.TagValueType.ANY_NUMBER)
    distance_meta = sly.TagMeta("distance", sly.TagValueType.ANY_NUMBER)

    meta = sly.ProjectMeta(
        obj_classes=[obj_class],
        tag_metas=[
            time_meta,
            datetime_meta,
            latitude_meta,
            longitude_meta,
            speed_meta,
            distance_meta,
        ],
    )
    api.project.update_meta(project.id, meta.to_json())

    name_to_meta = {}

    with open(meta_path, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            name_to_meta[row[0]] = [row[1], row[2], row[3], row[4], row[9], row[10]]

    for ds_name, ann_path in ds_name_to_anns.items():

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        curr_images_path = os.path.join(dataset_path, ds_name)

        json_ann = load_json_file(ann_path)
        image_id_to_name = {}
        image_name_to_shape = {}
        image_id_to_ann_data = defaultdict(list)

        images_data = json_ann["images"]
        for image_data in images_data:
            image_id_to_name[image_data["id"]] = image_data["file_name"]
            image_name_to_shape[image_data["file_name"]] = (
                image_data["height"],
                image_data["width"],
            )

        annotations = json_ann["annotations"]
        for ann in annotations:
            image_id_to_ann_data[image_id_to_name[ann["image_id"]]].append(ann["bbox"])

        progress = sly.Progress("Create dataset {}".format(ds_name), len(image_id_to_ann_data))

        images_names = os.listdir(curr_images_path)

        for images_names_batch in sly.batched(images_names, batch_size=batch_size):
            img_pathes_batch = [
                os.path.join(curr_images_path, im_name) for im_name in images_names_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))

    return project
