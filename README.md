# Upaj - Crop Prediction Application

We are using Machine Learning and NLP for predicting the best Crops to be cultivated based on the land type, weather, Minimum Support Price. 
We are providing a chat interface for providing all the information.

### Main Features of Chat

- Predict the most profitable crop(s) for a specific location and season keeping into the account the land type, the weather conditions, etc.
- Provide the location wise current weather information.
- Predict location wise minimum support price for crops.
- Provide all the information of pesticides of a certain crop.
- Provide suggestions for the best practices of cultivation in form of videos,etc.
- Provide customer support information.

### Technology Stack
- Angular 6 (front-end)
- Django Rest Framework
- API's 
  - Google Speech To Text(multilingual voice support)
  - Google Translate API(multilingual voice support)
  - Open Weather Mapfor weather details
 
### Setup
1. Clone the Project.

2. Create a virtual environment for the project using the command:
```
virtualenv -p python3 upajj
```

3. Activate the environement using the command:
```
source upajj/bin/activate
```

4. Satisfy all the requirements by running the following command:
```
pip install -r requirements.txt
```
5. Migrate the Database using commands:
```
python manage.py makemigrations
python manage.py migrate
```
6. Run Django server
```
python manage.py runserver
```
7. Install npm and its dependencies

8. Start the front-end server using command:
```
ng serve
```
### Our Application
![webp net-resizeimage](https://user-images.githubusercontent.com/25306801/53689639-3113cc00-3d80-11e9-931f-121fff865aef.jpg)
![webp net-resizeimage 1](https://user-images.githubusercontent.com/25306801/53690463-e5b5e980-3d90-11e9-9e2f-76040ff50ac1.jpg)
