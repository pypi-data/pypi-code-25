from img_utils.images import images2video

if __name__ == '__main__':
    images_dir = "/tmp/hawkeye/images/dsp_students_0.01667/face_detection"
    images2video(images_dir, 1, "dsp_students_face.mp4")
