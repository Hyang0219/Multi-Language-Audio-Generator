import srt
from datetime import timedelta
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk
import matplotlib.pyplot as plt
from langdetect import detect
import os
import json
from collections import Counter
import time

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
def text_to_speech_azure(text, filename, speech_key, service_region, prosody_rate, voice_name):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
    
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
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_ssml_async(ssml_string).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
        return True
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
                print("Did you set the speech resource key and region values?")
        return False

# Measure the duration of the audio file
def get_audio_duration(filename):
    try:
        audio = AudioSegment.from_file(filename)
        return len(audio) / 1000.0  # return duration in seconds
    except Exception as e:
        print(f"Could not decode audio file {filename}: {e}")
        return 0

# Step 3: Combine Audio Segments
def combine_audio_segments(segments):
    combined = AudioSegment.silent(duration=0)
    for i, (start, end, content) in enumerate(segments):
        audio = AudioSegment.from_file(f"segment_{i}.wav")
        silence = AudioSegment.silent(duration=start.total_seconds() * 1000 - len(combined))
        combined += silence + audio
    return combined

# Step 4: Plot Speed Factors with Durations
def plot_speed_factors_with_durations(speed_factors, default_durations, target_durations, min_speed_factor):
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.set_xlabel('Segment Index')
    ax1.set_ylabel('Speed Factor', color='tab:blue')
    ax1.bar(range(len(speed_factors)), speed_factors, color='blue', alpha=0.6, label='Speed Factor')
    ax1.axhline(y=min_speed_factor, color='red', linestyle='--', label='Minimum Speed Factor')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Duration (s)', color='tab:green')
    ax2.plot(range(len(default_durations)), default_durations, color='green', marker='o', linestyle='-', label='Default Duration')
    ax2.plot(range(len(target_durations)), target_durations, color='orange', marker='o', linestyle='-', label='Target Duration')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    fig.tight_layout()
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    plt.title('Speed Factors and Durations of Each Segment')
    plt.show()

# Main process
srt_file = 'Input SRT file path here'
segments = parse_srt(srt_file)

# Detect the majority language in the SRT file
majority_language = detect_majority_language(segments)
voice_name = voice_config["default_voice"].get(majority_language, "en-US-AriaNeural")  # Default to English if language is not recognized

# Your Azure Speech API key and region
speech_key = "Input Your Azure Speech Key Here"
service_region = "Input Your Azure Service Region Here"
min_speed_factor = 1  # Define minimum speed factor

# Lists to store speed factors and durations for each segment
speed_factors = []
default_durations = []
target_durations = []

# Generate audio files for each segment with adjusted prosody rate
for i, (start, end, content) in enumerate(segments):
    target_duration = (end - start).total_seconds()
    target_durations.append(target_duration)

    # Generate audio with default prosody rate to measure duration
    temp_filename = f"temp_segment_{i}.wav"
    success = text_to_speech_azure(content, temp_filename, speech_key, service_region, "1.0", voice_name)
    
    # If TTS failed, retry with a delay
    retries = 3
    while not success and retries > 0:
        print(f"Retrying for segment {i}...")
        time.sleep(5)  # Delay before retrying
        success = text_to_speech_azure(content, temp_filename, speech_key, service_region, "1.0", voice_name)
        retries -= 1
    
    if not success:
        # If all retries fail, use a silent segment with the target duration
        silent_audio = AudioSegment.silent(duration=target_duration * 1000)
        silent_audio.export(temp_filename, format="wav")
    
    default_duration = get_audio_duration(temp_filename)
    default_durations.append(default_duration)

    speed_factor = default_duration / target_duration

    # Ensure speed factor is not below minimum
    if speed_factor < min_speed_factor:
        speed_factor = min_speed_factor

    prosody_rate = f"{speed_factor:.2f}"
    speed_factors.append(speed_factor)

    # Generate final audio with adjusted prosody rate
    final_filename = f"segment_{i}.wav"
    success = text_to_speech_azure(content, final_filename, speech_key, service_region, prosody_rate, voice_name)
    
    # Retry if needed
    retries = 3
    while not success and retries > 0:
        print(f"Retrying for segment {i} with prosody rate {prosody_rate}...")
        time.sleep(5)  # Delay before retrying
        success = text_to_speech_azure(content, final_filename, speech_key, service_region, prosody_rate, voice_name)
        retries -= 1
    
    if not success:
        # If all retries fail, use a silent segment with the target duration
        silent_audio = AudioSegment.silent(duration=target_duration * 1000)
        silent_audio.export(final_filename, format="wav")

    # Clean up temporary file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

# Combine audio segments into one file
combined_audio = combine_audio_segments(segments)
combined_audio.export("/content/text_to_speech_audio.wav", format="wav")

# Plot speed factors and durations
plot_speed_factors_with_durations(speed_factors, default_durations, target_durations, min_speed_factor)
