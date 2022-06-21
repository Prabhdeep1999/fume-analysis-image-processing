from flask_restful import Resource
from flask import jsonify, request
from werkzeug.utils import secure_filename
import os

from .helper_utils import check_input, verify
from .fume_detect_extract_classify import analyze_fumes
from .postgres_connection import cursor

class Classify(Resource):
    """Performs the toxicity percentage calculation.

    Args:
        Resource (flask_restful.Resource): To perform POST API in a RESTful way
    """
    def post(self):
        default_ret = None

        # taking user credentials from user
        username = str(request.form.get('username', default_ret))
        password = str(request.form.get('password', default_ret))

        # check validity
        ret1 = check_input({"username": username, "password": password})

        # verify credentials
        ret2 = verify(cursor, username, password)
        if ret1["status"] != 200:
            return jsonify(ret1)
        else:
            if ret2["status"] != 200:
                return jsonify(ret2) 
        
        # taking video input from user
        vid = request.files["video"]
        vid.save(secure_filename("cached_vid.mp4"))

        print("[INFO] Video Received")
        # performing fume analysis
        toxicity_percentage = analyze_fumes("cached_vid.mp4")

        # uploading video to s3
        # upload_file_s3(vid.filename, "smartblast", "{}".format(str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")) + ".mp4"))

        # deleting file
        os.remove("cached_vid.mp4")
        os.remove('output_vid.avi')
        os.remove('masked_video.avi')
        print("[INFO] Temp Videos Removed")

        # preparing response
        retJson = {
            "status": 200,
            "msg": ["Toxicity", toxicity_percentage]
        }

        return jsonify(retJson)