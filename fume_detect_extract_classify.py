import cv2
import numpy as np
import argparse


def rescale_frame(frame, percent=75):
    """Rescale the Frame to required percentage

    Args:
        frame (numpy.ndarray): frame to be resized
        percent (int, optional): Resizing percentage in terms of original frame. Defaults to 75.

    Returns:
        resized_frame (numpy.ndarray): Resized frames as per needed
    """
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def bg_sub(input_video, debug=False):
    """Background Subtraction from a video. Removes frame by ignoring non moving objects.

    Args:
        input_video (video_file[any]): Input Video from which background needs to be removed
        debug (bool, Optional): If enabled it displays each frames while processing video

    Returns:
        op_video_name: Path of output video
    """
    cap = cv2.VideoCapture(input_video)

    _, first_frame = cap.read()
    r_frame = rescale_frame(first_frame, percent=100)
    first_gray = cv2.cvtColor(r_frame, cv2.COLOR_BGR2GRAY)
    first_gray = cv2.GaussianBlur(first_gray, (5, 5), 0)

    # We need to set resolutions for writing a video
    # so, convert them from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)

    # VideoWriter object for writing video
    op_video_name = 'output/masked_video.avi'
    save = cv2.VideoWriter(op_video_name, cv2.VideoWriter_fourcc(*'MJPG'), 30, size)

    while(cap.isOpened()):
        try:
            ret, frame = cap.read()
            if not ret:
                pass
            resize_frame = rescale_frame(frame, percent=100)
            gray_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (5,  5), 0)

            diff = cv2.absdiff(first_gray, gray_frame)
            _, diff = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

            # Using bitwise_and operator to apply the output difference mask on the original video to get coloured mask.
            mask = cv2.bitwise_and(resize_frame, resize_frame, mask=diff)
            if ret == True:

                # saving the video using 'save' object.
                save.write(mask)

                # for debugging and viewing the frames
                if debug:
                    cv2.imshow('Frame', resize_frame)
                    cv2.imshow('diff', diff)
                    cv2.imshow('mask', mask)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else:
                break
        except Exception as e:
            print(e)
            break

    cap.release()

    return op_video_name


def color_sub(masked_video, debug=False):
    """Color Subtraction module. Removes the colors bucketed the colors of harmful/toxic fumes 
    and extracts those fumes from the background subtracted video to avoid background noise.

    Args:
        masked_video (video_file[any]): Background subtracted/masked video of blast
        debug (bool, Optional): If enabled it displays each frames while processing video

    Returns:
        toxicity_percentage: The toxicity percentage of the blast in the video
    """
    # lower mask (0-10)
    lower_red = np.array([0,50,50])
    upper_red = np.array([60,255,255])

    # upper mask (170-180)
    lower_red1 = np.array([160,50,50])
    upper_red1 = np.array([200,255,255])

    cap = cv2.VideoCapture(masked_video)

    # We need to set resolutions for writing a video
    # so, convert them from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)

    # VideoWriter object for writing video
    op_video_name = 'output/output_vid.avi'
    save = cv2.VideoWriter(op_video_name, cv2.VideoWriter_fourcc(*'MJPG'), 30, size)

    toxicity_percentage = 0
    no_of_frames = 1

    while(cap.isOpened()):
        try:
            ret, frame = cap.read()
            if not ret:
                pass
            resize_frame = rescale_frame(frame, percent=100)
            mask0 = cv2.inRange(frame, lower_red, upper_red)
            mask1 = cv2.inRange(frame, lower_red1, upper_red1)
            # join my masks
            mask = mask0+mask1
            # mask = mask2

            # set my output img to zero everywhere except my mask
            output_img = frame.copy()
            output_img[np.where(mask==0)] = 0

            # print(len(np.where(mask==0)[0]), len(np.where(mask==0)[1]), len(np.where(mask!=0)[0]), len(np.where(mask!=0)[1]))
            non_zero_pixels = len(np.where(mask!=0)[0]) + len(np.where(mask!=0)[1])
            # tot_pixels = len(np.where(mask==0)[0]) + len(np.where(mask==0)[1]) + len(np.where(mask!=0)[0]) + len(np.where(mask!=0)[1])
            tot_pixels = len(np.where(frame!=0)[0]) + len(np.where(frame!=0)[1])
            try:
                toxicity_percentage += non_zero_pixels / tot_pixels
            except ZeroDivisionError:
                pass
            no_of_frames += 1

            save.write(output_img)

            if debug:
                # for debugging if required uncomment below lines
                cv2.imshow("img", output_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(e)
            break
    
    print(f"Toxicity Percentage is: {toxicity_percentage/no_of_frames * 100}")
    cap.release()

    return toxicity_percentage/no_of_frames * 100

def analyze_fumes(input_video, debug):
    """Main Function that removes background first and then runs color subtraction to find toxicity percentage

    Args:
        input_video (video_file[any]): Input Video from which background needs to be removed

    Returns:
        toxicity_percentage(float): The toxicity percentage (total pixels of toxic fumes/total fumes)
    """
    path_to_bg_sub_vid = bg_sub(input_video, debug)
    toxicity_percentage = color_sub(path_to_bg_sub_vid, debug)
    return toxicity_percentage


if __name__ == "__main__":
    
    # Create the parser
    parser = argparse.ArgumentParser()
    
    # Add an argument
    parser.add_argument('--vid', type=str, required=True, help="Path of the video file")
    parser.add_argument('--debug', type=bool, default=False, help="To visualize the processing")
    
    # Parse the argument
    args = parser.parse_args()
    
    # Running main function
    analyze_fumes(args.vid, args.debug)