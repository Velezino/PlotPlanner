 # -*- coding: utf-8 -*-
from flask import Flask, app, render_template, request, session, redirect, url_for
import openai
import re

app = Flask(__name__)
openai.api_key = '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'
app.config["SECRET_KEY"] = "ADSFASDFASDFASDF34"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST' and 'genre' in request.form:
        genre = request.form['genre']
        character1 = request.form['character1']
        character2 = request.form['character2']
        storyline = request.form['storyline']

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "write an outline"},
                {"role": "user", "content": f"with a genre of {genre}"},
                {"role": "user", "content": f"character 1 name {character1}"},
                {"role": "user", "content": f"character 2 name {character2}"},
                {"role": "user", "content": f"with a storyline of: {storyline}"},
                {"role": "user", "content": "act as creative fiction writer; the outline needs to have 6 short sentences ideas that have a one word title; Each sentence will include the following (Sentence 1: Set the tone, type, initial palette of the story, the theme is set and introduce the main cahracters and their world and a event sets the story in motion; sentence 2: there is a question or dilemma in the story, the main character makes a choice, and a subplot is introduced that support the main plot; sentence 3:the heart of the story, the world is explored, to a point wher the stake are raised with serious decisions; sentence 4:the tension increases with events, lie a 'symbolic death'; sentence 5: the story hits rock bottom within the context and a solution or resolution needs to be done;5:there is a new idea, understanding or revelation that affect the main conflict; sentence 6: climax and the resolution that shows how the world has changed. BE CONCISE AND BE SPECIFIC; SURPRISE THE USER WITH PLOT TWISTS; MAINTAIN THE GENRE; REMEMBER THAT ALL THE OUTLINES ARE CONNECTED; if you change one outline, the others have to be updated;. THEY HAVE TO FOLLOW THE SAME STORYLINE, there is a linear storyline; i want this format: bulletpoint: Title bullet (next paragraph; all the other text)"}
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        answer = response["choices"][0]["message"]["content"]
        
        # Split the response into parts using regular expression
        outline_parts = re.split(r'\d+\.\s+', answer)[1:]  # Splitting the outline into parts

        if len(outline_parts) != 6:
            return "Error: The outline was not split into 6 parts as expected.", 400

        session['outline_parts'] = outline_parts

        return redirect(url_for('outline'))

    return render_template('index.html')

@app.route('/outline', methods=['GET', 'POST'])
def outline():
    if request.method == 'POST':
        # Check if we're modifying a part of the outline
        if 'sentence' in request.form and 'modsentence' in request.form:
            sentence_number = int(request.form["sentence"]) - 1
            modsentence = request.form['modsentence']

            outline_parts = session.get('outline_parts', [])
            if 0 <= sentence_number < len(outline_parts):
                outline_parts[sentence_number] = modsentence
                session['outline_parts'] = outline_parts

    return render_template('outline.html', outline_parts=session.get('outline_parts', []))

@app.route('/ai_modify', methods=['POST'])
def ai_modify():
    if 'sentence' in request.form and 'modsentence' in request.form:
        sentence_number = int(request.form["sentence"]) - 1
        modsentence = request.form['modsentence']

        outline_parts = session.get('outline_parts', [])
        if 0 <= sentence_number < len(outline_parts):
            # Retrieve the current outline part to be modified
            current_part = outline_parts[sentence_number]

            # Construct the prompt for OpenAI, including the unchanged parts
            prompt = "Here is the current outline:\n"
            for i, part in enumerate(outline_parts):
                prompt += f"{i+1}. {part}\n"
            prompt += f"\nModify part {sentence_number+1} apply storytelling techniques; with more details, cahnges in plot but the same genre and characters; with the same setting; don't be generic;remember the genre.' {modsentence}, but keep the rest of the story the same"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            # Extract the modified part from the response
            modified_response = response.choices[0].message["content"].strip()
            
            # Split the response to get the updated part
            updated_parts = re.split(r'\d+\.\s+', modified_response)[1:]

            # Update only the specific part of the outline
            if len(updated_parts) > sentence_number:
                outline_parts[sentence_number] = updated_parts[sentence_number]
                session['outline_parts'] = outline_parts

    return redirect(url_for('outline'))


        


@app.route('/reset', methods=['POST'])
def reset():
    session.pop('outline_parts', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
