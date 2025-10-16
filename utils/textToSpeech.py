import os
from gtts import gTTS

# 1. Create the folder if it doesn't exist
output_dir = "sample-meetings"
os.makedirs(output_dir, exist_ok=True)

# 2. Your sample meeting script``
meeting_script_1 = """
John: Alright team, let’s do a quick sync-up. Sarah, how’s the progress on the onboarding flow?
Sarah: I finished the UI components yesterday. I’m integrating them with the backend today, and testing should be done by tomorrow.
John: Great. Raj, any updates on the analytics dashboard?
Raj: I’m still working on the chart rendering. I ran into a couple of bugs with dynamic filtering, but I should have them fixed by this afternoon.
John: Sounds good. Once you’re done, please pass it to QA. Lisa, how’s customer feedback processing going?
Lisa: We’ve categorized about 300 responses so far. I’ll prepare a summary report by end of day.
John: Awesome. Thanks, everyone. Let’s aim to wrap all this up before Friday.
"""

meeting_script_2 = """
Alice: Alright everyone, let's kick off the sprint retro. I know we’ve had a few hiccups this week. Bob, can you start with blockers?

Bob: Sure, the payment API integration caused some headaches. The dev docs weren’t complete, and I ran into 500 errors when simulating concurrent requests. It delayed the testing handoff by about two days.

Carol: Yeah, that hit QA pretty hard. We had to manually verify some critical flows because automation couldn’t run without the backend being stable. And even after we started, some intermittent failures kept popping up.

David: Speaking of which, the dashboard UI also has inconsistencies. Some of the new alert components don’t match the design system — spacing, color contrast, alignment — it’s all over the place.

Eve: And those changes affected the front-end build pipeline too. I had to roll back some components to get a stable dev branch, which slowed down my feature work.

Alice: Okay… so we’ve got backend delays, QA bottlenecks, and front-end inconsistencies. Bob, is the API issue resolved now, or is it still flaky?

Bob: Mostly resolved, but under high load, the cache layer sometimes returns stale data. I’ve added logging, but it may need backend tweaks next sprint. Also, the concurrency issue with transactions isn’t fully mitigated.

Carol: That explains why some regression tests failed randomly. I thought it was flaky network issues, but this makes sense now. We’ll need to rerun the full suite once Bob stabilizes the API.

David: And we should talk about design drift. Not just alerts — dropdowns, card layouts, and the notification panel all need a quick review. Otherwise, the release will feel inconsistent.

Eve: Yeah, plus the new component library update broke some mobile layouts. The scrolling behavior on notifications is laggy on iOS 14–15. It’s subtle but noticeable.

Alice: Good catch. Bob, do you think caching or backend tweaks will affect that?

Bob: Probably not. That’s mostly front-end. But if we’re throttling requests for performance, some of Eve’s data-bound components may load slower. Not a huge deal, but noticeable.

Carol: I’d suggest we prioritize what’s high-impact for end-users. Regression failures that affect transactions are critical, UI layout inconsistencies medium, performance tweaks low priority — otherwise, we’ll burn the team out.

David: Agreed. Also, some of the users reported that the hover states in the desktop dashboard are inconsistent across browsers — Safari vs Chrome mainly. It’s minor but will be noticeable in the demo.

Eve: And I noticed a regression from last sprint: the new search filter occasionally resets selections after refresh. Could confuse users.

Alice: Should we adjust the load testing for the caching layer now or next sprint?

Carol: Probably next sprint, since we need stable regression first. Otherwise we’ll have moving targets.

David: Also, minor note — the prototype for the new card component might need UX tweaks. Should we include it in this sprint retro discussion or table it?

Alice: Let’s table it for now. Focus on the blockers and current regressions. Document any feedback for the next sprint. 

Eve: Sounds good. I’ll make sure the front-end backlog reflects the regressions and mobile issues.

Alice: Perfect. Alright, that wraps up today’s retro. Thanks everyone — let’s follow up once the initial fixes are done.
"""
# 3. Generate MP3 with gTTS
tts = gTTS(text=meeting_script_2, lang='en')

# 4. Define path and save
output_path = os.path.join(output_dir, "meeting_2.mp3")
tts.save(output_path)

print(f"✅ MP3 file saved at: {output_path}")
