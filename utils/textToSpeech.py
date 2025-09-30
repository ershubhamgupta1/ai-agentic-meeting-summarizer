import os
from gtts import gTTS

# 1. Create the folder if it doesn't exist
output_dir = "sample-meetings"
os.makedirs(output_dir, exist_ok=True)

# 2. Your sample meeting script
meeting_script = """
John: Alright team, let’s do a quick sync-up. Sarah, how’s the progress on the onboarding flow?
Sarah: I finished the UI components yesterday. I’m integrating them with the backend today, and testing should be done by tomorrow.
John: Great. Raj, any updates on the analytics dashboard?
Raj: I’m still working on the chart rendering. I ran into a couple of bugs with dynamic filtering, but I should have them fixed by this afternoon.
John: Sounds good. Once you’re done, please pass it to QA. Lisa, how’s customer feedback processing going?
Lisa: We’ve categorized about 300 responses so far. I’ll prepare a summary report by end of day.
John: Awesome. Thanks, everyone. Let’s aim to wrap all this up before Friday.
"""

# 3. Generate MP3 with gTTS
tts = gTTS(text=meeting_script, lang='en')

# 4. Define path and save
output_path = os.path.join(output_dir, "meeting.mp3")
tts.save(output_path)

print(f"✅ MP3 file saved at: {output_path}")
