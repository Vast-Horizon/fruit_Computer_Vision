# fruit_Computer_Vision
![image](https://github.com/user-attachments/assets/b5e71335-f486-4827-bbe5-a9e5349aa2b7)

This project shows how to train and use a machine learning model based on tensorflow.keras to recognize fruits. 

The model's accuracy is not very good yetand is more of an educational project. You can train it better.

I also implemented a simple weight sensor system using HX711 to measure the weight of fruits (or any other object).

If you just want to try out the model(either by images or real-time): \
For Windows users, run predict.py or realtime-test.py \
For Raspberry Pi users, run predict_tf-runtime.py or realtime_pi-cam.py

For those want to learn how to use HX711 with Raspberry Pi, check out pi_weight_sensor/

=============================== \
Pretrained model: MobileNetV2. 

Dataset is based on Kaggle "Fruits and Vegetables Image - MobileNetV2" by Nima Pourmoradi. 
Adjustment of the dataset was done to improve accuracy for the specific project need.
 
My is board is a Raspberry Pi 5 with 32bit OS. Other Pi might or might not work directly 
![accurcy1](https://github.com/user-attachments/assets/28254267-aceb-431a-bd4b-a8618ded52d7)
