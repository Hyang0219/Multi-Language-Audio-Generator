import srt
from datetime import timedelta
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk
from langdetect import detect
import os
import json
from collections import Counter
import time
import io

# Load voice configuration from JSON file
with open('voice_config.json', 'r') as f:
    voice_config = json.load(f)

# Step 1: Parse SRT
def parse_srt(srt_file):
    with open(srt_file, 'r', encoding='utf-8') as file:
        subtitles = srt.parse(file.read())
        segments = [(sub.start, sub.end, sub.content) for sub in subtitles]
    return segments

# Detect majority language in SRT segments
def detect_majority_language(segments):
    languages = []
    for _, _, content in segments:
        try:
            detected_lang = detect(content)
            languages.append(detected_lang)
        except Exception as e:
            print(f"Error detecting language for content: {content}. Error: {e}")
    if languages:
        most_common_language = Counter(languages).most_common(1)[0][0]
        return most_common_language
    return 'unknown'

# Step 2: Convert Text to Speech using Azure TTS with prosody rate adjustment
def text_to_speech_azure(text, speech_key, service_region, prosody_rate, voice_name):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Setting the voice name from the config
    speech_config.speech_synthesis_voice_name = voice_name
    
    # Adjust prosody rate
    ssml_string = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{voice_name.split('-')[0]}'>
        <voice name='{speech_config.speech_synthesis_voice_name}'>
            <prosody rate='{prosody_rate}'>
                {text}
            </prosody>
        </voice>
    </speak>
    """
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_ssml_async(ssml_string).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
        audio_data = result.audio_data
        return audio_data
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
                print("Did you set the speech resource key and region values?")
        return None

# Measure the duration of the audio data
def get_audio_duration(audio_data):
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
    return len(audio) / 1000.0  # return duration in seconds

# Step 3: Combine Audio Segments
def combine_audio_segments(segments, speech_key, service_region, voice_name):
    combined = AudioSegment.silent(duration=0)
    for i, (start, end, content) in enumerate(segments):
        target_duration = (end - start).total_seconds()

        # Generate audio with default prosody rate to measure duration
        audio_data = text_to_speech_azure(content, speech_key, service_region, "1.0", voice_name)
        
        # If TTS failed, retry with a delay
        retries = 3
        while audio_data is None and retries > 0:
            print(f"Retrying for segment {i}...")
            time.sleep(5)  # Delay before retrying
            audio_data = text_to_speech_azure(content, speech_key, service_region, "1.0", voice_name)
            retries -= 1
        
        if audio_data is None:
            # If all retries fail, use a silent segment with the target duration
            audio_segment = AudioSegment.silent(duration=target_duration * 1000)
        else:
            default_duration = get_audio_duration(audio_data)
            speed_factor = default_duration / target_duration
            prosody_rate = f"{speed_factor:.2f}"

            # Generate final audio with adjusted prosody rate
            audio_data = text_to_speech_azure(content, speech_key, service_region, prosody_rate, voice_name)
            
            # Retry if needed
            retries = 3
            while audio_data is None and retries > 0:
                print(f"Retrying for segment {i} with prosody rate {prosody_rate}...")
                time.sleep(5)  # Delay before retrying
                audio_data = text_to_speech_azure(content, speech_key, service_region, prosody_rate, voice_name)
                retries -= 1
            
            if audio_data is None:
                # If all retries fail, use a silent segment with the target duration
                audio_segment = AudioSegment.silent(duration=target_duration * 1000)
            else:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")

        silence = AudioSegment.silent(duration=start.total_seconds() * 1000 - len(combined))
        combined += silence + audio_segment
    return combined

# Main process
srt_file = 'Paste SRT File Path Here'
segments = parse_srt(srt_file)

# Detect the majority language in the SRT file
majority_language = detect_majority_language(segments)
voice_name = voice_config["default_voice"].get(majority_language, "en-US-AriaNeural")  # Default to English if language is not recognized

# Your Azure Speech API key and region
speech_key = "Paste Your Azure Speech Key Here"
service_region = "Paste Your Azure Service Region Here"

# Combine audio segments into one file
combined_audio = combine_audio_segments(segments, speech_key, service_region, voice_name)
combined_audio.export("/content/text_to_speech_audio.wav", format="wav")
