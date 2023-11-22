# from integrations.youtube_utils import youtube_download

from fastapi import FastAPI

# from gender_detection import voice_gender_detection

app = FastAPI()


# youtube_link = "https://youtu.be/WDv4AWk0J3U?si=wL3cKW1PCvinxBDy"
# video_path = 'test-video-1min.mp4'

# source_blob_name = 'XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4'

# useId, projectId,

# https://audioland.fly.dev/?original_file_location=XYClUMP7wEPl8ktysClADpuaPIq2/4kIRz5B1JY0GAO1uj0dE/test-video-1min.mp4


@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    print("main started")
