# Multi-Language-Audio-Generator
A simple application to create synchronised audio of multi-languages from a subtitle file. It uses Microsoft Azure Speech service to dub the video with AI voices.
This programme is generated with the help of ChatGPT 4.0.

## How It Works
You will need a pre-prepared subtitle SRT file of the chosen language, you can 
  1. Automatically detects the languages within the SRT file
  2. Extract texts and timings from SRT file
  3. Uses Microsoft Azure API to generate individual audio clips (segment) based on the extracted texts and timings, through the Speech text-to-speech service
  4. Adjust the speed of the audio clips using the prosody parameter (speed factors) within SSML (Speech Synthesis Markup Language)
     * This is done by comparing the target duration (extracted timings) and default duration (time taken for AI voice to finish with its default speed). i.e speed_factor = default_duration / target_duration
     * Speed factor is capped at a minimum of 1 to avoid rare cases of extremely slow playback speed
  7. Build the entire track by combining all individual video clips based on the timing

## Key Features
  * Language auto-detection
  * AI voice customisation using Microsoft Azure Speech service
  * Fully synchronised audio track
  * Chart showing speed factors that provides capability of fine-tuning the srt file to move texts around (please do not change timings!) to reduce the speed factor under rare cases with super fast playback speed

## Instructions
1. Go to [Google Colab](https://colab.research.google.com/), sign in with your Google account and create a new notebook
2. Connect to the server and install the Python libraries by running the below codes in the notebook, one by one (you will get an error if you try to run them all in one go)
    1. `pip install gtts pydub srt`
    2. `pip install azure-cognitiveservices-speech`
    3. `pip install langdetect`
    4. `pip install matplotlib`
3. Copy the `main.py' file from the repo and paste it into your notebook  
4. Locate your Microsoft Azure service account information
    1. speech_key
    2. service_region  
![Screenshot 2024-06-23 172200](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/6ee89be0-9480-4bd3-88bc-bf9c0979c572)  
    and fill in the two fields in the notebook with your Azure service account information  
![Screenshot 2024-06-23 172456](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/25ad2e90-53ba-4a01-858f-5e52d97ac73f)  
5. Upload the SRT file to your notebook  
![Screenshot 2024-06-23 172200](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/36ac03a7-0c3f-4bb9-ae25-0d6bac6dc9bd)  
    and copy the file path  
    ![Screenshot 2024-06-23 172839](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/fcc188e1-eaf6-4f77-8a11-123adb8c531f)
6. Paste the path  
![Screenshot 2024-06-23 173232](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/5357641c-60ec-4352-9e72-0b304625dc40)
7. Download `voice_config.json` from the repo and upload it to your notebook following the same method as the SRT file.
8. Hit run and once it finishes, you will get a file `text_to_speech_audio.wav`. You can download it from the notebook and upload to either your editting software or Youtube Studio if you have the audio feather enabled in your account  
![Screenshot 2024-06-23 173841](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/6734eee2-ad74-4323-a396-51ec3686a50e)

## Additional Notes
1. You can browse on Microsoft Azure Speech service to choose the voice you want and copy the code and replace it with the default voice in the configuration file. Please do not add multiple voices for one language.  
![Screenshot 2024-06-23 220511](https://github.com/Hyang0219/Multi-Language-Audio-Generator/assets/54818876/f11ab891-0c57-4d9a-af41-1974e7265892)    
2. At the moment, I have only included a couple of languages in the configuration file `voice_config.json`, feel free to create your own configuration file and add your language so the programme can detect it.


