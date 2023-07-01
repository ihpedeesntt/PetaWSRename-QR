import cv2
import pyzbar.pyzbar as pyzbar

def detect_qr_code(image_path):
  """Detects QR codes from an image.

  Args:
    image_path: The path to the image.

  Returns:
    A list of the detected QR codes.
  """

  image = cv2.imread(image_path)

  qr_codes = pyzbar.decode(image)

  return qr_codes

if __name__ == "__main__":
  from glob import glob
  import os

  types = ('*.jpg', '*.JPEG', '*.jpeg', '*.JPG')
  list_images = []
  for files in types:
    list_images.extend(glob( "folder-input" + os.path.sep + files))

  print(list_images)

  for i in sorted(list_images):
    qr_codes = detect_qr_code(i)
    print(i,qr_codes)
    for qr_code in qr_codes:
      print(i,qr_code.data)