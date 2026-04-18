# title
Generate title slide JSON:
{"type":"title","unit":"...","lesson":"...","objective":"...","emoji":"🎯"}

# warm_up
Generate warm_up slide JSON:
{"type":"warm_up","title":"Warm Up","subtitle":"...","question":"...","starters":["...","..."]}

# useful_language_1
Generate useful_language_1 slide JSON. Words MUST exactly match the key_points list provided (one entry per word, no more, no fewer):
{"type":"useful_language_1","title":"Useful Language (Part 1)","teacher_instructions":["Read each word aloud and ask the student to repeat.","Read the definition and example sentence.","Ask the check question to confirm understanding.","Ask the student to make their own sentence with one word."],"words":[
  {"word":"<key_points[0]>","emoji":"...","definition":"...","example":"...","check":"..."},
  {"word":"<key_points[1]>","emoji":"...","definition":"...","example":"...","check":"..."}
]}
TITLE LOCK: The "title" field MUST be exactly "Useful Language (Part 1)" — do NOT rename it.
TEACHER INSTRUCTIONS LOCK: The "teacher_instructions" field MUST always be present and MUST be a JSON array of strings (NOT a single string). Use exactly 4 steps as shown above.
NOTE: If key_points has 3 words, add a 3rd entry. If it has 4, add 4 entries. Match EXACTLY.
CCQ RULE: Each "check" question MUST be an A/B choice question or an open-ended Wh- question. NEVER use bare Yes/No questions. For A1/A2 levels, ALWAYS use A/B choice (e.g. "Which is spicier: a green salad or a curry?", "Do you eat this with a fork or a spoon?"). For B1+, use Wh- questions that require a full sentence. Good examples: "Which of these is a better example: A or B?", "What would you do if...?", "How would you use this word in a sentence about your own life?".

# useful_language_2
Generate useful_language_2 slide JSON. Words MUST exactly match the key_points list provided (one entry per word, no more, no fewer):
{"type":"useful_language_2","title":"Useful Language (Part 2)","teacher_instructions":["Read each word aloud and ask the student to repeat.","Read the definition and example sentence.","Ask the check question to confirm understanding.","Ask the student to make their own sentence with one word."],"words":[
  {"word":"<key_points[0]>","emoji":"...","definition":"...","example":"...","check":"..."},
  {"word":"<key_points[1]>","emoji":"...","definition":"...","example":"...","check":"..."}
]}
TITLE LOCK: The "title" field MUST be exactly "Useful Language (Part 2)" — do NOT rename it.
TEACHER INSTRUCTIONS LOCK: The "teacher_instructions" field MUST always be present and MUST be a JSON array of strings (NOT a single string). Use exactly 4 steps as shown above.
NOTE: If key_points has 3 words, add a 3rd entry. If it has 4, add 4 entries. Match EXACTLY.
CCQ RULE: Each "check" question MUST be an A/B choice question or an open-ended Wh- question. NEVER use bare Yes/No questions. For A1/A2 levels, ALWAYS use A/B choice (e.g. "Which is spicier: a green salad or a curry?", "Do you eat this with a fork or a spoon?"). For B1+, use Wh- questions that require a full sentence. Good examples: "Which of these is a better example: A or B?", "What would you do if...?", "How would you use this word in a sentence about your own life?".

# conversation_builder
Generate conversation_builder slide JSON:
{"type":"conversation_builder","title":"Conversation Builder","goal":"...","linkers":[{"word":"...","use":"..."}],"model":"...","your_turn":{"teacher":"...","student":"..."}}

# practice
Generate practice slide JSON:
{"type":"practice","title":"Let's Practice","teacher_question":"...","student_guide":["...","...","..."]}
TEACHER QUESTION RULE: The "teacher_question" must set up a specific, concrete situation related to the topic. Give the student something real to respond to. Do NOT reference a "menu" or visual prop that doesn't exist in the slide — instead, list the available options directly in the question text. Example: "Imagine you are at the airport and your flight is delayed. I am the airline agent. Use the frames below to speak to me."
STUDENT GUIDE RULE: Each entry in "student_guide" MUST be a sentence frame with a blank (___) for the student to fill in with their own words — NOT a complete answer sentence. Example frames: "I usually _____ when I travel.", "The best thing about _____ is _____.", "I would say _____ because _____." Do NOT write complete model sentences.

# scenario
Generate scenario slide JSON:
{"type":"scenario","title":"Real-World Scenario","role_a":"...","role_b":"...","problem":"...","mission":["...","...","..."],"start":"..."}

# wrap_up
Generate wrap_up slide JSON:
{"type":"wrap_up","title":"Wrap-Up","recap":["vocab: <list ALL vocabulary words from this lesson>","chunk: <copy ALL functional language phrases from blueprint exactly, NOT a description of the task>","skill: ..."],"final_task":"...","challenge":"..."}
CRITICAL: The "vocab" recap item MUST list EVERY vocabulary word taught in this lesson (all words from useful_language_1 and useful_language_2 combined).
CRITICAL: The "chunk" recap item MUST be the actual spoken phrases taught (e.g. "I suggest we... / How about we..."), NOT a summary of what the student did in the scenario. Copy the phrases directly from the blueprint Functional Language field.
FINAL TASK RULE: The "final_task" field is a QUICK VERBAL SUMMARY — it must be completable in under 30 seconds. It is NOT a new role-play, debate, or extended activity. It should ask the student to say 1-2 sentences using today's vocabulary and chunks. Example: "In one sentence, tell me: what is the most useful phrase you learned today and when would you use it?" Do NOT assign a new scenario, debate, or task that requires more than 30 seconds to complete.
