# Doctorly API

Obtaining an appointment with a doctor for a checkup is commonly observed to be time-consuming and demanding. Usually, there are already booked slots and long waiting lists, so going to the hospital goes in vain, especially in post-Covid time.

I devised a solution to these issues. Utilizing this backend system, any client application, be it web-based or mobile can be made that provides the solution to the above issues. 

#### Home Page
![Api Home Page](/assets/doctorly_home.png)

#### Register 
![Api Register Page](/assets/doctorly_register.png)

#### Sign in
![Api Auth Page](/assets/doctorly_auth.png)

#### Slots
![Api Slots Page](/assets/doctorly_slots.png)

#### Redis Cached data 
![Api cache](/assets/doctorly_cache.png)

## How it works

Let's first understand the application architecture
1. Client will request the data from the REST API.
2. The API will first check the requested data in Redis Cache
3. If a cache hit occurs, it will directly return the data to the client.
4. If the API did not find the requested data in Redis Cache, then it will issue the query to the relational database. Upon the completion of the query, the data will be written back to the cache and then will be returned to the client.

![Application Architecture](/assets/doctorly%20architecture.drawio.png)

### How the data is stored:

#### Primary Database
I have used relational database to store all the data. To better understand the relationships between different tables, take a look at the ER diagram.

![ER Diagram](/assets/doctorly_er.png)

#### Redis As Cache
All the cached response will be saved in the form of key value pairs.
```
{

  "id": 1,
  "name": "testuser",
  "email": "testuser@example.com",
  "password": "testing123",
  "registered_at": "2019-08-24T14:15:22Z",
  "confirmed": true,
  "role": "user"
}
```

#### Redis JSON And RediSearch
- Search functionality is provided through the rediSearch.
- Client applications can search the doctors by their name, qualification and specialization. 
- In Redis JSON only the doctor related data is stored.
- The data in Redis JSON is kept in sync with the relational database to avoid providing inaccurate results.  
- Example JSON data
```
{
  "id": 1,
  "user": {
    "id": 2,
    "name": "doctor2",
    "email": "doctor2@email.com",
    "registered_at": "2022-08-24T13:47:29.234907",
    "confirmed": false,
    "role": "user"
  },
  "description": "Hello I am a doctor",
  "image": "http://localhost:5000/static/doctor_profile_pics/default_doctor_image.jpg",
  "experience": 3,
  "rating": 4.7,
  "no_of_patients": 0,
  "specializations": {
	"id": 1
	"name": "allergist"
	},
  "qualifications": {
    "qualification_name": [
      "mbbs"
    ],
    "procurement_year": [
      "2019-08-24"
    ],
    "institute_name": [
      "Dow University of Health and Sciences",
    ]
  },
  "slot": [
        "id": 14,
        "day": "monday",
        "start": "10:30",
        "end": "12:30",
        "consultation_fee": 1,
        "appointment_duration": 10,
        "num_slots": 10
      ]
}
```

### How the data is accessed:
- Auth Endpoints
    - `/auth/get_token` ~ Get the authentication token
    - `/auth/logout` ~ Logout the user

- User Endpoints
    - `/users/register` ~ Registers a new user
    - `/users/info` ~ Get the info of currently authenticated user

- Doctor Endpoints
    - `/doctors/new` ~ Registers a new doctor
    - `/doctors/all` ~ Returns all the doctors
    - `/doctors/info` ~ Get the info of currently authenticated doctor
    - `/doctors/image` ~ Update the profile picture
    - `/doctors/add_slot` ~ Create your available slot
    - `/doctors/patients` ~ Get all of your patients
    - `/doctors/get/{id}` ~ Get doctor by id
    - `/doctors/slot/{id}` ~ Get doctor slots by id
    - `/doctors/popular/doctors` ~ Get popular doctors
    - `/doctors/timings/{id}` ~ Get doctors next sitting date by id
    - `/doctors/patients/{id}` ~ Get all the patients of the doctor by appointment id
    - `/doctors/add_qualifications` ~ Add qualifications
    - `/doctors/add_specializations` ~ Add specialization

- Patient Endpoints
    - `/patient/new` ~ Registers a new patient
    - `/patient/all` ~ Returns all of your patients
    - `/patient/get/{id}` ~ Get patient by id
    - `/patient/new_appointment` ~ Create new appointment
    - `/patient/appointment/history ~ Appointment History

- Misc Endpoints
    - `/misc/qualifications` ~ Returns all qualifications
    - `/misc/specializations` ~ Returns all specialization
    - `/misc/doctors/day/{day}` ~ Search doctors available on a particular day
    - `/misc/doctors/{name}` ~ Search doctors by name
    - `/misc/doctors/specialization/{name}` ~ Search doctors by specialization
    - `/misc/doctors/qualification/{name}` ~ Search doctors by qualification
    - `/misc/image/{specialization_id}` ~ Upload specialization image

### Performance Benchmarks

[If you migrated an existing app to use Redis, please put performance benchmarks here to show the performance improvements.]

## How to run it locally?

### Prerequisites

- Python >= 3.10
- Pip >=  22.0.2
- Docker >= 20.10

### Local installation
Install the latest version of python3 and Docker.Only then proceeds with the below steps.

- Clone the repository
```
git clone https://github.com/zain2323/docterlyapi.git
```
- Navigate to the project directory
```
cd docterlyapi
```
- Pull images of Postgres and Redis Stack
```
docker pull postgres
docker pull redis/redis-stack-server:latest
```
- Build the image of the API
```
docker build -t doctorly:latest .
```
- Start all the containers using Docker Compose
```
docker compose -f docker-compose.yaml up
```
- To stop all the containers
```
docker compose down
```
- Navigate to `localhost:5000/` to test endpoints with the builtin test environment or use any of your favourite Api testing tool.

## Deployment

To make deploys work, you need to create free account on [Redis Cloud](https://redis.info/try-free-dev-to)

### Google Cloud Run

[Insert Run on Google button](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-button-click-to-deploy-your-git-repos-to-google-cloud)

### Heroku

[Insert Deploy on Heroku button](https://devcenter.heroku.com/articles/heroku-button)

### Netlify

[Insert Deploy on Netlify button](https://www.netlify.com/blog/2016/11/29/introducing-the-deploy-to-netlify-button/)

### Vercel

[Insert Deploy on Vercel button](https://vercel.com/docs/deploy-button)
