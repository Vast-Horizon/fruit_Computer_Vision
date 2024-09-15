# fruit_Computer_Vision
This project trains and uses a machine learning model based on tensorflow.keras to recognize fruits. 

I also implemented a weight sensor system using HX711 to measure the weight of fruits.

If you want to try out the model(either by images or real-time):
For Windows users, run predict.py or realtime-test.py
For Raspberry Pi users, run predict_tf-runtime.py or realtime_pi-cam.py

For those want to learn how to use HX711 with Raspberry Pi, check out pi_weight_sensor/

Pretrained model: MobileNetV2. 

Dataset is based on Kaggle "Fruits and Vegetables Image - MobileNetV2" by Nima Pourmoradi. 
Adjustment of the dataset was done to improve accuracy for the specific project need.
 
My is board is a Raspberry Pi 5 with 32bit OS. Other Pi might or might not work directly 