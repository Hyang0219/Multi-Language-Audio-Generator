# Multi-Language-Audio-Generator
A simple application to create synchronised audio of multi-languages from a subtitle file. It uses Microsoft Azure Speech service to dub the video with AI voices.

## How It Works
You will need a pre-prepared subtitle SRT file of the chosen language
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
1. Install all the requirements by running below codes in Google Colab, one by one
    1. pip install gtts pydub srt
    2. pip install azure-cognitiveservices-speech
    3. pip install langdetect
    4. pip install matplotlib
