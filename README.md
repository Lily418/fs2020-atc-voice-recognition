# Flight Simulator 2020 Voice Recognition
This project allows the Air Traffic Control (ATC) component of Flight Simulator 2020 to be controlled using voice.

The steps to achieve this are:
1. When the user presses a push to talk button, a screenshot is taken of the ATC window. 
2. This is processed with optical character recgonition to create a list of possible commands
3. The user's speech is processed with a speech model which has been trained on a list of domain specific language
4. Possible commands are compared to the users speech, with the closest match being inputted into the flight simualtor.
