arduino-cli upload \
  -p /dev/ttyUSB0 \
  --fqbn esp32:esp32:nodemcu-32s \
  --board-options UploadSpeed=115200 \
  controller.ino
