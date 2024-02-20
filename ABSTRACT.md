The **POG: People On Grass Dataset** is a real-world dataset. It shows people on mostly grassy areas from various angles and altitudes between 4 and 103 m. It contains 13,713 objects in 2900 images. The images are taken with a resolution of 3840 × 2150 px and also come with meta data like GPS location, altitude and attitude. The pictures were taken with a UAV by the University of Tübingen as part of the Avalon project.

## Motivation

Detection of objects from Unmanned Aerial Vehicles (UAVs) has emerged as a significant area of research due to its wide-ranging applications, including traffic surveillance, smart city management, and search and rescue operations. Despite notable advancements in generic object detection, the task remains highly challenging when applied to images captured by UAVs, primarily due to the diverse conditions encountered across domains.

One of the foremost challenges lies in the variability of images captured from different altitudes. Objects appear in vastly different scales, ranging from as small as 10 pixels to over 300 pixels, depending on the altitude. Lower altitudes yield detailed images, whereas higher altitudes result in blurrier images with more objects captured. Moreover, UAVs often utilize gimbal cameras, allowing for capturing objects from various viewing angles (pitch axis), further adding to the complexity. The roll axis of a UAV introduces additional variation, leading to objects being captured with diverse aspect ratios and orientations. This variability is particularly pronounced in top-down views, making it challenging to distinguish between similar objects such as cars and vans.

Numerous factors contribute to the appearance of objects, including variations in weather conditions, time of day, GPS location, and camera sensor characteristics. For instance, weather conditions like rain or sunshine affect object illumination, while different times of day can alter visibility. Backgrounds also vary significantly between urban and rural areas, further complicating object detection. Additionally, differences in camera lenses introduce distortions that impact image quality. These variations become even more critical when considering the interaction between different domains, highlighting the complexity of object detection from UAV-captured images.

## Dataset description

The authors have compiled the experimental dataset PeopleOnGrass (POG), which comprises 2,900 images with a resolution of 3840x2160 pixels. These images depict individuals captured from various perspectives and altitudes, ranging from 0° (horizontal) to 90° (top-down), and heights spanning from 4 meters to 103 meters. Each image is meticulously labeled with its precise altitude and angle of capture. Additionally, the dataset includes supplementary metadata such as GPS coordinates, UAV velocity and rotation information, timestamps, and other relevant details.

<img src="https://github.com/dataset-ninja/pog/assets/120389559/931db89b-68fe-4e47-8151-8b75dcc730e7" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Example images of the dataset POG, showing the same scenery taken from different perspectives (top: 10m, 10◦, bottom: 100m, 90◦).</span>

The data collection was conducted using a DJI Matrice 210 drone equipped with a Zenmuse XT2 camera. Metadata was extracted using [DJI's](https://developer.dji.com/onboard-sdk/) onboard software development kit. A metadata stamp is generated for each frame at a rate of 10 hertz to synchronize with the video data captured at 30 frames per second. To ensure temporal alignment between the videos data and timestamps, a nearest neighbor method was applied. For each image/frame, the dataset provides logged data from onboard sensors including the clock, barometer, Inertial Measurement Unit (IMU), and Global Positioning System (GPS) respectively:

* current ***datetime*** of capture,
* ***latitude***, ***longitude*** and altitude of the UAV,
* camera pitch, roll and yaw angle (viewing angle),
* speed along the x-, y and z-axes.

The meta values lie within the error thresholds introduced by the different sensors.

<img src="https://github.com/dataset-ninja/pog/assets/120389559/b7726ff0-eb4a-4e8f-9bef-39d6f7fedd49" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Distribution of objects in PeopleOnGrass (POG) across different levels of altitude and camera pitch angles. For visualization purposes only a 4x10 grid is shown.</span>

The authors manually and carefully annotate 13,713 people. They note that this is a simple real-world data set, suffering from fewer confounders than large data sets which is ideal for testing out the efficacy of multi-modal methods.

